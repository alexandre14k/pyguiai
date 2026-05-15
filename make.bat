@echo off
REM make.bat

set APP=%CD%
for %%I in ("%APP%") do set APP=%%~nI

set ENV=out
set REQ=mods.md
set BIN=python
set DIR=%ENV%

:menu
echo.
echo   python venv cmd [%APP%]
echo.
echo   d -- dir project
echo   b -- venv setup
echo   r -- run
echo   c -- clean
echo   v -- cmd
echo   x -- exit
echo.

set /p value=">> "

if "%value%"=="d" goto dir_project
if "%value%"=="b" goto venv_setup
if "%value%"=="r" goto run
if "%value%"=="c" goto clean
if "%value%"=="v" goto bash
if "%value%"=="x" goto end

cls
goto menu

:venv_setup
if not exist "%ENV%\Scripts\activate.bat" (
    %BIN% -m venv %ENV%
)

call "%ENV%\Scripts\activate.bat"

REM pip upgrade + install
pip install --upgrade pip setuptools wheel >nul
pip install -r %REQ% >nul

goto menu

:run
if not exist "%ENV%" (
    echo run venv_setup first
    goto menu
)

if not exist "%ENV%\Scripts\activate.bat" (
    echo run venv_setup first
    goto menu
)

call env.bat 2>nul
call "%ENV%\Scripts\activate.bat"

pushd src
python -B main.py
popd

goto menu

:bash
call "%ENV%\Scripts\activate.bat"
cmd /k "title (%ENV%)"
goto menu

:clean
if exist "%ENV%" (
    set /p confirm="confirm removing '%ENV%\' ? [y/N] "
    if /I "%confirm%"=="y" (
        rmdir /s /q "%ENV%"
        echo done
    ) else (
        echo abort
    )
)
goto menu

:dir_project
tree /F /A | findstr /V "%DIR%"
goto menu

:end
exit /b
