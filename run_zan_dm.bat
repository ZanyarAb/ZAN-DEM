@echo off
title ZAN-DM - PornHub Link Extractor
color 0A

echo ███████╗ █████╗ ███╗   ██╗      ██████╗ ███╗   ███╗
echo ╚══███╔╝██╔══██╗████╗  ██║      ██╔══██╗████╗ ████║
echo   ███╔╝ ███████║██╔██╗ ██║█████╗██║  ██║██╔████╔██║
echo  ███╔╝  ██╔══██║██║╚██╗██║╚════╝██║  ██║██║╚██╔╝██║
echo ███████╗██║  ██║██║ ╚████║      ██████╔╝██║ ╚═╝ ██║
echo ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝      ╚═════╝ ╚═╝     ╚═╝
echo.

echo Checking required libraries...
echo.

:: Check and install required libraries
pip show requests >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing requests library...
    pip install requests
)

pip show beautifulsoup4 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing beautifulsoup4 library...
    pip install beautifulsoup4
)

pip show colorama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing colorama library...
    pip install colorama
)

echo.
echo Running ZAN-DM...
echo.

:: Run Python script
python zan_dm.py %*

echo.
echo Press any key to exit...
pause >nul