#!/usr/bin/env python3
"""
Script para probar manualmente el flujo de actualización de computadoras.
Simula el comportamiento del navegador al editar y guardar.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgai.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from inventario.models import (
    Computadora, Estado, TipoComputadora, Lugares, TipoNivel,
    Fabricante, Modelo, TipoGarantia, Proveedor
)
from datetime import date

# Crear datos de prueba
print("=" * 80)
print("PRUEBA MANUAL DE ACTUALIZACIÓN DE COMPUTADORA")
print("=" * 80)

# Limpiar datos anteriores
Computadora.objects.filter(numero_serie='TEST-MANUAL-001').delete()

# Crear datos necesarios
estado_operativo, _ = Estado.objects.get_or_create(nombre='Operativo')
estado_stock, _ = Estado.objects.get_or_create(nombre='Stock')
tipo_comp, _ = TipoComputadora.objects.get_or_create(nombre='Desktop Test')
tipo_nivel, _ = TipoNivel.objects.get_or_create(nombre='Deposito', nivel=1)
lugar, _ = Lugares.objects.get_or_create(
    nombre='Depósito Test',
    tipo_nivel=tipo_nivel
)
fabricante, _ = Fabricante.objects.get_or_create(nombre='HP Test')
modelo, _ = Modelo.objects.get_or_create(
    nombre='EliteDesk Test',
    fabricante=fabricante
)
tipo_garantia, _ = TipoGarantia.objects.get_or_create(nombre='Fabricante')
proveedor, _ = Proveedor.objects.get_or_create(nombre='TechSupply Test')

# Crear computadora inicial
comp = Computadora.objects.create(
    nombre='TEST-OLD-NAME',
    estado=estado_operativo,
    lugar=lugar,
    tipo_computadora=tipo_comp,
    fabricante=fabricante,
    modelo=modelo,
    numero_serie='TEST-MANUAL-001',
    numero_inventario='TEST-OLD-INV',
    tipo_garantia=tipo_garantia,
    fecha_adquisicion=date(2024, 1, 1),
    anos_garantia=3,
    proveedor=proveedor,
    moneda='UYU',
    comentarios='Comentario inicial'
)

print(f"\n✓ Computadora creada:")
print(f"  ID: {comp.pk}")
print(f"  Nombre: {comp.nombre}")
print(f"  Estado: {comp.estado.nombre}")
print(f"  Número inventario: {comp.numero_inventario}")
print(f"  Comentarios: {comp.comentarios}")

# Simular actualización via POST
client = Client()
url = reverse('inventario:computadora_update', kwargs={'pk': comp.pk})

print(f"\n→ Simulando POST a: {url}")

# Usar follow=True para seguir redirecciones
post_data = {
    'nombre': comp.nombre,  # Mantener nombre generado
    'estado': estado_stock.pk,  # Cambiar a Stock
    'lugar': lugar.pk,
    'tipo_computadora': tipo_comp.pk,
    'fabricante': fabricante.pk,
    'modelo': modelo.pk,
    'numero_serie': 'TEST-MANUAL-001',
    'numero_inventario': comp.numero_inventario,  # Mantener inventario
    'proveedor': proveedor.pk,
    'tipo_garantia': tipo_garantia.pk,
    'fecha_adquisicion': '2024-01-01',
    'anos_garantia': 3,
    'valor_adquisicion': '1500.00',  # NUEVO
    'moneda': 'UYU',
    'comentarios': 'COMENTARIO ACTUALIZADO',  # NUEVO
    'monitores_vinculados': [],
    'impresoras_vinculadas': [],
}

# Deshabilitar el check de ALLOWED_HOSTS para testing
from django.conf import settings
settings.ALLOWED_HOSTS = ['*']

response = client.post(url, post_data, follow=False)

print(f"\n→ Respuesta HTTP: {response.status_code}")
print(f"→ Redirección: {response.get('Location', 'N/A')}")

# Verificar cambios en la BD
comp.refresh_from_db()

print(f"\n✓ Computadora después de actualizar:")
print(f"  ID: {comp.pk}")
print(f"  Nombre: {comp.nombre}")
print(f"  Estado: {comp.estado.nombre}")
print(f"  Número inventario: {comp.numero_inventario}")
print(f"  Valor adquisición: {comp.valor_adquisicion}")
print(f"  Comentarios: {comp.comentarios}")

# Validar resultados
errores = []

if comp.estado.nombre != 'Stock':
    errores.append(f"❌ Estado no cambió (esperado: Stock, actual: {comp.estado.nombre})")
else:
    print("\n✅ Estado actualizado correctamente a 'Stock'")

if comp.valor_adquisicion != 1500.00:
    errores.append(f"❌ Valor no cambió (esperado: 1500.00, actual: {comp.valor_adquisicion})")
else:
    print("✅ Valor de adquisición actualizado correctamente")

if comp.comentarios != 'COMENTARIO ACTUALIZADO':
    errores.append(f"❌ Comentarios no cambiaron (esperado: 'COMENTARIO ACTUALIZADO', actual: '{comp.comentarios}')")
else:
    print("✅ Comentarios actualizados correctamente")

if response.status_code != 302:
    errores.append(f"❌ No redirigió (código: {response.status_code})")
else:
    print("✅ Redirigió correctamente")

# Resumen
print("\n" + "=" * 80)
if errores:
    print("❌ PRUEBA FALLIDA\n")
    for error in errores:
        print(error)
else:
    print("✅ PRUEBA EXITOSA - Todos los cambios se guardaron correctamente")
print("=" * 80)

# Limpiar
comp.delete()
print("\n✓ Datos de prueba eliminados")
