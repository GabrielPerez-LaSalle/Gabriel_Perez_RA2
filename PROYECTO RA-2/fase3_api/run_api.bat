@echo off
REM ============================================================
REM Script para ejecutar la API
REM Fase 3: Exposición de Datos
REM ============================================================

echo ========================================
echo  Polymarket Data Warehouse API
echo  Fase 3 - Exposicion de Datos
echo ========================================
echo.

REM Verificar si el entorno virtual existe
if not exist "venv\" (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate

REM Instalar dependencias
echo.
echo Instalando dependencias...
pip install -r requirements.txt

REM Ejecutar la API
echo.
echo ========================================
echo  Iniciando API en http://localhost:8000
echo  Documentacion: http://localhost:8000/docs
echo ========================================
echo.

python main.py

pause
