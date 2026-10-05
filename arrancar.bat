@echo off
REM ============================================================
REM  Club Family Health MF - Arrancar ambos servidores (Dev)
REM  Python 3.10.x requerido + .venv creado + dependencias instaladas
REM ============================================================

echo.
echo ============================================================
echo   Club Family Health MF - Arrancando entorno desarrollo
echo   Backend Django  : http://127.0.0.1:8000
echo   Frontend Vite   : http://127.0.0.1:5173
echo ============================================================
echo.

REM --- Rutas raiz proyecto y entornos ---
set ROOT=%~dp0
set VENV=%ROOT%.venv\Scripts\python.exe

REM --- 1) Arrancar Django Backend en una ventana nueva ---
REM --- 0.0.0.0:8000 permite acceso desde m vil/celular en LAN (Mobile-First) ---
echo [1/2] Arrancando BACKEND Django (0.0.0.0:8000 / acceso LAN m vil habilitado) ...
start "CFH-BACKEND" cmd /k "cd /d %ROOT%backend && "%VENV%" manage.py runserver 0.0.0.0:8000"

REM --- Delay para que arranque Django antes del Frontend ---
timeout /t 3 /nobreak >nul

REM --- 2) Arrancar Vite Frontend en otra ventana nueva ---
echo [2/2] Arrancando FRONTEND Vite (0.0.0.0:5173 / acceso LAN m vil habilitado) ...
start "CFH-FRONTEND" cmd /k "cd /d %ROOT%frontend && npm.cmd run dev"

echo.
echo Hecho. Ambas ventanas deben abrirse.
echo ============================================================
echo  ACCESO DESDE ESTE PC:
echo    Backend :  http://127.0.0.1:8000/api/v1/health/
echo    Frontend:  http://127.0.0.1:5173/
echo.
echo  ACCESO DESDE CELULAR EN LA MISMA RED WiFi (Mobile-First):
echo    Backend :  http://[IP-DEL-PC-EN-LAN]:8000/api/v1/health/
echo    Frontend:  http://[IP-DEL-PC-EN-LAN]:5173/
echo ============================================================
echo Cierra estas ventanas o pulsa Ctrl+C en ellas para detener los servidores.
timeout /t 10 /nobreak >nul
