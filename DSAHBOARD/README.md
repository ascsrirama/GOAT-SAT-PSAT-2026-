## GOAT-SAT Dashboard

This repository contains a small dashboard for visualizing FAKE ESP (GPS/telemetry) data. There are two dashboard variants in the repo:

- `dashboard#3.py` — Kivy-based dashboard (primary/current).
- `dashboard#2.py` and `tempCodeRunnerFile.py` — older / alternate Tkinter-based examples and helper scripts.

This README explains how to prepare the project for checkin, install dependencies, run the app locally on Windows (PowerShell), and best-practices before committing.

## Quick summary / contract

- Input: Python 3.8+ runtime on Windows (tested with CPython + tkinter available).
- Output: A runnable Kivy dashboard app window (or Tkinter alternative) that simulates telemetry.
- Success criteria: Virtual environment created, dependencies installed, files renamed if necessary, app runs without syntax errors.

## Prerequisites

- Python 3.8 or newer. We recommend the latest stable Python 3.10+ or 3.11.
- PowerShell (Windows) — these commands are for PowerShell.

Note: `tkinter` is included with most official Python Windows installers. Kivy and some garden packages are installed via pip.

## Setup (recommended)

1. Open PowerShell in the project folder (`c:\GOAT-SAT-PSAT-2026-\DSAHBOARD`).
2. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
; .\.venv\Scripts\Activate.ps1
```

3. Install dependencies from `requirements.txt` (created below):

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If any garden package fails to install, see the notes in the Troubleshooting section below.

## Dependencies (minimal)

We detected these Python packages used in the source files. Add or adjust as needed:

- kivy
- kivy-garden
- kivy-garden.mapview
- kivy-garden.matplotlib
- matplotlib
- pyserial
- customtkinter
- tkintermapview

These are listed in `requirements.txt`. If you depend only on the Kivy dashboard, you may not need `customtkinter` / `tkintermapview`.

## Running the dashboard

Important: some filenames contain a `#` character (for example `dashboard#3.py`) which can be awkward for shell quoting and for git. It's best to rename those files before a checkin (see "Preparing files for checkin").

To run the Kivy dashboard (after renaming to `dashboard_3.py`):

```powershell
# run in the activated virtualenv
python dashboard_3.py
```

If you prefer to run the file without renaming, you can run it with quotes but renaming is recommended:

```powershell
python "dashboard#3.py"
```

To run the Tkinter sample (older alternate):

```powershell
python dashboard#2.py
# or
python tempCodeRunnerFile.py
```

## Preparing files for checkin (recommended steps)

1. Remove or move throwaway files:
   - `tempCodeRunnerFile.py` is typically a scratch file — either delete it or move it to a `scripts/` folder.
2. Rename files that contain `#` to safer names. Example renames we recommend:

```powershell
git mv "dashboard#3.py" dashboard_3.py
git mv "dashboard#2.py" dashboard_2.py
```

3. Add/verify `.gitignore` (we include one here). It excludes caches, the virtual environment folder `.venv`, and files with `#`.
4. Generate a pinned `requirements.txt` from your environment (optional, but recommended before publishing):

```powershell
python -m pip freeze > requirements.txt
```

5. Run formatters/linters (optional but recommended):

```powershell
pip install black ruff
black .
ruff check .
```

6. Run the app locally to verify everything works before committing.

7. Commit with a clear message, for example:

```powershell
git add .
git commit -m "chore: prepare dashboard for repo — rename files, add README and .gitignore"
git push
```

## .gitignore and recommended cleanup

This repo includes a `.gitignore` that prevents committing caches, the `.venv` folder, and temporary files. It also ignores any file with a `#` in its name so you don't accidentally add scratch versions.

If you intend to keep files with `#` in their names, edit or remove that ignore rule first.

## Troubleshooting

- Kivy installation on Windows can be tricky. If `pip install kivy` fails, follow the official Kivy Windows installation guide: https://kivy.org/doc/stable/gettingstarted/installation.html#windows
- Garden packages sometimes require `pip install kivy-garden` then `garden install mapview` (older instructions). Try `python -m pip install kivy_garden` or `pip install kivy-garden.mapview` depending on errors.
- If you see missing GUI backend errors for matplotlib, ensure you have a working wheel of matplotlib installed for your Python version: `python -m pip install --upgrade matplotlib`

## What I changed / added

- Added `README.md` — this file, with setup and checkin instructions.
- Added `requirements.txt` — minimal dependency list detected from sources.
- Added `.gitignore` — ignores caches, `.venv`, and temporary scratch files.

## Next steps (optional)

- I can rename `dashboard#3.py` to `dashboard_3.py` and update imports/usages if you want me to do that automatically.
- Add small run/test script or a short unit test to validate the app imports successfully in CI.

If you'd like me to also perform the rename and run a quick import test inside a virtualenv, say "please rename and run tests" and I'll proceed.

---
Happy to update the README further or make the rename changes for you.
