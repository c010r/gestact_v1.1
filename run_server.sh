#!/bin/bash

echo "========================================"
echo "    ASSE-GestACT - Iniciando Servidor"
echo "========================================"
echo

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "ERROR: No se encontró el entorno virtual"
    echo "Ejecuta primero: ./setup.sh"
    exit 1
fi

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate
echo "✓ Entorno virtual activado"
echo

# Verificar si la base de datos existe
if [ ! -f "db.sqlite3" ]; then
    echo "Base de datos no encontrada. Ejecutando migraciones..."
    python manage.py makemigrations
    python manage.py migrate
    echo "✓ Base de datos configurada"
    echo
fi

echo "Iniciando servidor Django..."
echo "Servidor disponible en: http://127.0.0.1:8000/"
echo "Presiona Ctrl+C para detener el servidor"
echo

python manage.py runserver