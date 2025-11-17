#!/usr/bin/env python
"""
Crear tokens de autenticación para usuarios existentes
Utilidad para generar tokens de API para los usuarios del sistema
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgai.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


def crear_token_usuario(username):
    """Crear token para un usuario específico"""
    try:
        user = User.objects.get(username=username)
        token, created = Token.objects.get_or_create(user=user)
        if created:
            print(f"✓ Token creado para '{username}': {token.key}")
        else:
            print(f"✓ Token existente para '{username}': {token.key}")
        return token.key
    except User.DoesNotExist:
        print(f"❌ Usuario '{username}' no encontrado")
        return None


def crear_tokens_todos():
    """Crear tokens para todos los usuarios"""
    users = User.objects.all()
    if not users:
        print("No hay usuarios en el sistema")
        return
    
    print(f"Creando tokens para {users.count()} usuarios...\n")
    
    for user in users:
        token, created = Token.objects.get_or_create(user=user)
        status = "nuevo" if created else "existente"
        print(f"{user.username}: {token.key} ({status})")
    
    print(f"\n✓ Procesados {users.count()} usuarios")


def main():
    print("=== GESTIÓN DE TOKENS DE API ===\n")
    print("1. Crear token para usuario específico")
    print("2. Crear tokens para todos los usuarios")
    print("3. Listar tokens existentes")
    print("4. Salir")
    
    opcion = input("\nSeleccione opción (1-4): ").strip()
    
    if opcion == '1':
        username = input("Nombre de usuario: ").strip()
        crear_token_usuario(username)
    elif opcion == '2':
        crear_tokens_todos()
    elif opcion == '3':
        tokens = Token.objects.select_related('user').all()
        print(f"\nTokens existentes ({tokens.count()}):")
        for token in tokens:
            print(f"{token.user.username}: {token.key}")
    elif opcion == '4':
        print("Saliendo...")
    else:
        print("❌ Opción inválida")


if __name__ == '__main__':
    main()