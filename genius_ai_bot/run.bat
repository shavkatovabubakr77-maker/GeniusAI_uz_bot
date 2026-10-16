@echo off
title Genius AI Telegram Bot
chcp 65001 > nul
echo ====================================================
echo        Genius AI Telegram Bot Ishga Tushmoqda...
echo ====================================================
cd /d "%~dp0"
.\venv\Scripts\python.exe bot.py
pause
