#!/usr/bin/env python
"""
Script de gestión de usuarios y grupos para ASSE-GestACT
Permite crear usuarios y asignarlos a grupos (Activos Informáticos o Tecnología Médica)
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgai.settings')
django.setup()

from django.contrib.auth.models import User, Group


def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "="*60)
    print("    GESTIÓN DE USUARIOS Y GRUPOS - ASSE-GestACT")
    print("="*60)
    print("\n1. Crear nuevo usuario")
    print("2. Asignar usuario a grupo")
    print("3. Listar usuarios y sus grupos")
    print("4. Listar grupos disponibles")
    print("5. Cambiar grupo de un usuario")
    print("6. Eliminar usuario de grupo")
    print("7. Salir")
    print("\n" + "-"*60)


def crear_usuario():
    """Crea un nuevo usuario"""
    print("\n--- CREAR NUEVO USUARIO ---")
    username = input("Nombre de usuario: ").strip()
    
    if User.objects.filter(username=username).exists():
        print(f"❌ El usuario '{username}' ya existe.")
        return
    
    email = input("Email (opcional): ").strip()
    first_name = input("Nombre (opcional): ").strip()
    last_name = input("Apellido (opcional): ").strip()
    password = input("Contraseña: ").strip()
    
    user = User.objects.create_user(
        username=username,
        email=email or '',
        password=password,
        first_name=first_name or '',
        last_name=last_name or ''
    )
    
    print(f"\n✓ Usuario '{username}' creado exitosamente")
    
    # Preguntar si desea asignar a un grupo
    asignar = input("\n¿Desea asignar a un grupo ahora? (s/n): ").strip().lower()
    if asignar == 's':
        asignar_grupo(user)


def asignar_grupo(user=None):
    """Asigna un usuario a un grupo"""
    print("\n--- ASIGNAR USUARIO A GRUPO ---")
    
    if user is None:
        username = input("Nombre de usuario: ").strip()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            print(f"❌ El usuario '{username}' no existe.")
            return
    
    print("\nGrupos disponibles:")
    print("1. Activos Informáticos (TI)")
    print("2. Tecnología Médica")
    
    opcion = input("\nSeleccione grupo (1 o 2): ").strip()
    
    if opcion == '1':
        grupo_nombre = 'Activos Informáticos'
    elif opcion == '2':
        grupo_nombre = 'Tecnología Médica'
    else:
        print("❌ Opción inválida")
        return
    
    try:
        grupo = Group.objects.get(name=grupo_nombre)
        user.groups.add(grupo)
        print(f"\n✓ Usuario '{user.username}' asignado al grupo '{grupo_nombre}'")
    except Group.DoesNotExist:
        print(f"❌ El grupo '{grupo_nombre}' no existe")


def listar_usuarios():
    """Lista todos los usuarios y sus grupos"""
    print("\n--- USUARIOS Y GRUPOS ---\n")
    usuarios = User.objects.all().order_by('username')
    
    if not usuarios:
        print("No hay usuarios en el sistema")
        return
    
    print(f"{'Usuario':<20} {'Nombre completo':<30} {'Grupos':<30}")
    print("-" * 80)
    
    for user in usuarios:
        grupos = ', '.join([g.name for g in user.groups.all()]) or 'Sin grupo'
        nombre_completo = user.get_full_name() or '-'
        print(f"{user.username:<20} {nombre_completo:<30} {grupos:<30}")
    
    print(f"\nTotal: {usuarios.count()} usuarios")


def listar_grupos():
    """Lista todos los grupos y cantidad de usuarios"""
    print("\n--- GRUPOS DISPONIBLES ---\n")
    grupos = Group.objects.all().order_by('name')
    
    if not grupos:
        print("No hay grupos en el sistema")
        return
    
    print(f"{'Grupo':<30} {'Usuarios':<10}")
    print("-" * 40)
    
    for grupo in grupos:
        cantidad = grupo.user_set.count()
        print(f"{grupo.name:<30} {cantidad:<10}")
    
    print(f"\nTotal: {grupos.count()} grupos")


def cambiar_grupo():
    """Cambia el grupo de un usuario"""
    print("\n--- CAMBIAR GRUPO DE USUARIO ---")
    
    username = input("Nombre de usuario: ").strip()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ El usuario '{username}' no existe.")
        return
    
    grupos_actuales = list(user.groups.all())
    if grupos_actuales:
        print(f"\nGrupos actuales: {', '.join([g.name for g in grupos_actuales])}")
    else:
        print("\nEl usuario no pertenece a ningún grupo")
    
    print("\nNuevos grupos disponibles:")
    print("1. Activos Informáticos (TI)")
    print("2. Tecnología Médica")
    print("3. Ninguno (limpiar grupos)")
    
    opcion = input("\nSeleccione nueva asignación (1, 2 o 3): ").strip()
    
    # Limpiar grupos actuales
    user.groups.clear()
    
    if opcion == '1':
        grupo = Group.objects.get(name='Activos Informáticos')
        user.groups.add(grupo)
        print(f"\n✓ Usuario '{username}' ahora está en 'Activos Informáticos'")
    elif opcion == '2':
        grupo = Group.objects.get(name='Tecnología Médica')
        user.groups.add(grupo)
        print(f"\n✓ Usuario '{username}' ahora está en 'Tecnología Médica'")
    elif opcion == '3':
        print(f"\n✓ Grupos eliminados para el usuario '{username}'")
    else:
        print("❌ Opción inválida")


def eliminar_de_grupo():
    """Elimina un usuario de todos sus grupos"""
    print("\n--- ELIMINAR USUARIO DE GRUPOS ---")
    
    username = input("Nombre de usuario: ").strip()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ El usuario '{username}' no existe.")
        return
    
    grupos_actuales = list(user.groups.all())
    if not grupos_actuales:
        print(f"\nEl usuario '{username}' no pertenece a ningún grupo")
        return
    
    print(f"\nGrupos actuales: {', '.join([g.name for g in grupos_actuales])}")
    confirmar = input("\n¿Confirma eliminar de todos los grupos? (s/n): ").strip().lower()
    
    if confirmar == 's':
        user.groups.clear()
        print(f"\n✓ Usuario '{username}' eliminado de todos los grupos")
    else:
        print("Operación cancelada")


def main():
    """Función principal"""
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == '1':
            crear_usuario()
        elif opcion == '2':
            asignar_grupo()
        elif opcion == '3':
            listar_usuarios()
        elif opcion == '4':
            listar_grupos()
        elif opcion == '5':
            cambiar_grupo()
        elif opcion == '6':
            eliminar_de_grupo()
        elif opcion == '7':
            print("\n¡Hasta luego!")
            sys.exit(0)
        else:
            print("\n❌ Opción inválida. Intente nuevamente.")
        
        input("\nPresione Enter para continuar...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

