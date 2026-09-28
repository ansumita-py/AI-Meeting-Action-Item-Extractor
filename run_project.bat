@echo off
echo Installing required package...
pip install -r requirements.txt
echo.
echo Starting AI Meeting Action-Item Extractor...
python app.py
pause
