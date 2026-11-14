@echo off
title Kodi Manager Server
cd /d C:\Users\ngwanyijegmail.com\kodi_manager
call env\Scripts\activate
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:8000/"
python manage.py runserver
pause
