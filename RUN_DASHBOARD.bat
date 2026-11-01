@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Virtual environment not found. Run FIRST_TIME_SETUP.bat first.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
python main.py setup
python -m streamlit run app.py
pause
