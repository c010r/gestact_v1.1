@echo off
echo ========================================
echo    ASSE-GestACT - Script de Inicializacion
echo ========================================
echo.

echo [1/4] Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: No se pudo activar el entorno virtual
    echo Asegurate de que existe la carpeta 'venv'
    pause
    exit /b 1
)
echo ✓ Entorno virtual activado
echo.

echo [2/4] Instalando dependencias desde requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Fallo la instalacion de dependencias
    pause
    exit /b 1
)
echo ✓ Dependencias instaladas correctamente
echo.

echo [3/4] Creando migraciones...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo ERROR: Fallo la creacion de migraciones
    pause
    exit /b 1
)
echo ✓ Migraciones creadas
echo.

echo [4/4] Aplicando migraciones a la base de datos...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: Fallo la aplicacion de migraciones
    pause
    exit /b 1
)
echo ✓ Migraciones aplicadas correctamente
echo.

echo ========================================
echo    ✓ CONFIGURACION COMPLETADA
echo ========================================
echo.
echo El proyecto ASSE-GestACT esta listo para usar.
echo Para iniciar el servidor ejecuta: python manage.py runserver
echo.
pause