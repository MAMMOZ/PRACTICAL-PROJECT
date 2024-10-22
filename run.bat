@echo off
REM Navigate to the Yolo directory
cd Yolo

REM Run the Uvicorn server
python -m uvicorn main:app --reload --host 0.0.0.0

REM Pause the command window so you can see any messages
pause
