#!/usr/bin/env python3
"""
Script para probar actualización de computadora CON LOGS detallados.
"""
import os
import sys
import django
import logging

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgai.settings')
django.setup()

# Configurar logging para ver TODOS los mensajes
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from django.test import Client
from django.urls import reverse
from django.conf import settings
from inventario.models import (
    Computadora, Estado, TipoComputadora, Lugares, TipoNivel,
    Fabricante, Modelo, TipoGarantia, Proveedor
)
from datetime import date

print("\n" + "=" * 80)
print("PRUEBA DE ACTUALIZACIÓN DE COMPUTADORA CON LOGS DETALLADOS")
print("=" * 80)

# Permitir testserver
settings.ALLOWED_HOSTS = ['*']

# Limpiar datos anteriores
Computadora.objects.filter(numero_serie='LOG-TEST-001').delete()

# Crear datos necesarios
estado_operativo, _ = Estado.objects.get_or_create(nombre='Operativo')
estado_stock, _ = Estado.objects.get_or_create(nombre='Stock')
tipo_comp, _ = TipoComputadora.objects.get_or_create(nombre='Laptop Test')
tipo_nivel, _ = TipoNivel.objects.get_or_create(nombre='Deposito', nivel=1)
lugar, _ = Lugares.objects.get_or_create(
    nombre='Depósito Test Logs',
    tipo_nivel=tipo_nivel
)
fabricante, _ = Fabricante.objects.get_or_create(nombre='Dell Test')
modelo, _ = Modelo.objects.get_or_create(
    nombre='Latitude Test',
    fabricante=fabricante
)
tipo_garantia, _ = TipoGarantia.objects.get_or_create(nombre='Fabricante')
proveedor, _ = Proveedor.objects.get_or_create(nombre='Dell Direct')

# Crear computadora
comp = Computadora.objects.create(
    nombre='INICIAL-NOMBRE',
    estado=estado_operativo,
    lugar=lugar,
    tipo_computadora=tipo_comp,
    fabricante=fabricante,
    modelo=modelo,
    numero_serie='LOG-TEST-001',
    numero_inventario='INICIAL-INV',
    tipo_garantia=tipo_garantia,
    fecha_adquisicion=date(2024, 1, 1),
    anos_garantia=3,
    proveedor=proveedor,
    moneda='UYU',
    comentarios='Comentario ANTES de actualizar',
    valor_adquisicion=1000.00
)

print(f"\n[ANTES] Computadora creada:")
print(f"  • ID: {comp.pk}")
print(f"  • Nombre: '{comp.nombre}'")
print(f"  • Estado: '{comp.estado.nombre}'")
print(f"  • Inventario: '{comp.numero_inventario}'")
print(f"  • Valor: {comp.valor_adquisicion}")
print(f"  • Comentarios: '{comp.comentarios}'")

print("\n" + "=" * 80)
print("INICIANDO ACTUALIZACIÓN VIA POST")
print("=" * 80 + "\n")

# Cliente de test
client = Client()
url = reverse('inventario:computadora_update', kwargs={'pk': comp.pk})

# Datos para actualizar
post_data = {
    'nombre': comp.nombre,  
    'estado': estado_stock.pk,  # CAMBIO: Operativo -> Stock
    'lugar': lugar.pk,
    'tipo_computadora': tipo_comp.pk,
    'fabricante': fabricante.pk,
    'modelo': modelo.pk,
    'numero_serie': 'LOG-TEST-001',
    'numero_inventario': comp.numero_inventario,
    'proveedor': proveedor.pk,
    'tipo_garantia': tipo_garantia.pk,
    'fecha_adquisicion': '2024-01-01',
    'anos_garantia': 3,
    'valor_adquisicion': '2500.00',  # CAMBIO: 1000 -> 2500
    'moneda': 'UYU',
    'comentarios': 'COMENTARIO MODIFICADO EN EL UPDATE',  # CAMBIO
    'monitores_vinculados': [],
    'impresoras_vinculadas': [],
}

print("Datos enviados en POST:")
for key, value in post_data.items():
    if key not in ['monitores_vinculados', 'impresoras_vinculadas']:
        print(f"  • {key}: {value}")

print("\n" + "-" * 80)
print("EJECUTANDO POST...")
print("-" * 80 + "\n")

# Hacer el POST y capturar logs
response = client.post(url, post_data, follow=False)

print("\n" + "-" * 80)
print("RESPUESTA HTTP:")
print("-" * 80)
print(f"  • Status Code: {response.status_code}")
print(f"  • Redirección: {response.get('Location', 'N/A')}")

# Verificar cambios en BD
comp.refresh_from_db()

print("\n" + "=" * 80)
print("[DESPUÉS] Estado en la base de datos:")
print("=" * 80)
print(f"  • ID: {comp.pk}")
print(f"  • Nombre: '{comp.nombre}'")
print(f"  • Estado: '{comp.estado.nombre}'")
print(f"  • Inventario: '{comp.numero_inventario}'")
print(f"  • Valor: {comp.valor_adquisicion}")
print(f"  • Comentarios: '{comp.comentarios}'")

# Verificar cambios
print("\n" + "=" * 80)
print("VALIDACIÓN DE CAMBIOS:")
print("=" * 80)

cambios = []
if comp.estado.nombre == 'Stock':
    print("  ✅ Estado cambió a 'Stock'")
else:
    print(f"  ❌ Estado NO cambió (actual: '{comp.estado.nombre}')")
    cambios.append('estado')

if comp.valor_adquisicion == 2500.00:
    print("  ✅ Valor cambió a 2500.00")
else:
    print(f"  ❌ Valor NO cambió (actual: {comp.valor_adquisicion})")
    cambios.append('valor')

if comp.comentarios == 'COMENTARIO MODIFICADO EN EL UPDATE':
    print("  ✅ Comentarios cambiaron")
else:
    print(f"  ❌ Comentarios NO cambiaron (actual: '{comp.comentarios}')")
    cambios.append('comentarios')

if response.status_code == 302:
    print("  ✅ Redirigió correctamente")
else:
    print(f"  ❌ No redirigió (status: {response.status_code})")
    cambios.append('redirect')

print("\n" + "=" * 80)
if cambios:
    print("❌ FALLÓ - Campos sin actualizar:", ", ".join(cambios))
else:
    print("✅ TODO FUNCIONÓ CORRECTAMENTE")
print("=" * 80 + "\n")

# Limpiar
comp.delete()
print("✓ Datos de prueba eliminados\n")
