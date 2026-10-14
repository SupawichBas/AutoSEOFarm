@echo off
chcp 65001 > nul
title Shopee AutoSEO Farm - CEO Headquarters

cd /d "%~dp0"
python farm_ceo.py
pause
