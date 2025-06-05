@echo off
echo ===================================================
echo            ML System & Flask Startup
echo ===================================================

:: Set UTF-8 code page for better emoji support
chcp 65001 > nul

echo Checking ML system status...

:: Check if models exist, if not run setup
if not exist "ml_system\modelos\enrollment_prediction_model.pkl" (
    echo ML models not found. Running setup...
    call setup_ml.bat
) else (
    echo ML models found. System ready.
)

echo.
echo Starting Flask server...
echo.
echo Once server is running, test endpoints with:
echo    python ml_system\test_ml_endpoints.py
echo.
echo Press Ctrl+C to stop the server.
echo.

python run.py
