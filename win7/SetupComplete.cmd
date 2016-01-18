rem This is to disable auto updates
reg add ^
  "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update" ^
  /v AUOptions /t REG_DWORD /d 1 /f

net user Administrator /active:yes
net start sshd

set scripts=C:\Windows\Setup\Scripts
set profiles=W:\Users\profiles.reg

if exist "%profiles%" (
    reg import "%profiles%"
)

schtasks /ru "" /create /f /tn "profiles" /sc onlogon /tr ^
    "%scripts%\hidden.vbs %scripts%\export.cmd %profiles%"
