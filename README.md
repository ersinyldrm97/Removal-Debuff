# Removal Debuff

**Removal Debuff** is a small Python tool for working with Knight Online debuff removal logic and packaging it as a standalone executable.

## Project Structure

- `removal_debuff.py` — Main Python script.
- `removal_debuff.spec` — PyInstaller spec file for building the standalone executable.
- `build/` — PyInstaller build artifacts.
- `dist/` — Generated executable and related files.
- `images/` — Image assets used by the application.

## Requirements

- Python 3.10+ (or a compatible Python 3.x version)
- `pyinstaller`

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install PyInstaller:

```powershell
pip install pyinstaller
```

## Build to EXE

There are two common ways to create the executable:

### Option 1: Use the existing spec file

```powershell
python -m PyInstaller --noconsole --onefile removal_debuff.py
```

### Option 2: Build directly from the script

```powershell
pyinstaller --onefile --windowed removal_debuff.py
```

After the build finishes, the executable will be available in the `dist/` directory.

## Usage

Run the script directly with Python or execute the generated EXE from `dist/`:

```powershell
python removal_debuff.py
```

or

```powershell
dist\removal_debuff.exe
```

## Notes

- If you want a console window during execution, omit `--windowed`.
- Update `removal_debuff.spec` if you need to bundle additional data files or assets.

## Contributing

If you make improvements or fixes, add them to a new branch and submit a pull request.

## License

Specify your license here, if applicable.
