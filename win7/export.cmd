@echo off

set HS=HKLM\SOFTWARE
set NTVER=Microsoft\Windows NT\CurrentVersion
set TMPFILE=%~dp0%current.reg
set ALLFILE=%~dp0%profiles.reg

echo. > "%ALLFILE%"

call :exp "%HS%\Microsoft\IdentityStore"         "%TMPFILE%" "%ALLFILE%"
call :exp "%HS%\%NTVER%\PolicyGuid"              "%TMPFILE%" "%ALLFILE%"
call :exp "%HS%\%NTVER%\ProfileGuid"             "%TMPFILE%" "%ALLFILE%"
call :exp "%HS%\%NTVER%\ProfileList"             "%TMPFILE%" "%ALLFILE%"
call :exp "%HS%\Wow6432Node\%NTVER%\ProfileList" "%TMPFILE%" "%ALLFILE%"

del "%TMPFILE%"
goto :EOF

:exp
reg query %1 >nul 2>&1
if NOT ERRORLEVEL 1 (
    reg export %1 %2 /y >nul
    type %2 >> %3
)
