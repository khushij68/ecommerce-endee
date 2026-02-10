@echo off
echo Installing Python dependencies...
pip install --user flask flask-cors requests sentence-transformers numpy python-dotenv

echo.
echo Dependencies installed!
echo.
echo Starting Flask backend server...
python app.py
