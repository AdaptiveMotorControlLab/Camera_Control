echo OFF

echo.
echo.
echo Initialize system setup via write_camera_details.py file
copy write_camera_details_TEMPLATE.py write_camera_details.py
python write_camera_details.py


echo.
echo.
echo Write Shortcut File to the Desktop
echo call activate.bat > C:%HOMEPATH%\Desktop\cameraGUI.bat
echo call activate camera36 >> C:%HOMEPATH%\Desktop\cameraGUI.bat
echo cd %cd% >> C:%HOMEPATH%\Desktop\cameraGUI.bat
echo python camera_control_GUI.py >> C:%HOMEPATH%\Desktop\cameraGUI.bat

echo.
echo.
echo Installation complete!
echo Please edit 'write_camera_details.py' according to your system's camera configuration (see README for further instructions).
echo Next, run the program by calling python camera_control_GUI.py or run the 'cameraGUI.bat' shortcut on the Desktop!

pause
