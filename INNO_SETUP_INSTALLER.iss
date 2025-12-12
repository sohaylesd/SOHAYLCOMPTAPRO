; Inno Setup Script (optional) - to create installer
[Setup]
AppName=ComptaSouhail
AppVersion=1.0
DefaultDirName={pf}\ComptaSouhail
DefaultGroupName=ComptaSouhail
OutputBaseFilename=ComptaSouhail_Installer
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "compta.db"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ComptaSouhail"; Filename: "{app}\main.exe"
