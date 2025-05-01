@echo off
setlocal

REM === CONFIGURATION ===
REM Change this to your desired Python version (must be installed)
set PYTHON=py -3.10

REM === Create virtual environment ===
if exist venv (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)

echo Creating new virtual environment using %PYTHON%...
%PYTHON% -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment. Is Python 3.10+ installed?
    exit /b 1
)

REM === Activate environment ===
call venv\Scripts\activate.bat

REM === Upgrade pip ===
echo Upgrading pip...
python -m pip install --upgrade pip

REM === Install OctoPrint ===
echo Installing OctoPrint...
pip install "https://get.octoprint.org/latest"
if errorlevel 1 (
    echo Failed to install OctoPrint.
    exit /b 1
)

REM === Install plugin in editable mode ===
echo Installing plugin in editable mode...
pip install -e .
if errorlevel 1 (
    echo Failed to install the plugin. Check if OctoPrint's setuptools was imported correctly.
    exit /b 1
)

REM === Done ===
echo.
echo Setup complete! You can now run OctoPrint with:
echo   venv\Scripts\activate
echo   octoprint serve
echo.

endlocal
pause
