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
- **v8.0**: Added real-time monitoring with `--watch` mode.
- **v9.0**: Added desktop notifications and maintenance (auto-deletion of old files).
- **v10.0**: Added `--undo` functionality using the log file.
- **v11.0**: Added `start_organizer.bat` and desktop shortcut for easy background execution.

## Usage
### One-click Start
Double-click the **Start Downloads Organizer** shortcut on your desktop to start the background monitor in a minimized window.
Run the script to organize your Downloads:
```bash
python organize_downloads.py
```

To see what would happen without making any changes:
```bash
python organize_downloads.py --dry-run
```

To keep the script running in the background and organize files as they arrive:
```bash
python organize_downloads.py --watch
```

To reverse the last organization session:
```bash
python organize_downloads.py --undo
```
