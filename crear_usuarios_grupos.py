#!/usr/bin/env python
"""
Script para crear usuarios específicos con sus grupos asignados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgai.settings')
django.setup()

from django.contrib.auth.models import User, Group


def crear_grupos():
    """Crear los grupos necesarios si no existen"""
    grupos = ['Activos Informáticos', 'Tecnología Médica']
    
    for nombre_grupo in grupos:
        grupo, created = Group.objects.get_or_create(name=nombre_grupo)
        if created:
            print(f"✓ Grupo '{nombre_grupo}' creado")
        else:
            print(f"✓ Grupo '{nombre_grupo}' ya existe")


def crear_usuario_ti():
    """Crear usuario para Activos Informáticos"""
    username = 'admin_ti'
    password = 'ti123456'
    
    # Crear o actualizar usuario
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': 'admin.ti@asse.com.uy',
            'first_name': 'Administrador',
            'last_name': 'TI',
            'is_staff': False,
            'is_superuser': False,
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"✓ Usuario '{username}' creado")
    else:
        print(f"✓ Usuario '{username}' ya existe")
    
    # Asignar al grupo
    grupo = Group.objects.get(name='Activos Informáticos')
    user.groups.clear()
    user.groups.add(grupo)
    
    print(f"✓ Usuario '{username}' asignado al grupo 'Activos Informáticos'")
    print(f"  Credenciales: {username} / {password}")
    
    return user


def crear_usuario_medica():
    """Crear usuario para Tecnología Médica"""
    username = 'admin_medica'
    password = 'medica123456'
    
    # Crear o actualizar usuario
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': 'admin.medica@asse.com.uy',
            'first_name': 'Administrador',
            'last_name': 'Médica',
            'is_staff': False,
            'is_superuser': False,
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"✓ Usuario '{username}' creado")
    else:
        print(f"✓ Usuario '{username}' ya existe")
    
    # Asignar al grupo
    grupo = Group.objects.get(name='Tecnología Médica')
    user.groups.clear()
    user.groups.add(grupo)
    
    print(f"✓ Usuario '{username}' asignado al grupo 'Tecnología Médica'")
    print(f"  Credenciales: {username} / {password}")
    
    return user


def main():
    print("=== CREACIÓN DE USUARIOS POR GRUPO ===\n")
    
    try:
        # Crear grupos
        print("1. Creando grupos...")
        crear_grupos()
        print()
        
        # Crear usuarios
        print("2. Creando usuarios...")
        crear_usuario_ti()
        print()
        crear_usuario_medica()
        print()
        
        print("=== RESUMEN ===")
        print("✓ Usuarios creados exitosamente")
        print("\nCredenciales de acceso:")
        print("- Activos Informáticos: admin_ti / ti123456")
        print("- Tecnología Médica: admin_medica / medica123456")
        print("\nCada usuario será redirigido automáticamente a su dashboard correspondiente.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()