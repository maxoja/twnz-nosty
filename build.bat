@echo off
setlocal enabledelayedexpansion

:: Get the current script's directory
for %%A in ("%~dp0.") do set "THIS_DIR=%%~fA"

:: Remove the dist directory if it exists
if exist .\dist rmdir /s /q .\dist

:: Build the executable using pyinstaller
pyinstaller build.spec

:: Create the src directory in the dist folder
:: mkdir .\dist\src

:: Copy files from src to dist/src
:: xcopy .\src\* .\dist\src\ /E /Y

:: Get the current date and time in a format like "yyyyMMdd-HHmmss"
for /f "tokens=1-4 delims=:/ " %%a in ("%date% %time%") do (
    set "DATE_STR=%%c%%b%%a-%%d"
)

:: Zip the dist folder with the timestamp in the filename
powershell -Command "Compress-Archive -Path .\dist -DestinationPath .\dist\mac-%DATE_STR%.zip"

endlocal
