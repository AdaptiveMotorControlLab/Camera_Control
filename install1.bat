echo OFF

@setlocal enableextensions
@cd /d "%~dp0"

echo.
echo.
echo Install Imaging Source Library...
TISGrabberSetup_3.4.0.51.exe


echo.
echo.
echo Download FFMPEG...
curl https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20190730-a0c1970-win64-static.zip -o C:%HOMEPATH%\Downloads\ffmpeg-20190730-a0c1970-win64-static.zip


echo.
echo.
echo Install FFMPEG...
powershell Expand-Archive C:%HOMEPATH%\Downloads\ffmpeg-20190730-a0c1970-win64-static.zip -DestinationPath C:%HOMEPATH%\Downloads\ffmpeg
move C:%HOMEPATH%\Downloads\ffmpeg\ffmpeg-20190730-a0c1970-win64-static "C:\Program Files\ffmpeg"


echo.
echo.
echo Setting Environmental Varibles for Imaging Source Library and FFMPEG...
SET NEW_PATH=%PATH%;C:%HOMEPATH%\Documents\The Imaging Source Europe Gmbh\Tis Grabber DLL\bin\win32;C:%HOMEPATH%\Documents\The Imaging Source Europe Gmbh\Tis Grabber DLL\bin\x64;C:\Program Files\ffmpeg\bin
powershell [System.Environment]::SetEnvironmentVariable('PATH', '%NEW_PATH%', 'Machine')


echo.
echo.
echo Create New Conda Environment: camera36
call activate.bat
conda env create -f camera_env.yml
