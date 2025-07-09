@echo off
echo Starting LLM Chat Demo...
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please create a .env file with your OpenAI API key:
    echo OPENAI_API_KEY=your-openai-api-key-here
    echo.
    pause
    exit /b 1
)

echo.
echo Starting Flask application...
echo Open your browser and navigate to http://localhost:5000
echo.
python main.py
