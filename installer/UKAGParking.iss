; Compiler avec Inno Setup 6, apres scripts/build_windows.ps1.
[Setup]
AppId={{A6849886-5E90-436B-B8C3-E9E8771088F5}
AppName=UKAG Parking
AppVersion=1.0.1
AppPublisher=Universite Kofi Annan de Guinee
DefaultDirName={localappdata}\Programs\UKAG Parking
DefaultGroupName=UKAG Parking
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.17763
UninstallDisplayIcon={app}\UKAGParking.exe
SetupIconFile=..\build\ukag.ico
OutputDir=..\dist\installer
OutputBaseFilename=UKAGParking-Setup-1.0.1-x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Creer un raccourci sur le bureau"; Flags: unchecked

[Files]
Source: "..\dist\UKAGParking\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "INSTALLATION-WINDOWS.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\UKAG Parking"; Filename: "{app}\UKAGParking.exe"
Name: "{group}\Guide d'installation"; Filename: "{app}\INSTALLATION-WINDOWS.txt"
Name: "{autodesktop}\UKAG Parking"; Filename: "{app}\UKAGParking.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\UKAGParking.exe"; Description: "Lancer UKAG Parking (MySQL doit etre demarre dans XAMPP)"; Flags: nowait postinstall skipifsilent
