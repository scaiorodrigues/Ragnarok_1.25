@echo off
REM  Encerra todas as instancias de OpenKore (processos perl.exe).
REM  ATENCAO: mata QUALQUER perl.exe em execucao, nao so os bots.

echo Encerrando instancias do OpenKore...
taskkill /F /IM perl.exe >nul 2>&1
if %errorLevel% equ 0 (echo   Encerradas.) else (echo   Nenhuma instancia em execucao.)
echo.
pause
