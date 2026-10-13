@echo off
chcp 65001 > nul
title Shopee AutoSEO Farm
cd /d "%~dp0"

echo ======================================================
echo    Shopee AutoSEO Farm - 1-Click Autopilot
echo ======================================================
echo.

python run_farm.py

echo.
echo ======================================================
echo    ประมวลผลเสร็จสิ้นเรียบร้อยแล้ว
echo ======================================================
pause
