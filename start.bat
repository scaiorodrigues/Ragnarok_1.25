@echo off
title rAthena - Servidor Ragnarok Online
echo ============================================
echo   Iniciando Servidor Ragnarok Online
echo ============================================
echo.

echo [1/3] Iniciando Login Server...
start "" login-server.exe

timeout /t 2 /nobreak >nul

echo [2/3] Iniciando Char Server...
start "" char-server.exe

timeout /t 2 /nobreak >nul

echo [3/3] Iniciando Map Server...
start "" map-server.exe

echo.
echo ============================================
echo   Todos os servidores foram iniciados!
echo ============================================
echo.
echo Feche esta janela quando quiser.
pause
