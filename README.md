# Windows Registry Tweaks

A polished desktop GUI application for managing Windows Registry tweaks, created as a university project.

## Project
- Project Title: Windows Registry
- Student Name: Mohadeseh Abbasi
- Professor Name: Mojtaba Mansouri
- Application Title: Windows Registry Tweaks

## Features
- 20 individual Registry tweak cards
- Modern dark themed UI using CustomTkinter
- Search and filtering
- Dynamic status detection
- Enable / Disable controls for each value
- Registry backup creation
- Warning dialogs before applying changes
- Permission handling for admin-only tweaks
- Safe error handling without crashing

## Requirements
- Windows 10 or Windows 11
- Python 3.10+
- Administrator privileges recommended for HKLM changes

## Install
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run
```powershell
python app.py
```

## Notes
- The application modifies the Windows Registry and should be used carefully.
- A backup is created through the app before or during modification. You can also create one manually from the UI.
- Some tweaks may require Explorer restart or log-off to take effect.
- `HKEY_LOCAL_MACHINE` operations require administrator access.
