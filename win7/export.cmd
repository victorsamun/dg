@echo off

if "%1" == "" (
    echo usage: %0 ^<output.reg^> 1>&2
    exit /b 1
) else (
    set output=%1
)

set hs=HKLM\SOFTWARE
set ntver=Microsoft\Windows NT\CurrentVersion
set tmpfile=%TEMP%\export.reg

type nul > "%output%"

call :exp "%tmpfile%" "%output%" "%hs%\Microsoft\IdentityStore"
call :exp "%tmpfile%" "%output%" "%hs%\%ntver%\PolicyGuid"
call :exp "%tmpfile%" "%output%" "%hs%\%ntver%\ProfileGuid"
call :exp "%tmpfile%" "%output%" "%hs%\%ntver%\ProfileList"
call :exp "%tmpfile%" "%output%" "%hs%\Wow6432Node\%ntver%\ProfileList"

del "%tmpfile%"
exit /b

:exp
reg query %3 >nul 2>&1
if NOT ERRORLEVEL 1 (
    reg export %3 %1 /y
    type %1 >> %2
)
