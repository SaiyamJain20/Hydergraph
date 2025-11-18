@echo off
echo Starting Hyderabad Cultural Network Recommender System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing/updating requirements...
pip install -r requirements.txt

REM Check for .env file
if not exist ".env" (
    echo.
    echo WARNING: No .env file found!
    echo Copy .env.example to .env and add your Gemini API key for natural language recommendations
    echo You can get a free API key from: https://makersuite.google.com/app/apikey
    echo.
    echo The app will work without the API key, but won't generate natural language recommendations.
    pause
)

REM Download spacy model if not present
echo Checking spaCy model...
python -m spacy download en_core_web_sm

REM Check if graph file exists
if not exist "sentence_network.graphml" (
    if not exist "sentence_network_modified.graphml" (
        echo Warning: No graph file found!
        echo Please ensure sentence_network.graphml exists in this directory
        echo You can copy it from your network analysis output
        pause
        exit /b 1
    )
)

echo.
echo Starting Flask application...
echo Access the dashboard at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python recommender_app.py