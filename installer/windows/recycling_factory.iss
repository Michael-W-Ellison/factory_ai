; Inno Setup Script for Recycling Factory
; This script creates a Windows installer with desktop and Start menu shortcuts
;
; Prerequisites:
;   1. Build the game first: python build.py
;   2. Install Inno Setup: https://jrsoftware.org/isdl.php
;   3. Run this script with Inno Setup Compiler
;
; Or use the automated build: python build_installer.py

#define MyAppName "Recycling Factory"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Michael W. Ellison"
#define MyAppURL "https://github.com/Michael-W-Ellison/factory_ai"
#define MyAppExeName "RecyclingFactory.exe"

[Setup]
; App identification
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases

; Installation directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output settings
OutputDir=..\..\dist\installer
OutputBaseFilename=RecyclingFactory_Setup_{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; Visual settings
WizardStyle=modern
; Uncomment when icon is available:
; SetupIconFile=..\..\assets\icons\icon.ico

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Misc
AllowNoIcons=yes
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable (single-file build)
Source: "..\..\dist\RecyclingFactory.exe"; DestDir: "{app}"; Flags: ignoreversion

; If using onedir build, use these instead:
; Source: "..\..\dist\RecyclingFactory\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Data files (if not bundled in exe)
; Source: "..\..\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up save files on uninstall (optional - comment out to keep saves)
; Type: filesandordirs; Name: "{app}\data\saves"

[Code]
// Custom code for installation validation
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
