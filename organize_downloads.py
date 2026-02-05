import os
import shutil
import argparse
import json
import hashlib
from datetime import datetime
from pathlib import Path

# Define the source directory (Downloads)
DOWNLOADS_PATH = Path.home() / "Downloads"
CONFIG_FILE = Path(__file__).parent / "config.json"

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

def main():
    parser = argparse.ArgumentParser(description="Organize your Downloads folder.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be moved without actually moving files.")
    args = parser.parse_args()

    config = load_config()
    categories = config.get("categories", {})

    if args.dry_run:
        print("--- DRY RUN MODE (No files will be moved) ---\n")

    print(f"Organizing: {DOWNLOADS_PATH}")
    if not DOWNLOADS_PATH.exists():
        print("Downloads folder not found.")
        return

    moved_count = 0
    duplicates_found = 0

    for item in DOWNLOADS_PATH.iterdir():
        if item.is_dir() or item.name in ["organize_downloads.py", "config.json"]:
            continue

        category = get_category(item.suffix, categories)
        target_dir = DOWNLOADS_PATH / category

        # Add date subfolders if enabled
        if config.get("settings", {}).get("organize_by_date", False):
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            year = str(mtime.year)
            month = mtime.strftime("%B")
            target_dir = target_dir / year / month

        destination = target_dir / item.name

        # Check for duplicates
        if is_duplicate(item, target_dir):
            duplicates_found += 1
            if config.get("settings", {}).get("delete_duplicates", False):
                if args.dry_run:
                    print(f"[WOULD DELETE DUPLICATE]: {item.name}")
                else:
                    item.unlink()
                    print(f"Deleted duplicate: {item.name}")
                continue
            else:
                print(f"Skipping duplicate: {item.name}")
                continue

        # Handle name collisions (different content, same name)
        if destination.exists():
            print(f"Skipping {item.name}: File with same name exists in {category} but content differs.")
            continue

        if args.dry_run:
            print(f"[WOULD MOVE]: {item.name} -> {category}/")
            moved_count += 1
        else:
            if not target_dir.exists():
                target_dir.mkdir(parents=True, exist_ok=True)

            try:
                shutil.move(str(item), str(destination))
                print(f"Moved: {item.name} -> {category}/")
                moved_count += 1
            except Exception as e:
                print(f"Error moving {item.name}: {e}")

    status = "Would move" if args.dry_run else "Moved"
    print(f"\nTask complete. {status} {moved_count} files. Duplicates handled: {duplicates_found}")

if __name__ == "__main__":
    main()
