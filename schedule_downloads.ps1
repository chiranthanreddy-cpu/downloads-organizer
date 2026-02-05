# Downloads Organizer - Task Scheduler Setup
$ScriptName = "organize_downloads.py"
$CurrentDir = "C:\Users\chiru\downloads-organizer"
$PythonPath = (Get-Command python).Source
$TaskName = "WeeklyDownloadsOrganizer"
$ActionExecutable = $PythonPath
$ActionArguments = "`"$CurrentDir\$ScriptName`""

# Create the action
$Action = New-ScheduledTaskAction -Execute $ActionExecutable -Argument $ActionArguments

# Create the trigger (Weekly on Sunday at 10:00 AM)
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 10:00am

# Create the settings (Only run on AC power)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries:$false -DontStopIfGoingOnBatteries:$false

# Register the task
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Automated weekly organization of the Downloads folder." -Force

Write-Host "Task '$TaskName' has been scheduled successfully!" -ForegroundColor Green
Write-Host "It will run every Sunday at 10:00 AM."
