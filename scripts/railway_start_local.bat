@echo off
REM ============================================================
REM  START LOCAL GUNICORN SIMULADO (runserver producción Windows)
REM  NOTA: Railway usa Gunicorn (Linux). En Windows usamos waitress si existe
REM        o Django runserver 0.0.0.0:8000 con DEBUG=False simulado.
REM ============================================================
setlocal enabledelayedexpansion
chcp 65001 >nul
set "ROOT=%~dp0.."
set "BACK=%ROOT%\backend"
set "PY=%ROOT%\.venv\Scripts\python.exe"
set "PORT=%PORT:-8000%"
if "%PORT%"=="" set PORT=8000

cd /d "%BACK%"
echo ============================================================
echo  Iniciando servidor Family Health MF en 0.0.0.0:%PORT%
echo  (Producción simulada Windows - usar waitress si está instalado)
echo ============================================================
"%PY%" -m pip show waitress >nul 2>&1
if errorlevel 1 (
    echo [INFO] waitress no instalado, usando Django runserver 0.0.0.0:%PORT%
    set DJANGO_DEBUG=0
    "%PY%" manage.py runserver "0.0.0.0:%PORT%"
) else (
    echo [INFO] Iniciando waitress-serve en puerto %PORT%
    "%ROOT%\.venv\Scripts\waitress-serve.exe" --listen="*:%PORT%" --threads=8 config.wsgi:application
)
