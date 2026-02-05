# Downloads Organizer
An automated Python script to categorize and organize files in the Downloads folder.

## Versions
- **v1.0**: Initial setup and basic file detection logic.
- **v2.0**: Core organization logic, folder creation, and collision handling.
- **v3.0**: Added dry-run mode and argument parsing.
- **v4.0**: Externalized configuration to `config.json`.
- **v5.0**: Added SHA-256 hash-based duplicate detection.
- **v6.0**: Added optional date-based subfolder organization (Year/Month).
- **v7.0**: Added logging and automatic empty folder cleanup.

## Usage
Run the script to organize your Downloads:
```bash
python organize_downloads.py
```

To see what would happen without making any changes:
```bash
python organize_downloads.py --dry-run
```
