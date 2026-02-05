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
### One-time organization
Run the script to organize your Downloads:
```bash
python organize_downloads.py
```

### Dry Run
To see what would happen without making any changes:
```bash
python organize_downloads.py --dry-run
```

### Weekly Auto-Scheduling (Background Mode)
To automatically organize your downloads every Sunday at 10:00 AM without any terminal windows popping up:

1. **Open PowerShell as Administrator** (Right-click Start > Terminal (Admin) or PowerShell (Admin)).
2. Navigate to this folder:
   ```powershell
   cd "C:\Users\chiru\downloads-organizer"
   ```
3. Run the setup script:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; ./schedule_downloads.ps1
   ```

*Note: The script uses `pythonw.exe` for the scheduled task, meaning it will work silently in the background.*

### Real-time Monitoring
To keep the script running in the background and organize files as they arrive:
```bash
python organize_downloads.py --watch
```

### Undo Last Session
To reverse the last organization session:
```bash
python organize_downloads.py --undo
```
