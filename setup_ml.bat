@echo off
echo ===================================================
echo           ML System Setup Script
echo ===================================================
echo.

:: Set UTF-8 code page for better emoji support
chcp 65001 > nul

:: Set paths 
set PROJECT_ROOT=%~dp0
set ML_SYSTEM=%PROJECT_ROOT%ml_system
set PYTHON_EXE=python

:: Check Python installation
echo Checking Python installation...
%PYTHON_EXE% --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH.
    exit /b 1
)

:: Install required packages
echo Installing required packages...
%PYTHON_EXE% -m pip install pandas scikit-learn numpy joblib flask psycopg2-binary > nul 2>&1

:: Create required directories
echo Creating directories...
if not exist "%ML_SYSTEM%\data" mkdir "%ML_SYSTEM%\data"
if not exist "%ML_SYSTEM%\modelos" mkdir "%ML_SYSTEM%\modelos"
if not exist "%ML_SYSTEM%\tests" mkdir "%ML_SYSTEM%\tests"

:: Extract data
echo Extracting data from database...
%PYTHON_EXE% "%ML_SYSTEM%\scripts\standalone_data_extractor.py"

:: Train models
echo Training ML models...
%PYTHON_EXE% "%ML_SYSTEM%\scripts\train_models_fixed.py"

:: Test ML system
echo Testing ML system...
%PYTHON_EXE% "%ML_SYSTEM%\test_ml_pipeline.py"

echo.
echo ===================================================
echo ML System Setup Complete!
echo ===================================================
echo.
echo Next steps:
echo 1. Start Flask server: python run.py
echo 2. Test ML endpoints with:
echo    - GET http://localhost:5000/ml/health
echo    - POST http://localhost:5000/ml/predict/enrollment
echo.
echo For more information, see: ml_system\README.md
echo.
