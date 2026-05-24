@echo off
title Inventory Management System Launcher
echo ===========================================================
echo   Starting Inventory Management System Server...
echo ===========================================================
echo.

:: Automatically open the default web browser to the home page
start "" "http://127.0.0.1:8000/"

:: Launch Django server using the local virtual environment
.\venv\Scripts\python manage.py runserver

pause
