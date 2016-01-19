rem This is to disable auto updates
reg add ^
  "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update" ^
  /v AUOptions /t REG_DWORD /d 1 /f

net user Administrator /active:yes
net start sshd

rem the next line is to ease preprocessing, do not remove
rem set profiles=
if "%profiles%" == "" exit /b

for %%f in (%profiles%) do set profiles_dir=%%~dpf
if not exist "%profiles_dir%" exit /b

if exist "%profiles%" reg import "%profiles%"

set scripts=%~dp0
schtasks /ru "" /create /f /tn "profiles" /sc onlogon /tr ^
    "%scripts%hidden.vbs %scripts%export.cmd %profiles%"
