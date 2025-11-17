#!/usr/bin/env python
"""
Script para ejecutar automáticamente los scripts SQL de inicialización de BD
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def ejecutar_postgresql():
    """Ejecuta el script de PostgreSQL"""
    script_path = 'init_postgresql.sql'
    if not os.path.exists(script_path):
        print(f"❌ Script {script_path} no encontrado")
        return False
    
    print("🐘 Ejecutando script de PostgreSQL...")
    
    # Solicitar credenciales
    print("Ingresa las credenciales de PostgreSQL:")
    host = input("Host [localhost]: ").strip() or 'localhost'
    port = input("Puerto [5432]: ").strip() or '5432'
    user = input("Usuario [postgres]: ").strip() or 'postgres'
    
    try:
        # Ejecutar script SQL
        cmd = ['psql', '-h', host, '-p', port, '-U', user, '-f', script_path]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✓ Script de PostgreSQL ejecutado exitosamente")
        print("Salida:")
        print(result.stdout)
        
        if result.stderr:
            print("Advertencias:")
            print(result.stderr)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar script de PostgreSQL: {e}")
        print(f"Salida de error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ psql no encontrado. Asegúrate de que PostgreSQL esté instalado y en el PATH")
        return False

def ejecutar_mysql():
    """Ejecuta el script de MySQL"""
    script_path = 'init_mysql.sql'
    if not os.path.exists(script_path):
        print(f"❌ Script {script_path} no encontrado")
        return False
    
    print("🐬 Ejecutando script de MySQL...")
    
    # Solicitar credenciales
    print("Ingresa las credenciales de MySQL:")
    host = input("Host [localhost]: ").strip() or 'localhost'
    port = input("Puerto [3306]: ").strip() or '3306'
    user = input("Usuario [root]: ").strip() or 'root'
    
    try:
        # Ejecutar script SQL
        cmd = ['mysql', '-h', host, '-P', port, '-u', user, '-p']
        
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        result = subprocess.run(cmd, input=script_content, check=True, capture_output=True, text=True)
        
        print("✓ Script de MySQL ejecutado exitosamente")
        print("Salida:")
        print(result.stdout)
        
        if result.stderr:
            print("Advertencias:")
            print(result.stderr)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar script de MySQL: {e}")
        print(f"Salida de error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ mysql no encontrado. Asegúrate de que MySQL esté instalado y en el PATH")
        return False

def ejecutar_oracle():
    """Ejecuta el script de Oracle"""
    script_path = 'init_oracle.sql'
    if not os.path.exists(script_path):
        print(f"❌ Script {script_path} no encontrado")
        return False
    
    print("🔶 Ejecutando script de Oracle...")
    
    # Solicitar credenciales
    print("Ingresa las credenciales de Oracle:")
    host = input("Host [localhost]: ").strip() or 'localhost'
    port = input("Puerto [1521]: ").strip() or '1521'
    sid = input("SID [XE]: ").strip() or 'XE'
    user = input("Usuario [system]: ").strip() or 'system'
    
    try:
        # Construir string de conexión
        connect_string = f"{user}@{host}:{port}/{sid}"
        
        # Ejecutar script SQL
        cmd = ['sqlplus', connect_string, '@' + script_path]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✓ Script de Oracle ejecutado exitosamente")
        print("Salida:")
        print(result.stdout)
        
        if result.stderr:
            print("Advertencias:")
            print(result.stderr)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar script de Oracle: {e}")
        print(f"Salida de error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ sqlplus no encontrado. Asegúrate de que Oracle Client esté instalado y en el PATH")
        return False

def detectar_scripts_disponibles():
    """Detecta qué scripts SQL están disponibles"""
    scripts = {
        'postgresql': 'init_postgresql.sql',
        'mysql': 'init_mysql.sql',
        'oracle': 'init_oracle.sql'
    }
    
    disponibles = {}
    for motor, archivo in scripts.items():
        if os.path.exists(archivo):
            disponibles[motor] = archivo
    
    return disponibles

def main():
    """Función principal"""
    print("=== Ejecutor de Scripts SQL para ASSE-GestACT ===")
    print("Este script ejecuta automáticamente los scripts de inicialización de BD\n")
    
    # Detectar scripts disponibles
    scripts_disponibles = detectar_scripts_disponibles()
    
    if not scripts_disponibles:
        print("❌ No se encontraron scripts SQL de inicialización")
        print("Ejecuta primero 'python crear_bd.py' para generar los scripts")
        return False
    
    print("Scripts disponibles:")
    motores = list(scripts_disponibles.keys())
    for i, motor in enumerate(motores, 1):
        print(f"{i}. {motor.upper()} ({scripts_disponibles[motor]})")
    
    # Seleccionar motor
    while True:
        try:
            choice = input(f"\nSelecciona el motor (1-{len(motores)}): ").strip()
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(motores):
                motor_seleccionado = motores[choice_idx]
                break
            else:
                print(f"❌ Opción inválida. Selecciona un número del 1 al {len(motores)}.")
        except ValueError:
            print("❌ Por favor ingresa un número válido.")
        except KeyboardInterrupt:
            print("\n❌ Operación cancelada.")
            return False
    
    print(f"\n🔧 Ejecutando script para {motor_seleccionado.upper()}...")
    
    # Ejecutar script correspondiente
    ejecutores = {
        'postgresql': ejecutar_postgresql,
        'mysql': ejecutar_mysql,
        'oracle': ejecutar_oracle
    }
    
    if motor_seleccionado in ejecutores:
        success = ejecutores[motor_seleccionado]()
        
        if success:
            print(f"\n🎉 ¡Script de {motor_seleccionado.upper()} ejecutado correctamente!")
            print("\n📋 Próximos pasos:")
            print("1. Verifica que el servidor de BD esté ejecutándose")
            print("2. Prueba la conexión desde la aplicación Django")
            print("3. Ejecuta 'python manage.py runserver' para iniciar la aplicación")
            return True
        else:
            print(f"\n❌ Error al ejecutar script de {motor_seleccionado.upper()}")
            return False
    else:
        print(f"❌ Ejecutor no implementado para {motor_seleccionado}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)