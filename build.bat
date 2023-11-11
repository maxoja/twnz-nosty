@echo off
setlocal enabledelayedexpansion

:: Get the current script's directory
for %%A in ("%~dp0.") do set "THIS_DIR=%%~fA"

:: Remove the dist directory if it exists
if exist .\dist rmdir /s /q .\dist
if exist .\dist-zip rmdir /s /q .\dist-zip

:: Build the executable using pyinstaller
pyinstaller --onefile --noconsole --splash "src\banner2.png" -i"src\tray_icon.png" nosty_bot.py
pyarmor gen -O obfdist --enable-jit --mix-str --assert-import --assert-call --obf-code 0 --pack dist/nosty_bot.exe nosty_bot.py

:: Create the src directory in the dist folder
mkdir .\dist\src
mkdir .\dist\rsc
mkdir .\dist-zip

:: Copy files from src to dist/src
mkdir .\temp\nosty-bot\src
mkdir .\temp\nosty-bot\rsc
xcopy .\src\* .\temp\nosty-bot\src\ /E /Y
xcopy .\dist\* .\temp\nosty-bot\ /E /Y

:: Get the current date and time in a format like "yyyyMMdd-HHmmss"
for /f "delims=" %%a in ('wmic OS Get localdatetime ^| find "."') do set datetime=%%a
set "DATE_STR=%datetime:~0,8%-%datetime:~8,6%"

:: Zip the dist folder with the timestamp in the filename
set "destinationPath=.\dist-zip\nosty-bot-!DATE_STR!.zip"
powershell.exe -Command "Compress-Archive -Path '.\temp\*' -DestinationPath '!destinationPath!'"

endlocal