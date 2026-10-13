@echo off
chcp 65001 > nul
echo ======================================================
echo    TechAuto Guide - Drip Release (ปล่อยบทความ 1 ชิ้น)
echo ======================================================
python release_drip.py --count 1
echo.
pause
