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
from plyer import notification

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

def send_notification(title, message):
    """Send a desktop notification."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Downloads Organizer",
            timeout=5
        )
    except Exception as e:
        print(f"Error sending notification: {e}")

def delete_old_files(days):
    """Delete files older than the specified number of days."""
    if days <= 0:
        return
    
    now = time.time()
    cutoff = now - (days * 86400)
    deleted_count = 0

    print(f"Checking for files older than {days} days...")
    for root, dirs, files in os.walk(DOWNLOADS_PATH):
        for name in files:
            file_path = Path(root) / name
            if file_path.stat().st_mtime < cutoff:
                try:
                    if not args.dry_run:
                        file_path.unlink()
                        logging.info(f"Auto-deleted old file: {file_path}")
                        deleted_count += 1
                    else:
                        print(f"[WOULD AUTO-DELETE]: {file_path}")
                except Exception as e:
                    print(f"Error deleting old file {file_path}: {e}")
    
    if deleted_count > 0:
        print(f"Auto-deleted {deleted_count} old files.")
        send_notification("Maintenance Complete", f"Auto-deleted {deleted_count} old files.")

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
        msg = f"Moved: {item.name} -> {target_dir.relative_to(DOWNLOADS_PATH)}/"
        print(msg)
        logging.info(msg)
        if config.get("settings", {}).get("enable_notifications", True):
            send_notification("File Organized", f"{item.name} moved to {category}")
    except Exception as e:
        print(f"Error moving {item.name}: {e}")
        logging.error(f"Error moving {item.name}: {e}")

def undo_last_session():
    """Reverse the moves made in the last session recorded in the log."""
    if not LOG_FILE.exists():
        print("No log file found. Nothing to undo.")
        return

    moves = []
    # We want to find the last block of moves
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
        
    # Find the start of the last session
    session_start_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        if "Started organization task" in lines[i]:
            session_start_idx = i
            break
    
    if session_start_idx == -1:
        print("No recent organization session found to undo.")
        return

    # Extract moves from that session
    for i in range(session_start_idx, len(lines)):
        if "Moved:" in lines[i]:
            # Format: 2026-02-05 14:55:00 - INFO - Moved: file.txt to C:\Users\...\Documents
            parts = lines[i].split("Moved: ")
            if len(parts) > 1:
                move_info = parts[1].split(" to ")
                filename = move_info[0].strip()
                target_path = Path(move_info[1].strip()) / filename
                moves.append((target_path, DOWNLOADS_PATH / filename))

    if not moves:
        print("No moves found in the last session.")
        return

    print(f"Undoing {len(moves)} moves...")
    undone_count = 0
    for src, dest in reversed(moves):
        if src.exists():
            try:
                if not args.dry_run:
                    shutil.move(str(src), str(dest))
                    print(f"Restored: {dest.name}")
                    undone_count += 1
                else:
                    print(f"[WOULD RESTORE]: {dest.name}")
            except Exception as e:
                print(f"Error restoring {src}: {e}")
        else:
            print(f"Could not find {src} to restore.")

    if not args.dry_run:
        logging.info(f"Undo completed. Restored {undone_count} files.")
        print(f"\nUndo complete. Restored {undone_count} files.")

def main():
    global args
    parser = argparse.ArgumentParser(description="Organize your Downloads folder.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be moved without actually moving files.")
    parser.add_argument("--watch", action="store_true", help="Watch the folder in real-time.")
    parser.add_argument("--undo", action="store_true", help="Undo the last organization session.")
    args = parser.parse_args()

    if args.undo:
        undo_last_session()
        return

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

    # Auto-delete old files
    delete_old_files(config.get("settings", {}).get("auto_delete_days", 0))

    # Cleanup empty folders
    cleanup_empty_folders(DOWNLOADS_PATH)

    status = "Would move" if args.dry_run else "Moved"
    print(f"\nTask complete. {status} {moved_count} files. Duplicates handled: {duplicates_found}")
    logging.info(f"Task complete. {status} {moved_count} files. Duplicates: {duplicates_found}")

if __name__ == "__main__":
    main()
