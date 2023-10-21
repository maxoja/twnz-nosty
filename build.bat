@echo off
setlocal enabledelayedexpansion

:: Get the current script's directory
for %%A in ("%~dp0.") do set "THIS_DIR=%%~fA"

:: Remove the dist directory if it exists
if exist .\dist rmdir /s /q .\dist
if exist .\dist-archive rmdir /s /q .\dist-archive

:: Build the executable using pyinstaller
pyinstaller --onefile --noconsole run.py

:: Create the src directory in the dist folder
mkdir .\dist\src
mkdir .\dist-archive

:: Copy files from src to dist/src
mkdir .\temp\nosty-bot\src
xcopy .\src\* .\temp\nosty-bot\src\ /E /Y
xcopy .\dist\* .\temp\nosty-bot\ /E /Y

:: Get the current date and time in a format like "yyyyMMdd-HHmmss"
for /f "delims=" %%a in ('wmic OS Get localdatetime ^| find "."') do set datetime=%%a
set "DATE_STR=%datetime:~0,8%-%datetime:~8,6%"

:: Zip the dist folder with the timestamp in the filename
set "destinationPath=.\dist-archive\mac-!DATE_STR!.zip"
powershell.exe -Command "Compress-Archive -Path '.\temp\*' -DestinationPath '!destinationPath!'"

endlocal