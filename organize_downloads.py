import os
import shutil
import argparse
import json
import hashlib
import logging
import time
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define paths
DOWNLOADS_PATH = Path.home() / "Downloads"
PROJECT_ROOT = Path(__file__).parent
CONFIG_FILE = PROJECT_ROOT / "config.json"
LOG_FILE = PROJECT_ROOT / "organizer.log"

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def cleanup_empty_folders(path):
    """Recursively remove empty folders."""
    for root, dirs, files in os.walk(path, topdown=False):
        for name in dirs:
            dir_path = Path(root) / name
            try:
                if not any(dir_path.iterdir()):
                    if not args.dry_run:
                        dir_path.rmdir()
                        print(f"Removed empty folder: {dir_path.relative_to(path)}")
                    else:
                        print(f"[WOULD REMOVE EMPTY]: {dir_path.relative_to(path)}")
            except Exception as e:
                print(f"Error removing {dir_path}: {e}")

def get_file_hash(file_path):
    """Calculate SHA-256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        print(f"Error hashing {file_path}: {e}")
        return None

def is_duplicate(source_path, target_dir):
    """Check if file already exists in target directory with same content."""
    if not target_dir.exists():
        return False
    
    source_hash = get_file_hash(source_path)
    if not source_hash:
        return False

    for existing_file in target_dir.iterdir():
        if existing_file.is_file() and existing_file.name == source_path.name:
            existing_hash = get_file_hash(existing_file)
            return source_hash == existing_hash
    return False

def load_config():
    default_config = {
        "categories": {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
            "Documents": [".pdf", ".doc", ".docx", ".txt", ".csv", ".xlsx", ".pptx"],
            "Installers": [".exe", ".msi", ".dmg", ".pkg"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
            "Videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv"],
            "Music": [".mp3", ".wav", ".aac", ".flac"],
        },
        "settings": {"organize_by_date": False, "delete_duplicates": False}
    }
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config.json: {e}. Using defaults.")
    
    return default_config

def get_category(file_extension, categories):
    for category, extensions in categories.items():
        if file_extension.lower() in extensions:
            return category
    return "Others"

class DownloadHandler(FileSystemEventHandler):
    def __init__(self, categories, config):
        self.categories = categories
        self.config = config

    def on_created(self, event):
        if not event.is_directory:
            # Wait a moment for the download to finish/file to be stable
            time.sleep(1)
            organize_file(Path(event.src_path), self.categories, self.config)

    def on_moved(self, event):
        if not event.is_directory:
            organize_file(Path(event.dest_path), self.categories, self.config)

def organize_file(item, categories, config):
    if item.is_dir() or item.name in ["organize_downloads.py", "config.json", "organizer.log"]:
        return

    category = get_category(item.suffix, categories)
    target_dir = DOWNLOADS_PATH / category

    if config.get("settings", {}).get("organize_by_date", False):
        mtime = datetime.fromtimestamp(item.stat().st_mtime)
        year = str(mtime.year)
        month = mtime.strftime("%B")
        target_dir = target_dir / year / month

    destination = target_dir / item.name

    if is_duplicate(item, target_dir):
        if config.get("settings", {}).get("delete_duplicates", False):
            item.unlink()
            print(f"Deleted duplicate: {item.name}")
            logging.info(f"Deleted duplicate: {item.name}")
            return
        else:
            print(f"Skipping duplicate: {item.name}")
            return

    if destination.exists():
        print(f"Skipping {item.name}: File with same name exists in {category} but content differs.")
        return

    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)

    try:
        shutil.move(str(item), str(destination))
        print(f"Moved: {item.name} -> {target_dir.relative_to(DOWNLOADS_PATH)}/")
        logging.info(f"Moved: {item.name} to {target_dir}")
    except Exception as e:
        print(f"Error moving {item.name}: {e}")
        logging.error(f"Error moving {item.name}: {e}")

def main():
    global args
    parser = argparse.ArgumentParser(description="Organize your Downloads folder.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be moved without actually moving files.")
    parser.add_argument("--watch", action="store_true", help="Watch the folder in real-time.")
    args = parser.parse_args()

    config = load_config()
    categories = config.get("categories", {})

    if args.watch:
        print(f"Monitoring: {DOWNLOADS_PATH}")
        logging.info("Started real-time monitoring.")
        event_handler = DownloadHandler(categories, config)
        observer = Observer()
        observer.schedule(event_handler, str(DOWNLOADS_PATH), recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
        return

    if args.dry_run:
        print("--- DRY RUN MODE (No files will be moved) ---\n")
        logging.info("Started dry run organization.")
    else:
        logging.info("Started organization task.")

    print(f"Organizing: {DOWNLOADS_PATH}")
    if not DOWNLOADS_PATH.exists():
        print("Downloads folder not found.")
        logging.error("Downloads folder not found.")
        return

    moved_count = 0
    # Initial scan
    for item in DOWNLOADS_PATH.iterdir():
        if item.is_file():
            if not args.dry_run:
                organize_file(item, categories, config)
                moved_count += 1
            else:
                # Dry run logic simplified for the scan
                category = get_category(item.suffix, categories)
                print(f"[WOULD MOVE]: {item.name} -> {category}/")
                moved_count += 1

    # Cleanup empty folders
    cleanup_empty_folders(DOWNLOADS_PATH)

    status = "Would move" if args.dry_run else "Moved"
    print(f"\nTask complete. {status} {moved_count} files. Duplicates handled: {duplicates_found}")
    logging.info(f"Task complete. {status} {moved_count} files. Duplicates: {duplicates_found}")

if __name__ == "__main__":
    main()
