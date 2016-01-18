@echo off

if "%1" == "" (
    set outdir=%~dp0
) else (
    set outdir=%1
)

set hs=HKLM\SOFTWARE
set ntver=Microsoft\Windows NT\CurrentVersion
set tmpfile=%TEMP%\export.reg
set allfile=%outdir%profiles.reg

type nul > "%allfile%"

call :exp "%tmpfile%" "%allfile%" "%hs%\Microsoft\IdentityStore"
call :exp "%tmpfile%" "%allfile%" "%hs%\%ntver%\PolicyGuid"
call :exp "%tmpfile%" "%allfile%" "%hs%\%ntver%\ProfileGuid"
call :exp "%tmpfile%" "%allfile%" "%hs%\%ntver%\ProfileList"
call :exp "%tmpfile%" "%allfile%" "%hs%\Wow6432Node\%ntver%\ProfileList"

del "%tmpfile%"
goto :EOF

:exp
reg query %3 >nul 2>&1
if NOT ERRORLEVEL 1 (
    reg export %3 %1 /y >nul
    type %1 >> %2
)
