ComptaSouhail - Prototype Windows (source + build script)
===========================================================

Contenu du package:
- db_init.py
- main.py
- edi_generator.py
- requirements.txt
- build_exe.ps1   (PowerShell script to create a Windows .exe using PyInstaller)
- INNO_SETUP_INSTALLER.iss (optional Inno Setup script to create an installer)
- README.txt (this file)

But IMPORTANT: I cannot produce a Windows .exe from this environment. Instead I prepared this package so you can create the .exe easily on your Windows PC.

Step-by-step to produce the .exe on your Windows machine (recommended):
1) Install Python 3.8+ for Windows from https://www.python.org/downloads/windows/ (choose the installer matching your system).
2) Open PowerShell as Administrator in this folder (right-click -> Open PowerShell window here).
3) (Optional) Create a virtual environment:
   python -m venv venv
   .\\venv\\Scripts\\Activate.ps1
4) Install dependencies:
   pip install -r requirements.txt
   pip install pyinstaller
5) Run the build script (PowerShell):
   .\\build_exe.ps1
   This runs PyInstaller and produces dist\\main.exe and optional installer files.
6) After build, you will find an executable in the 'dist' folder and the database 'compta.db' must be copied next to the exe.

If you prefer I can also:
- Provide a GitHub Actions workflow you can paste into your repo to produce a ready downloadable .exe artifact automatically on each commit.
- Walk you step-by-step in PowerShell (I can paste commands).

If you want the team to build the exe for you, you'll need to upload the folder to a file-sharing link or give me permission to build via GitHub Actions (I can give you the workflow).

PowerShell build script (build_exe.ps1) will be included in the zip.
