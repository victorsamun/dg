@echo off

set ac=0
for %%x in (%*) do set /A ac+=1

if %ac% neq 2 (
    echo usage: %0 ^<profiles.reg^> ^<default profile path^> 1>&2
    exit /b 1
)

set profiles=%1
set default=%2
set tmpkey=HKU\_temp
set export=%~dp0%export.cmd
set runonce=Software\Microsoft\Windows\CurrentVersion\RunOnce

if exist "%profiles%" (
    reg import "%profiles%"
)

reg load "%tmpkey%" "%default%\NTUSER.DAT"
reg add "%tmpkey%\%runonce%" /v profiles /d "%export% %profiles%" /f
reg unload "%tmpkey%"
