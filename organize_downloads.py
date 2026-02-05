import os
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

def main():
    print(f"Scanning: {DOWNLOADS_PATH}")
    if not DOWNLOADS_PATH.exists():
        print("Downloads folder not found.")
        return

    for item in DOWNLOADS_PATH.iterdir():
        if item.is_file():
            print(f"Found file: {item.name}")

if __name__ == "__main__":
    main()
