@echo off
chcp 65001 > nul
title Setup Daily AutoSEO Schedule
cd /d "%~dp0"

echo ======================================================
echo    ตั้งเวลารันระบบ TechAuto Guide อัตโนมัติทุกวัน
echo ======================================================
echo.
echo กำลังตั้งเวลาให้รันอัตโนมัติทุกวัน เวลา 08:30 น. ...
echo.

schtasks /create /tn "TechAutoGuide_Daily" /tr "\"%~dp0run.bat\"" /sc daily /st 08:30 /f

if %errorlevel% equ 0 (
    echo.
    echo [✓] ตั้งเวลาสำเร็จเรียบร้อย! ระบบจะทำงานทุกวันเวลา 08:30 น.
) else (
    echo.
    echo [!] ไม่สามารถตั้งเวลาได้ (หากต้องการใช้งาน ให้คลิกขวาแล้วเลือก 'Run as administrator')
)

echo.
pause
