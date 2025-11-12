@echo off
echo ================================
echo Starting WhatsApp AI Server
echo ================================
echo.

REM Check if Ollama is running
curl -s http://localhost:11434 >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama is not running!
    echo Please start Ollama first or run: ollama serve
    pause
    exit /b 1
)

echo [OK] Ollama is running

REM Check if phi3 model exists
curl -s http://localhost:11434/api/tags | find "phi3" >nul
if errorlevel 1 (
    echo [WARNING] phi3 model not found
    echo Pulling phi3 model... this will take a few minutes
    curl -X POST http://localhost:11434/api/pull -d "{\"name\": \"phi3\"}"
)

echo [OK] phi3 model is ready
echo.

REM Get local IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    goto :found
)
:found
echo Your laptop IP address: %IP%
echo Configure this in the Android app: http://%IP%:5000
echo.

REM Start the server
echo Starting Flask server...
cd ai-server
python server_ollama.py
