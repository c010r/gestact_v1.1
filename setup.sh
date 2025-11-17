#!/bin/bash

echo "========================================"
echo "    ASSE-GestACT - Script de Inicialización"
echo "========================================"
echo

# Verificar si Python3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no está instalado"
    echo "Instala Python3 primero: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

echo "[1/4] Configurando entorno virtual..."
if [ -d "venv" ]; then
    echo "Entorno virtual encontrado, activando..."
    source venv/bin/activate
    echo "✓ Entorno virtual activado"
else
    echo "Creando nuevo entorno virtual..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        source venv/bin/activate
        echo "✓ Entorno virtual creado y activado"
    else
        echo "ERROR: No se pudo crear el entorno virtual"
        exit 1
    fi
fi
echo

echo "[2/4] Actualizando pip e instalando dependencias..."
pip install --upgrade pip
if pip install -r requirements.txt; then
    echo "✓ Dependencias instaladas correctamente"
else
    echo "ERROR: Falló la instalación de dependencias"
    exit 1
fi
echo

echo "[3/4] Creando migraciones..."
if python manage.py makemigrations; then
    echo "✓ Migraciones creadas"
else
    echo "ERROR: Falló la creación de migraciones"
    exit 1
fi
echo

echo "[4/4] Aplicando migraciones a la base de datos..."
if python manage.py migrate; then
    echo "✓ Migraciones aplicadas correctamente"
else
    echo "ERROR: Falló la aplicación de migraciones"
    exit 1
fi
echo

echo "========================================"
echo "    ✓ CONFIGURACIÓN COMPLETADA"
echo "========================================"
echo
echo "El proyecto ASSE-GestACT está listo para usar."
echo "Para iniciar el servidor ejecuta:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo
echo "O simplemente ejecuta: ./run_server.sh"
echo