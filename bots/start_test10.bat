@echo off
REM ===========================================================================
REM  [Hardcore] Ambiente de teste — 10 bots
REM ===========================================================================
REM  Sobe uma instancia do OpenKore por bot, cada uma em janela propria.
REM  --control aceita varias pastas: a do bot vem primeiro (config.txt e
REM  macros dele) e a control padrao do OpenKore preenche o resto
REM  (timeouts.txt, items_control.txt, etc.), evitando duplicar arquivos.
REM
REM  PRE-REQUISITOS:
REM    1. login/char/map-server no ar
REM    2. Os 10 personagens ja criados (ver README_TESTE.md) — o OpenKore
REM       nao cria personagem sozinho, so a conta e automatica
REM ===========================================================================

setlocal
set OK=C:\rAthena\openkore-master
set BOTS=C:\rAthena\bots
set DELAY=4

if not exist "%OK%\openkore.pl" (
    echo ERRO: OpenKore nao encontrado em %OK%
    pause & exit /b 1
)

echo Subindo a frota de teste (10 bots), %DELAY%s entre cada...
echo.

for %%B in (
    HC_Novice01
    HC_Merchant01
    HC_Knight_STR01
    HC_Priest_Supp01
    HC_Wizard_INT01
    HC_Hunter_DEX01
    HC_LK_STR01
    HC_HW_INT01
    HC_Sniper_Trap01
    HC_Creator_FCP01
) do (
    if exist "%BOTS%\%%B\config.txt" (
        echo   iniciando %%B
        start "RO Bot - %%B" /D "%OK%" perl openkore.pl ^
            --control="%BOTS%\%%B;%OK%\control" ^
            --plugins="%BOTS%\plugins;%OK%\plugins" ^
            --logs="%BOTS%\logs\%%B"
        REM  Espacamento entre logins. Mesmo com ddos_count elevado, subir 10
        REM  instancias de Perl ao mesmo tempo satura CPU e disco.
        timeout /t %DELAY% /nobreak >nul
    ) else (
        echo   AVISO: %%B sem config.txt, pulando
    )
)

echo.
echo Frota de teste no ar. Feche as janelas individualmente para parar,
echo ou use stop_bots.bat para encerrar todas de uma vez.
echo.
pause
