@echo off
REM ============================================================
REM  BUILD LOCAL (Simula Railway build - Windows PowerShell)
REM  Proyecto: Club Family Health MF
REM  Uso: Doble clic o: .\scripts\railway_build_local.bat
REM ============================================================
setlocal enabledelayedexpansion
chcp 65001 >nul
set "ROOT=%~dp0.."
set "BACK=%ROOT%\backend"
set "FRONT=%ROOT%\frontend"
set "PY=%ROOT%\.venv\Scripts\python.exe"
set "NPM=npm.cmd"

echo ============================================================
echo  [1/5] Instalando frontend (npm ci)
echo ============================================================
cd /d "%FRONT%"
call "%NPM%" ci --no-audit --no-fund
if errorlevel 1 goto :err

echo.
echo ============================================================
echo  [2/5] Compilando SPA Vue 3 (vite build)
echo ============================================================
call "%NPM%" run build
if errorlevel 1 goto :err

echo.
echo ============================================================
echo  [3/5] Asegurando requirements backend
echo ============================================================
cd /d "%BACK%"
"%PY%" -m pip install -q -r requirements.txt
if errorlevel 1 goto :err

echo.
echo ============================================================
echo  [4/5] collectstatic Django
echo ============================================================
"%PY%" manage.py collectstatic --noinput --clear
if errorlevel 1 goto :err

echo.
echo ============================================================
echo  [5/5] migrate + seed bootstrap
echo ============================================================
"%PY%" manage.py migrate --noinput
"%PY%" bootstrap_data.py

echo.
echo ============================================================
echo  BUILD LOCAL COMPLETADO OK.
echo  Ahora puedes ejecutar: scripts\railway_start_local.bat
echo ============================================================
exit /b 0

:err
echo.
echo [ERROR] Fase fallida. Revisa logs arriba.
exit /b 1
