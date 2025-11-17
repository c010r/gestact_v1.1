#!/usr/bin/env python
"""
Script automatizado de creación de base de datos ASSE-GestACT
Este script puede ejecutarse con parámetros desde la API web
"""

import os
import sys
import django
import json
import argparse
import subprocess
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgai.settings')
django.setup()

# Configuraciones de motores de BD
DB_ENGINES = {
    'sqlite': {
        'engine': 'django.db.backends.sqlite3',
        'default_name': 'db.sqlite3',
        'requires_server': False,
        'default_host': '',
        'default_port': '',
        'default_user': ''
    },
    'postgresql': {
        'engine': 'django.db.backends.postgresql',
        'default_name': 'asse_gestit_db',
        'requires_server': True,
        'default_host': 'localhost',
        'default_port': '5432',
        'default_user': 'asse_gestit_user'
    },
    'mysql': {
        'engine': 'django.db.backends.mysql',
        'default_name': 'asse_gestit_db',
        'requires_server': True,
        'default_host': 'localhost',
        'default_port': '3306',
        'default_user': 'asse_gestit_user'
    },
    'oracle': {
        'engine': 'django.db.backends.oracle',
        'default_name': 'asse_gestit_db',
        'requires_server': True,
        'default_host': 'localhost',
        'default_port': '1521',
        'default_user': 'asse_gestit_user'
    }
}

def log_step(message, step_type="info"):
    """Registra un paso del proceso"""
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "process": "🔄"
    }
    icon = icons.get(step_type, "ℹ️")
    print(f"{icon} {message}")
    sys.stdout.flush()

def generar_script_sql(motor, params):
    """Genera el script SQL para el motor especificado"""
    log_step(f"Generando script SQL para {motor.upper()}", "process")
    
    if motor == 'postgresql':
        sql_script = f'''
-- Script de inicialización para PostgreSQL
-- Base de datos: {params['nombre']}
-- Usuario: {params['usuario']}

-- Crear base de datos
DROP DATABASE IF EXISTS {params['nombre']};
CREATE DATABASE {params['nombre']}
    WITH ENCODING 'UTF8'
    LC_COLLATE = 'es_ES.UTF-8'
    LC_CTYPE = 'es_ES.UTF-8'
    TEMPLATE template0;

-- Crear usuario
DROP USER IF EXISTS {params['usuario']};
CREATE USER {params['usuario']} WITH PASSWORD '{params['password']}';
GRANT ALL PRIVILEGES ON DATABASE {params['nombre']} TO {params['usuario']};

-- Conectar a la base de datos
\\c {params['nombre']}

-- Otorgar permisos en el esquema public
GRANT ALL ON SCHEMA public TO {params['usuario']};
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {params['usuario']};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {params['usuario']};

-- Configurar permisos por defecto
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {params['usuario']};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {params['usuario']};

SELECT 'PostgreSQL configurado correctamente para ASSE-GestACT' AS status;
'''
        
    elif motor == 'mysql':
        sql_script = f'''
-- Script de inicialización para MySQL
-- Base de datos: {params['nombre']}
-- Usuario: {params['usuario']}

-- Crear base de datos
DROP DATABASE IF EXISTS {params['nombre']};
CREATE DATABASE {params['nombre']}
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Crear usuario
DROP USER IF EXISTS '{params['usuario']}'@'localhost';
DROP USER IF EXISTS '{params['usuario']}'@'%';
CREATE USER '{params['usuario']}'@'localhost' IDENTIFIED BY '{params['password']}';
CREATE USER '{params['usuario']}'@'%' IDENTIFIED BY '{params['password']}';

-- Otorgar permisos
GRANT ALL PRIVILEGES ON {params['nombre']}.* TO '{params['usuario']}'@'localhost';
GRANT ALL PRIVILEGES ON {params['nombre']}.* TO '{params['usuario']}'@'%';

-- Aplicar cambios
FLUSH PRIVILEGES;

-- Usar la base de datos
USE {params['nombre']};

SELECT 'MySQL configurado correctamente para ASSE-GestACT' AS status;
'''
        
    elif motor == 'oracle':
        sql_script = f'''
-- Script de inicialización para Oracle
-- Base de datos: {params['nombre']}
-- Usuario: {params['usuario']}

-- Crear tablespace
CREATE TABLESPACE asse_gestit_data
DATAFILE 'asse_gestit_data.dbf' SIZE 100M
AUTOEXTEND ON NEXT 10M MAXSIZE UNLIMITED;

-- Crear usuario
DROP USER {params['usuario']} CASCADE;
CREATE USER {params['usuario']}
    IDENTIFIED BY {params['password']}
    DEFAULT TABLESPACE asse_gestit_data
    QUOTA UNLIMITED ON asse_gestit_data;

-- Otorgar permisos
GRANT CONNECT, RESOURCE, DBA TO {params['usuario']};
GRANT CREATE SESSION TO {params['usuario']};
GRANT CREATE TABLE TO {params['usuario']};
GRANT CREATE SEQUENCE TO {params['usuario']};
GRANT CREATE VIEW TO {params['usuario']};
GRANT CREATE PROCEDURE TO {params['usuario']};
GRANT CREATE TRIGGER TO {params['usuario']};

SELECT 'Oracle configurado correctamente para ASSE-GestACT' FROM dual;
'''
    else:
        return None
    
    # Guardar script
    script_filename = f'init_{motor}.sql'
    with open(script_filename, 'w', encoding='utf-8') as f:
        f.write(sql_script)
    
    log_step(f"Script SQL generado: {script_filename}", "success")
    return script_filename

def configurar_django_settings(motor, params):
    """Configura temporalmente Django para usar la nueva BD"""
    log_step("Configurando Django para la nueva base de datos", "process")
    
    from django.conf import settings
    
    # Crear configuración de BD
    bd_config = {
        'ENGINE': DB_ENGINES[motor]['engine'],
        'NAME': params['nombre']
    }
    
    if DB_ENGINES[motor]['requires_server']:
        bd_config.update({
            'HOST': params['host'],
            'PORT': params['puerto'],
            'USER': params['usuario'],
            'PASSWORD': params['password'],
            'OPTIONS': {}
        })
    
    # Actualizar configuración temporalmente
    settings.DATABASES['default'] = bd_config
    
    log_step(f"Django configurado para {motor.upper()}", "success")
    return bd_config

def ejecutar_migraciones():
    """Ejecuta las migraciones de Django"""
    log_step("Creando migraciones para la aplicación seteo", "process")
    
    try:
        # Crear migraciones
        from django.core.management import call_command
        from io import StringIO
        
        # Capturar salida
        out = StringIO()
        call_command('makemigrations', 'seteo', stdout=out, verbosity=0)
        makemigrations_output = out.getvalue()
        
        if "No changes detected" not in makemigrations_output:
            log_step("Nuevas migraciones creadas", "success")
        else:
            log_step("No se detectaron cambios en los modelos", "info")
        
        log_step("Aplicando migraciones", "process")
        
        # Aplicar migraciones
        out = StringIO()
        call_command('migrate', stdout=out, verbosity=1)
        migrate_output = out.getvalue()
        
        log_step("Migraciones aplicadas correctamente", "success")
        return True
        
    except Exception as e:
        log_step(f"Error en migraciones: {str(e)}", "error")
        return False

def crear_datos_iniciales(motor, params):
    """Crea los datos iniciales en la BD"""
    log_step("Creando datos iniciales", "process")
    
    try:
        from seteo.models import ConfiguracionSistema, Rol, Usuario
        
        # Crear configuración de BD
        bd_config = {
            'engine': DB_ENGINES[motor]['engine'],
            'name': params['nombre'],
            'host': params.get('host', ''),
            'port': params.get('puerto', ''),
            'user': params.get('usuario', ''),
            'password': params.get('password', ''),
            'options': '{}'
        }
        
        config_bd, created = ConfiguracionSistema.objects.get_or_create(
            nombre='configuracion_bd',
            defaults={
                'tipo': 'database',
                'valor': bd_config,
                'descripcion': f'Configuración de base de datos {motor.upper()}'
            }
        )
        
        if created:
            log_step(f"Configuración de BD {motor.upper()} creada", "success")
        else:
            config_bd.valor = bd_config
            config_bd.descripcion = f'Configuración de base de datos {motor.upper()}'
            config_bd.save()
            log_step(f"Configuración de BD {motor.upper()} actualizada", "success")
        
        # Crear configuración de Keycloak
        config_keycloak, created = ConfiguracionSistema.objects.get_or_create(
            nombre='configuracion_keycloak',
            defaults={
                'tipo': 'authentication',
                'valor': {
                    'server_url': 'http://localhost:8080',
                    'realm': 'asse-gestit',
                    'client_id': 'asse-gestit-client',
                    'client_secret': '',
                    'admin_username': 'admin',
                    'admin_password': 'admin'
                },
                'descripcion': 'Configuración de Keycloak'
            }
        )
        
        if created:
            log_step("Configuración de Keycloak creada", "success")
        
        # Crear roles
        roles_data = [
            {'nombre': 'Administrador', 'descripcion': 'Acceso completo al sistema'},
            {'nombre': 'Usuario', 'descripcion': 'Acceso básico al sistema'},
            {'nombre': 'Supervisor', 'descripcion': 'Acceso de supervisión'}
        ]
        
        for rol_data in roles_data:
            rol, created = Rol.objects.get_or_create(
                nombre=rol_data['nombre'],
                defaults={
                    'descripcion': rol_data['descripcion'],
                    'activo': True
                }
            )
            if created:
                log_step(f"Rol '{rol_data['nombre']}' creado", "success")
        
        # Crear usuario administrador
        admin_user, created = Usuario.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'email': 'admin@asse-gestit.com',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
                'estado': 'activo'
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            
            # Asignar rol de administrador
            admin_rol = Rol.objects.get(nombre='Administrador')
            admin_user.roles.add(admin_rol)
            
            log_step("Usuario administrador creado (admin/admin123)", "success")
        
        return True
        
    except Exception as e:
        log_step(f"Error al crear datos iniciales: {str(e)}", "error")
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Script automatizado de creación de BD ASSE-GestACT'
    )
    parser.add_argument(
        '--motor',
        required=True,
        choices=['sqlite', 'postgresql', 'mysql', 'oracle'],
        help='Motor de base de datos',
    )
    parser.add_argument(
        '--params-file',
        required=True,
        help='Archivo JSON con parámetros de configuración',
    )
    
    args = parser.parse_args()
    
    # Cargar parámetros
    try:
        with open(args.params_file, 'r') as f:
            params = json.load(f)
    except Exception as e:
        log_step(f"Error al cargar parámetros: {str(e)}", "error")
        return False
    
    log_step(
        "=== Iniciando creación automatizada de base de datos ASSE-GestACT ===",
        "info",
    )
    log_step(f"Motor seleccionado: {args.motor.upper()}", "info")
    log_step(f"Base de datos: {params['nombre']}", "info")
    
    if DB_ENGINES[args.motor]['requires_server']:
        log_step(f"Host: {params['host']}:{params['puerto']}", "info")
        log_step(f"Usuario: {params['usuario']}", "info")
    
    # Generar script SQL si es necesario
    if DB_ENGINES[args.motor]['requires_server']:
        script_file = generar_script_sql(args.motor, params)
        if script_file:
            log_step(
                "IMPORTANTE: Ejecuta el script SQL antes de continuar: "
                f"{script_file}",
                "warning",
            )
    
    # Configurar Django
    configurar_django_settings(args.motor, params)
    
    # Ejecutar migraciones
    if not ejecutar_migraciones():
        log_step("Error en las migraciones", "error")
        return False
    
    # Crear datos iniciales
    if not crear_datos_iniciales(args.motor, params):
        log_step("Error al crear datos iniciales", "error")
        return False
    
    log_step("=== Base de datos creada exitosamente ===", "success")
    log_step(f"Configuración guardada para {args.motor.upper()}", "success")
    
    if DB_ENGINES[args.motor]['requires_server']:
        log_step(
            f"Recuerda ejecutar el script SQL: init_{args.motor}.sql",
            "warning",
        )
    
    log_step(
        "Accede a la configuración en: http://127.0.0.1:8000/"
        "seteo/base-datos/",
        "info",
    )
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
