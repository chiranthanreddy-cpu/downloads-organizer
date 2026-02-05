import os
import shutil
import argparse
from pathlib import Path

# Define the source directory (Downloads)
DOWNLOADS_PATH = Path.home() / "Downloads"

# Define file categories and their associated extensions
FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".csv", ".xlsx", ".pptx"],
    "Installers": [".exe", ".msi", ".dmg", ".pkg"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv"],
    "Music": [".mp3", ".wav", ".aac", ".flac"],
}

def get_category(file_extension):
    for category, extensions in FILE_CATEGORIES.items():
        if file_extension.lower() in extensions:
            return category
    return "Others"

def main():
    parser = argparse.ArgumentParser(description="Organize your Downloads folder.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be moved without actually moving files.")
    args = parser.parse_args()

    if args.dry_run:
        print("--- DRY RUN MODE (No files will be moved) ---\n")

    print(f"Organizing: {DOWNLOADS_PATH}")
    if not DOWNLOADS_PATH.exists():
        print("Downloads folder not found.")
        return

    moved_count = 0

    for item in DOWNLOADS_PATH.iterdir():
        if item.is_dir() or item.name == "organize_downloads.py":
            continue

        category = get_category(item.suffix)
        target_dir = DOWNLOADS_PATH / category

        # Handle name collisions
        destination = target_dir / item.name
        if destination.exists():
            print(f"Skipping {item.name}: File already exists in {category}")
            continue

        if args.dry_run:
            print(f"[WOULD MOVE]: {item.name} -> {category}/")
            moved_count += 1
        else:
            # Create the category folder if it doesn't exist
            if not target_dir.exists():
                target_dir.mkdir()

            try:
                shutil.move(str(item), str(destination))
                print(f"Moved: {item.name} -> {category}/")
                moved_count += 1
            except Exception as e:
                print(f"Error moving {item.name}: {e}")

    status = "Would move" if args.dry_run else "Moved"
    print(f"\nTask complete. {status} {moved_count} files.")

if __name__ == "__main__":
    main()
