@echo off
REM Script de instalación y ejecución para Windows
REM FASE 1: Extracción de Datos de Polymarket

echo ============================================================
echo  FASE 1: Extracción de Datos de Polymarket
echo ============================================================
echo.

REM Verificar Python
echo Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    pause
    exit /b 1
)
echo.

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo.

REM Crear directorios si no existen
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "delta_lake" mkdir delta_lake

echo ============================================================
echo  Ejecutando extracción de datos...
echo ============================================================
echo.

REM Ejecutar el script principal
python main.py

echo.
echo ============================================================
echo  Proceso completado
echo ============================================================
pause
