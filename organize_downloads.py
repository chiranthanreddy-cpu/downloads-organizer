import os
import shutil
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
    print(f"Organizing: {DOWNLOADS_PATH}")
    if not DOWNLOADS_PATH.exists():
        print("Downloads folder not found.")
        return

    moved_count = 0

    for item in DOWNLOADS_PATH.iterdir():
        # Skip directories and the script itself if it were in the same folder
        if item.is_dir() or item.name == "organize_downloads.py":
            continue

        category = get_category(item.suffix)
        target_dir = DOWNLOADS_PATH / category

        # Create the category folder if it doesn't exist
        if not target_dir.exists():
            target_dir.mkdir()

        # Handle name collisions
        destination = target_dir / item.name
        if destination.exists():
            print(f"Skipping {item.name}: File already exists in {category}")
            continue

        try:
            shutil.move(str(item), str(destination))
            print(f"Moved: {item.name} -> {category}/")
            moved_count += 1
        except Exception as e:
            print(f"Error moving {item.name}: {e}")

    print(f"\nTask complete. Moved {moved_count} files.")

if __name__ == "__main__":
    main()
