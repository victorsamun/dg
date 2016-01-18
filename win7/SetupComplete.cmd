rem This is to disable auto updates
reg add ^
  "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update" ^
  /v AUOptions /t REG_DWORD /d 1 /f

net user Administrator /active:yes
net start sshd

set scripts=C:\Windows\Setup\Scripts

rem set profiles=
if "%profiles%" == "" goto :EOF

for %%f in (%profiles%) do set profiles_dir=%%~dpf
if not exist "%profiles_dir%" goto :EOF

if exist "%profiles%" reg import "%profiles%"

schtasks /ru "" /create /f /tn "profiles" /sc onlogon /tr ^
    "%scripts%\hidden.vbs %scripts%\export.cmd %profiles%"
