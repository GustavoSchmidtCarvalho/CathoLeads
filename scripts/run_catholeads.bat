@echo off
setlocal enabledelayedexpansion

REM Executa o CathoLeads.exe e abre o log ao final.
REM Coloque este .bat na mesma pasta do CathoLeads.exe (ex: dist\CathoLeads\)

set "APP_DIR=%~dp0"
set "EXE=%APP_DIR%CathoLeads.exe"
set "LOG=%APP_DIR%output\logs\catho_leads.log"

echo.
echo === CathoLeads ===
echo Pasta: %APP_DIR%

if not exist "%EXE%" (
  echo ERRO: Nao encontrei o executavel:
  echo   %EXE%
  echo.
  pause
  exit /b 2
)

echo Executando...
echo.

REM /wait garante que o .bat aguarde o termino para abrir o log depois.
start "CathoLeads" /wait "%EXE%"
set "EXITCODE=%ERRORLEVEL%"

echo.
echo Finalizou com codigo: %EXITCODE%

if exist "%LOG%" (
  echo Abrindo log: %LOG%
  notepad "%LOG%"
) else (
  echo Log ainda nao existe: %LOG%
)

echo.
pause
exit /b %EXITCODE%
