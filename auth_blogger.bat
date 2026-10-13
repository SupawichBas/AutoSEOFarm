@echo off
chcp 65001 > nul
title Blogger Google Login
cd /d "%~dp0"

echo ======================================================
echo    ยืนยันสิทธิ์ Google Blogger API (ทำแค่ครั้งเดียว)
echo ======================================================
echo.
echo ระบบจะเปิดเบราว์เซอร์ขึ้นมา ให้คุณเข้าสู่ระบบและกด "Allow" / "อนุญาต"
echo.

python blogger_api.py

echo.
echo ======================================================
pause
