rem This is to disable auto updates
reg add ^
  "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update" ^
  /v AUOptions /t REG_DWORD /d 1 /f

net user Administrator /active:yes
net start sshd
