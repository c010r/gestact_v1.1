#!/usr/bin/env python
"""
Script para crear la base de datos desde cero con soporte para múltiples motores de BD
"""

import os
import sys
import django
import subprocess
import json
from django.core.management import execute_from_command_line
from django.db import connection
from django.core.management.commands.migrate import Command as MigrateCommand

# Configuraciones por motor de base de datos
DB_ENGINES = {
    'sqlite': {
        'engine': 'django.db.backends.sqlite3',
        'default_name': 'db.sqlite3',
        'default_port': '',
        'requires_server': False,
        'init_script': 'init_sqlite'
    },
    'postgresql': {
        'engine': 'django.db.backends.postgresql',
        'default_name': 'asse_gestit_db',
        'default_port': '5432',
        'requires_server': True,
        'init_script': 'init_postgresql'
    },
    'mysql': {
        'engine': 'django.db.backends.mysql',
        'default_name': 'asse_gestit_db',
        'default_port': '3306',
        'requires_server': True,
        'init_script': 'init_mysql'
    },
    'oracle': {
        'engine': 'django.db.backends.oracle',
        'default_name': 'asse_gestit_db',
        'default_port': '1521',
        'requires_server': True,
        'init_script': 'init_oracle'
    }
}

def init_sqlite():
    """Inicialización específica para SQLite"""
    print("📁 Configurando SQLite...")
    db_file = 'db.sqlite3'
    if os.path.exists(db_file):
        print(f"Eliminando base de datos SQLite existente: {db_file}")
        try:
            os.remove(db_file)
            print("✓ Base de datos SQLite eliminada")
        except PermissionError:
            print("⚠️  No se pudo eliminar la BD (en uso). Continuando...")
            try:
                connection.close()
                os.remove(db_file)
                print("✓ Base de datos SQLite eliminada después de cerrar conexiones")
            except:
                print("⚠️  Continuando sin eliminar BD existente")
    return True

def init_postgresql():
    """Inicialización específica para PostgreSQL"""
    print("🐘 Configurando PostgreSQL...")
    try:
        # Intentar verificar si PostgreSQL está disponible (opcional)
        try:
            result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ PostgreSQL detectado: {result.stdout.strip()}")
            else:
                print("⚠️  PostgreSQL no detectado en PATH, pero generando script SQL...")
        except FileNotFoundError:
            print("⚠️  PostgreSQL no detectado en PATH, pero generando script SQL...")
        
        # Script SQL para crear la base de datos
        sql_script = """
        -- Crear base de datos ASSE-GestACT
        DROP DATABASE IF EXISTS asse_gestit_db;
        CREATE DATABASE asse_gestit_db
            WITH ENCODING 'UTF8'
            LC_COLLATE = 'es_ES.UTF-8'
            LC_CTYPE = 'es_ES.UTF-8'
            TEMPLATE template0;
        
        -- Crear usuario para la aplicación
        DROP USER IF EXISTS asse_gestit_user;
        CREATE USER asse_gestit_user WITH PASSWORD 'asse_gestit_password';
        GRANT ALL PRIVILEGES ON DATABASE asse_gestit_db TO asse_gestit_user;
        """
        
        with open('init_postgresql.sql', 'w', encoding='utf-8') as f:
            f.write(sql_script)
        
        print("📄 Script SQL de PostgreSQL creado: init_postgresql.sql")
        print("💡 Para ejecutar: psql -U postgres -f init_postgresql.sql")
        return True
        
    except Exception as e:
        print(f"❌ Error al generar script PostgreSQL: {e}")
        return False

def init_mysql():
    """Inicialización específica para MySQL"""
    print("🐬 Configurando MySQL...")
    try:
        # Intentar verificar si MySQL está disponible (opcional)
        try:
            result = subprocess.run(['mysql', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ MySQL detectado: {result.stdout.strip()}")
            else:
                print("⚠️  MySQL no detectado en PATH, pero generando script SQL...")
        except FileNotFoundError:
            print("⚠️  MySQL no detectado en PATH, pero generando script SQL...")
        
        # Script SQL para crear la base de datos
        sql_script = """
        -- Crear base de datos ASSE-GestACT
        DROP DATABASE IF EXISTS asse_gestit_db;
        CREATE DATABASE asse_gestit_db
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci;
        
        -- Crear usuario para la aplicación
        DROP USER IF EXISTS 'asse_gestit_user'@'localhost';
        CREATE USER 'asse_gestit_user'@'localhost'
            IDENTIFIED BY 'asse_gestit_password';
        GRANT ALL PRIVILEGES ON asse_gestit_db.*
            TO 'asse_gestit_user'@'localhost';
        FLUSH PRIVILEGES;
        """
        
        with open('init_mysql.sql', 'w', encoding='utf-8') as f:
            f.write(sql_script)
        
        print("📄 Script SQL de MySQL creado: init_mysql.sql")
        print("💡 Para ejecutar: mysql -u root -p < init_mysql.sql")
        return True
        
    except Exception as e:
        print(f"❌ Error al generar script MySQL: {e}")
        return False

def init_oracle():
    """Inicialización específica para Oracle"""
    print("🔶 Configurando Oracle...")
    try:
        # Intentar verificar si Oracle está disponible (opcional)
        try:
            result = subprocess.run(['sqlplus', '-v'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Oracle detectado")
            else:
                print("⚠️  Oracle no detectado en PATH, pero generando script SQL...")
        except FileNotFoundError:
            print("⚠️  Oracle no detectado en PATH, pero generando script SQL...")
        
        # Script SQL para crear la base de datos
        sql_script = """
        -- Crear usuario y tablespace para ASSE-GestACT
        CREATE TABLESPACE asse_gestit_data
            DATAFILE 'asse_gestit_data.dbf' SIZE 100M
            AUTOEXTEND ON NEXT 10M MAXSIZE UNLIMITED;
        
        DROP USER asse_gestit_user CASCADE;
        CREATE USER asse_gestit_user
            IDENTIFIED BY asse_gestit_password
            DEFAULT TABLESPACE asse_gestit_data
            QUOTA UNLIMITED ON asse_gestit_data;

    GRANT CONNECT, RESOURCE, CREATE VIEW TO asse_gestit_user;
        """
        
        with open('init_oracle.sql', 'w', encoding='utf-8') as f:
            f.write(sql_script)
        
        print("📄 Script SQL de Oracle creado: init_oracle.sql")
        print("💡 Para ejecutar: sqlplus system/password @init_oracle.sql")
        return True
        
    except Exception as e:
        print(f"❌ Error al generar script Oracle: {e}")
        return False

def seleccionar_motor_bd():
    """Permite al usuario seleccionar el motor de base de datos"""
    print("\n=== Seleccionar Motor de Base de Datos ===")
    print("Motores disponibles:")
    for i, (key, config) in enumerate(DB_ENGINES.items(), 1):
        status = "✓" if not config['requires_server'] else "⚠️ (requiere servidor)"
        print(f"{i}. {key.upper()} {status}")
    
    while True:
        try:
            choice = input("\nSelecciona el motor (1-4) [1 para SQLite]: ").strip()
            if not choice:
                choice = '1'
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(DB_ENGINES):
                selected_engine = list(DB_ENGINES.keys())[choice_idx]
                return selected_engine
            else:
                print("❌ Opción inválida. Selecciona un número del 1 al 4.")
        except ValueError:
            print("❌ Por favor ingresa un número válido.")
        except (EOFError, KeyboardInterrupt):
            print("\n⚠️  Entrada interrumpida, usando SQLite por defecto...")
            return 'sqlite'

def configurar_bd_personalizada(engine_key, usar_defaults=False):
    """Permite configurar parámetros personalizados de la BD"""
    config = DB_ENGINES[engine_key]
    print(f"\n=== Configuración de {engine_key.upper()} ===")
    
    if usar_defaults:
        # Usar valores por defecto sin pedir entrada
        bd_config = {
            'engine': config['engine'],
            'name': config['default_name']
        }
        
        if config['requires_server']:
            bd_config['host'] = 'localhost'
            bd_config['port'] = config['default_port']
            bd_config['user'] = 'asse_gestit_user'
            bd_config['password'] = 'asse_gestit_password'
        else:
            bd_config['host'] = ''
            bd_config['port'] = ''
            bd_config['user'] = ''
            bd_config['password'] = ''
        
        print(f"Usando configuración por defecto para {engine_key.upper()}:")
        print(f"  Nombre: {bd_config['name']}")
        if bd_config['host']:
            print(f"  Host: {bd_config['host']}:{bd_config['port']}")
            print(f"  Usuario: {bd_config['user']}")
    else:
        # Pedir entrada interactiva
        try:
            bd_config = {
                'engine': config['engine'],
                'name': input(f"Nombre de la BD [{config['default_name']}]: ").strip() or config['default_name']
            }
            
            if config['requires_server']:
                bd_config['host'] = input("Host [localhost]: ").strip() or 'localhost'
                bd_config['port'] = input(f"Puerto [{config['default_port']}]: ").strip() or config['default_port']
                bd_config['user'] = (
                    input("Usuario [asse_gestit_user]: ").strip()
                    or 'asse_gestit_user'
                )
                bd_config['password'] = (
                    input("Contraseña [asse_gestit_password]: ").strip()
                    or 'asse_gestit_password'
                )
            else:
                bd_config['host'] = ''
                bd_config['port'] = ''
                bd_config['user'] = ''
                bd_config['password'] = ''
        except (EOFError, KeyboardInterrupt):
            print("\n⚠️  Entrada interrumpida, usando valores por defecto...")
            return configurar_bd_personalizada(engine_key, usar_defaults=True)
    
    bd_config['options'] = '{}'
    
    return bd_config

def main():
    """Función principal para crear la BD desde cero"""
    
    print("=== Script de Creación de Base de Datos ASSE-GestACT ===")
    print("Este script soporta múltiples motores de base de datos\n")
    
    # Seleccionar motor de BD
    engine_key = seleccionar_motor_bd()
    engine_config = DB_ENGINES[engine_key]
    
    print(f"\n🔧 Motor seleccionado: {engine_key.upper()}")
    
    # Ejecutar script de inicialización específico
    init_function = globals()[engine_config['init_script']]
    if not init_function():
        print(f"❌ Error en la inicialización de {engine_key}")
        return False
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgai.settings')
    django.setup()
    
    print("\n=== Configurando Django ===")
    
    # Configurar BD personalizada
    bd_config = configurar_bd_personalizada(engine_key)
    print(f"\n📋 Configuración de BD:")
    print(f"   Motor: {bd_config['engine']}")
    print(f"   Nombre: {bd_config['name']}")
    if bd_config['host']:
        print(f"   Host: {bd_config['host']}:{bd_config['port']}")
        print(f"   Usuario: {bd_config['user']}")
    
    # 2. Crear migraciones para seteo si no existen
    print("\nCreando migraciones para la aplicación seteo...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations', 'seteo'])
    except Exception as e:
        print(f"Error al crear migraciones: {e}")
    
    # 3. Aplicar migraciones
    print("\nAplicando migraciones...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✓ Migraciones aplicadas correctamente")
    except Exception as e:
        print(f"Error al aplicar migraciones: {e}")
        return False
    
    # 4. Crear datos iniciales
    print("\nCreando datos iniciales...")
    try:
        from seteo.models import ConfiguracionSistema, Rol, Usuario
        
        # Crear configuración de BD con los parámetros seleccionados
        config_bd, created = ConfiguracionSistema.objects.get_or_create(
            nombre='configuracion_bd',
            defaults={
                'tipo': 'database',
                'valor': bd_config,
                'descripcion': f'Configuración de base de datos {engine_key.upper()}'
            }
        )
        if created:
            print(f"✓ Configuración de BD {engine_key.upper()} creada")
        else:
            # Actualizar configuración existente
            config_bd.valor = bd_config
            config_bd.descripcion = f'Configuración de base de datos {engine_key.upper()}'
            config_bd.save()
            print(f"✓ Configuración de BD {engine_key.upper()} actualizada")
        
        # Crear configuración de Keycloak por defecto
        config_keycloak, created = ConfiguracionSistema.objects.get_or_create(
            nombre='configuracion_keycloak',
            defaults={
                'tipo': 'keycloak',
                'valor': {
                    'server_url': 'http://localhost:8080',
                    'realm': 'asse-gestit',
                    'client_id': 'asse-gestit-client',
                    'client_secret': '',
                    'admin_username': 'admin',
                    'admin_password': ''
                },
                'descripcion': 'Configuración de Keycloak'
            }
        )
        if created:
            print("✓ Configuración de Keycloak creada")
        
        # Crear roles por defecto
        roles_defecto = [
            {'nombre': 'Administrador', 'descripcion': 'Acceso completo al sistema'},
            {'nombre': 'Usuario', 'descripcion': 'Acceso básico al sistema'},
            {'nombre': 'Supervisor', 'descripcion': 'Acceso de supervisión'}
        ]
        
        for rol_data in roles_defecto:
            rol, created = Rol.objects.get_or_create(
                nombre=rol_data['nombre'],
                defaults={'descripcion': rol_data['descripcion']}
            )
            if created:
                print(f"✓ Rol '{rol_data['nombre']}' creado")
        
        # Crear usuario administrador por defecto
        admin_rol = Rol.objects.get(nombre='Administrador')
        usuario_admin, created = Usuario.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@asse-gestit.local',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'is_active': True,
                'estado': 'activo'
            }
        )
        if created:
            usuario_admin.roles.add(admin_rol)
        if created:
            print("✓ Usuario administrador creado (username: admin)")
        
        print("\n=== Base de datos creada exitosamente ===")
        print("\nDatos iniciales:")
        print(f"- Configuración de BD: {engine_key.upper()} ({bd_config['name']})")
        if bd_config['host']:
            print(f"  Host: {bd_config['host']}:{bd_config['port']}")
            print(f"  Usuario: {bd_config['user']}")
        print("- Configuración de Keycloak: localhost:8080")
        print("- Roles: Administrador, Usuario, Supervisor")
        print("- Usuario admin creado")
        
        if engine_config['requires_server']:
            print(f"\n⚠️  IMPORTANTE: Para {engine_key.upper()}:")
            print(f"   1. Ejecuta el script SQL generado: init_{engine_key}.sql")
            print(f"   2. Asegúrate de que el servidor {engine_key} esté ejecutándose")
            print(f"   3. Verifica la conectividad antes de usar la aplicación")
        
        print("\nPuedes acceder a la configuración en: http://127.0.0.1:8000/seteo/base-datos/")
        
        return True
        
    except Exception as e:
        print(f"Error al crear datos iniciales: {e}")
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("\n🎉 ¡Base de datos creada correctamente!")
        sys.exit(0)
    else:
        print("\n❌ Error al crear la base de datos")
        sys.exit(1)