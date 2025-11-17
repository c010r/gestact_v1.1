import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgai.settings')
django.setup()

from inventario.models import (
    TipoComputadora, Estado, Fabricante, Modelo, 
    Proveedor, TipoGarantia, TipoImpresora, TipoMonitor
)

print("=" * 80)
print("CREANDO DATOS MAESTROS PARA EL SISTEMA")
print("=" * 80)

# 1. Crear Estados
print("\n1. Creando Estados...")
estados = [
    {'nombre': 'Operativo', 'comentarios': 'Dispositivo en funcionamiento normal'},
    {'nombre': 'En reparación', 'comentarios': 'Dispositivo en proceso de reparación'},
    {'nombre': 'Fuera de servicio', 'comentarios': 'Dispositivo no funcional'},
    {'nombre': 'Stock', 'comentarios': 'Dispositivo disponible en stock'},
    {'nombre': 'Dado de baja', 'comentarios': 'Dispositivo retirado del inventario'},
]
for estado_data in estados:
    estado, created = Estado.objects.get_or_create(
        nombre=estado_data['nombre'],
        defaults={'comentarios': estado_data['comentarios']}
    )
    print(f"   {'✓ Creado' if created else '- Ya existe'}: {estado.nombre}")

# 2. Crear Tipos de Garantía
print("\n2. Creando Tipos de Garantía...")
tipos_garantia = [
    {'nombre': 'Fabricante', 'descripcion': 'Garantía del fabricante original'},
    {'nombre': 'Proveedor', 'descripcion': 'Garantía extendida por proveedor'},
    {'nombre': 'Sin garantía', 'descripcion': 'Equipo sin cobertura de garantía'},
]
for tipo_data in tipos_garantia:
    tipo, created = TipoGarantia.objects.get_or_create(
        nombre=tipo_data['nombre'],
        defaults={'descripcion': tipo_data['descripcion']}
    )
    print(f"   {'✓ Creado' if created else '- Ya existe'}: {tipo.nombre}")

# 3. Crear Fabricantes
print("\n3. Creando Fabricantes...")
fabricantes_data = [
    {'nombre': 'HP', 'comentarios': 'Hewlett-Packard'},
    {'nombre': 'Dell', 'comentarios': 'Dell Technologies'},
    {'nombre': 'Lenovo', 'comentarios': 'Lenovo Group Limited'},
    {'nombre': 'ASUS', 'comentarios': 'ASUSTeK Computer Inc.'},
    {'nombre': 'Acer', 'comentarios': 'Acer Inc.'},
    {'nombre': 'Samsung', 'comentarios': 'Samsung Electronics'},
    {'nombre': 'LG', 'comentarios': 'LG Electronics'},
    {'nombre': 'Canon', 'comentarios': 'Canon Inc.'},
    {'nombre': 'Epson', 'comentarios': 'Seiko Epson Corporation'},
]
fabricantes = {}
for fab_data in fabricantes_data:
    fab, created = Fabricante.objects.get_or_create(
        nombre=fab_data['nombre'],
        defaults={'comentarios': fab_data['comentarios']}
    )
    fabricantes[fab.nombre] = fab
    print(f"   {'✓ Creado' if created else '- Ya existe'}: {fab.nombre}")

# 4. Crear Tipos de Computadora
print("\n4. Creando Tipos de Computadora...")
tipos_comp = [
    {'nombre': 'Desktop', 'comentarios': 'Computadora de escritorio'},
    {'nombre': 'Laptop', 'comentarios': 'Computadora portátil'},
    {'nombre': 'All-in-One', 'comentarios': 'Computadora todo en uno'},
    {'nombre': 'Workstation', 'comentarios': 'Estación de trabajo profesional'},
    {'nombre': 'Mini PC', 'comentarios': 'Computadora compacta'},
]
for tipo_data in tipos_comp:
    tipo, created = TipoComputadora.objects.get_or_create(
        nombre=tipo_data['nombre'],
        defaults={'comentarios': tipo_data['comentarios']}
    )
    print(f"   {'✓ Creado' if created else '- Ya existe'}: {tipo.nombre}")

# 5. Crear Modelos de ejemplo
print("\n5. Creando Modelos de ejemplo...")
modelos_data = [
    {'fabricante': 'HP', 'nombre': 'EliteDesk 800 G6', 'tipo': 'Desktop'},
    {'fabricante': 'HP', 'nombre': 'ProBook 450 G8', 'tipo': 'Laptop'},
    {'fabricante': 'Dell', 'nombre': 'OptiPlex 7090', 'tipo': 'Desktop'},
    {'fabricante': 'Dell', 'nombre': 'Latitude 5520', 'tipo': 'Laptop'},
    {'fabricante': 'Lenovo', 'nombre': 'ThinkCentre M90a', 'tipo': 'All-in-One'},
    {'fabricante': 'Lenovo', 'nombre': 'ThinkPad E15', 'tipo': 'Laptop'},
    {'fabricante': 'ASUS', 'nombre': 'VivoBook 15', 'tipo': 'Laptop'},
    {'fabricante': 'Acer', 'nombre': 'Aspire 5', 'tipo': 'Laptop'},
]
for modelo_data in modelos_data:
    fab = fabricantes.get(modelo_data['fabricante'])
    if fab:
        modelo, created = Modelo.objects.get_or_create(
            fabricante=fab,
            nombre=modelo_data['nombre'],
            defaults={'comentarios': f"Modelo {modelo_data['tipo']}"}
        )
        print(f"   {'✓ Creado' if created else '- Ya existe'}: {fab.nombre} {modelo.nombre}")

# 6. Crear Tipos de Impresora
print("\n6. Creando Tipos de Impresora...")
tipos_impresora = [
    {'nombre': 'Láser', 'comentarios': 'Impresora láser monocromática o color'},
    {'nombre': 'Inyección de tinta', 'comentarios': 'Impresora de tinta'},
    {'nombre': 'Multifuncional', 'comentarios': 'Impresora, escáner, copiadora'},
    {'nombre': 'Matricial', 'comentarios': 'Impresora de matriz de puntos'},
]
for tipo_data in tipos_impresora:
    tipo, created = TipoImpresora.objects.get_or_create(
        nombre=tipo_data['nombre'],
        defaults={'comentarios': tipo_data['comentarios']}
    )
    print(f"   {'✓ Creado' if created else '- Ya existe'}: {tipo.nombre}")

# 7. Crear Tipos de Monitor
print("\n7. Creando Tipos de Monitor...")
tipos_monitor = [
    {'nombre': 'LED', 'comentarios': 'Monitor con retroiluminación LED'},
    {'nombre': 'LCD', 'comentarios': 'Monitor de cristal líquido'},
    {'nombre': 'OLED', 'comentarios': 'Monitor con diodos orgánicos'},
]
for tipo_data in tipos_monitor:
    tipo, created = TipoMonitor.objects.get_or_create(
        nombre=tipo_data['nombre'],
        defaults={'comentarios': tipo_data['comentarios']}
    )
    print(f"   {'✓ Creado' if created else '- Ya existe'}: {tipo.nombre}")

# 8. Crear Proveedores
print("\n8. Creando Proveedores...")
proveedores = [
    {'nombre': 'TechSupply S.A.'},
    {'nombre': 'InfoSolutions'},
]
for prov_data in proveedores:
    prov, created = Proveedor.objects.get_or_create(
        nombre=prov_data['nombre']
    )
    print(f"   {'✓ Creado' if created else '- Ya existe'}: {prov.nombre}")

print("\n" + "=" * 80)
print("✅ DATOS MAESTROS CREADOS EXITOSAMENTE")
print("=" * 80)

# Mostrar resumen
print("\nResumen de datos creados:")
print(f"  - Estados: {Estado.objects.count()}")
print(f"  - Tipos de Garantía: {TipoGarantia.objects.count()}")
print(f"  - Fabricantes: {Fabricante.objects.count()}")
print(f"  - Tipos de Computadora: {TipoComputadora.objects.count()}")
print(f"  - Modelos: {Modelo.objects.count()}")
print(f"  - Tipos de Impresora: {TipoImpresora.objects.count()}")
print(f"  - Tipos de Monitor: {TipoMonitor.objects.count()}")
print(f"  - Proveedores: {Proveedor.objects.count()}")

print("\n¡Ahora puedes crear y editar dispositivos!")
