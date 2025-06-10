<<<<<<< HEAD
@echo off
setlocal enabledelayedexpansion

REM ----------- CONFIGURABLE -----------
set VENV_DIR=./../.venv
set REQUIREMENTS=requirements.txt
set PYTHON=python

REM ----------- Python 3.10+ check -----------
%PYTHON% --version 2>NUL | findstr /r " 3\.[1-9][0-9]*" >nul
if errorlevel 1 (
    echo [ERROR] Python 3.10+ is required and not found in PATH.
    echo Please install Python 3.10 or later and add it to your PATH.
    exit /b 1
)

REM ----------- venv creation -----------
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment...
    %PYTHON% -m venv %VENV_DIR%
)

REM ----------- Activate venv -----------
call "%VENV_DIR%\Scripts\activate.bat"

REM ----------- pip upgrade -----------
python -m pip install --upgrade pip

REM ----------- Install dependencies -----------
if exist %REQUIREMENTS% (
    pip install -r %REQUIREMENTS%
) else (
    echo [WARN] requirements.txt not found. Installing base packages...
    pip install streamlit opencv-contrib-python streamlit-webrtc numpy
)

REM ----------- Install OpenCV contrib for SIFT/SURF (if not already present) -----------
pip install opencv-contrib-python --upgrade

echo.
echo [SUCCESS] Setup complete!
echo To activate the virtual environment later, run:
echo     call %VENV_DIR%\Scripts\activate.bat
echo To start the app, run:
echo     streamlit run app.py
echo.

pause
=======
@echo off
setlocal enabledelayedexpansion

REM ----------- CONFIGURABLE -----------
set VENV_DIR=./../.venv
set REQUIREMENTS=requirements.txt
set PYTHON=python

REM ----------- Python 3.10+ check -----------
%PYTHON% --version 2>NUL | findstr /r " 3\.[1-9][0-9]*" >nul
if errorlevel 1 (
    echo [ERROR] Python 3.10+ is required and not found in PATH.
    echo Please install Python 3.10 or later and add it to your PATH.
    exit /b 1
)

REM ----------- venv creation -----------
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment...
    %PYTHON% -m venv %VENV_DIR%
)

REM ----------- Activate venv -----------
call "%VENV_DIR%\Scripts\activate.bat"

REM ----------- pip upgrade -----------
python -m pip install --upgrade pip

REM ----------- Install dependencies -----------
if exist %REQUIREMENTS% (
    pip install -r %REQUIREMENTS%
) else (
    echo [WARN] requirements.txt not found. Installing base packages...
    pip install streamlit opencv-contrib-python streamlit-webrtc numpy
)

REM ----------- Install OpenCV contrib for SIFT/SURF (if not already present) -----------
pip install opencv-contrib-python --upgrade

echo.
echo [SUCCESS] Setup complete!
echo To activate the virtual environment later, run:
echo     call %VENV_DIR%\Scripts\activate.bat
echo To start the app, run:
echo     streamlit run app.py
echo.

pause
>>>>>>> f5e81b6 (Initial commit)
