@echo off

:: Name of the virtual environment
set ENV_NAME=.venv

:: Path to the requirements file
set REQUIREMENTS_FILE=requirements.txt

:: Check if requirements.txt exists
if not exist "%REQUIREMENTS_FILE%" (
    echo Error: '%REQUIREMENTS_FILE%' not found.
    exit /b 1
)

:: Create the virtual environment
python -m venv "%ENV_NAME%"
if errorlevel 1 (
    echo Failed to create virtual environment.
    exit /b 1
)
echo Virtual environment '%ENV_NAME%' created.

:: Activate the virtual environment
call "%ENV_NAME%\Scripts\activate.bat"

:: Install the requirements
pip install -r "%REQUIREMENTS_FILE%"
if errorlevel 1 (
    echo Failed to install requirements.
    exit /b 1
)
echo Requirements from '%REQUIREMENTS_FILE%' installed.

:: Install the silkmoth package
pip install -e ../src
if errorlevel 1 (
    echo Failed to install the silkmoth package.
    exit /b 1
)
echo Silkmoth package installed.

powershell -ExecutionPolicy Bypass -File "%ENV_NAME%\Scripts\Activate.ps1"
echo Virtual environment '%ENV_NAME%' activated.

:: Check if the activation was successful
if not defined VIRTUAL_ENV (
    echo Error: Virtual environment activation failed.
    exit /b 1
)
echo Virtual environment '%ENV_NAME%' is ready to use.
streamlit run app.py