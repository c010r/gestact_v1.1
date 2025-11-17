import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgai.settings')
django.setup()

from inventario.forms import ComputadoraForm
from inventario.models import *

print("=" * 80)
print("PRUEBA DE VALIDACIÓN DEL FORMULARIO DE COMPUTADORA")
print("=" * 80)

# Obtener datos de prueba
try:
    tipo_comp = TipoComputadora.objects.first()
    estado = Estado.objects.first()
    lugar = Lugares.objects.first()
    fabricante = Fabricante.objects.first()
    modelo = Modelo.objects.filter(fabricante=fabricante).first() if fabricante else None
    proveedor = Proveedor.objects.first()
    tipo_garantia = TipoGarantia.objects.first()
    
    print("\n✓ Datos de prueba obtenidos:")
    print(f"  - Tipo Computadora: {tipo_comp}")
    print(f"  - Estado: {estado}")
    print(f"  - Lugar: {lugar}")
    print(f"  - Fabricante: {fabricante}")
    print(f"  - Modelo: {modelo}")
    print(f"  - Proveedor: {proveedor}")
    print(f"  - Tipo Garantía: {tipo_garantia}")
    
    if not all([tipo_comp, estado, lugar, fabricante, modelo, tipo_garantia]):
        print("\n❌ ERROR: Faltan datos maestros en la base de datos")
        print("   Por favor, crea los registros necesarios primero.")
        exit(1)
    
    # Crear datos de formulario
    form_data = {
        'nombre': 'Computadora de Prueba',
        'tipo_computadora': tipo_comp.id,
        'estado': estado.id,
        'lugar': lugar.id,
        'fabricante': fabricante.id,
        'modelo': modelo.id,
        'numero_serie': 'TEST-12345',
        'numero_inventario': '001-2025-TEST',
        'proveedor': proveedor.id if proveedor else '',
        'tipo_garantia': tipo_garantia.id,
        'fecha_adquisicion': '2025-01-15',
        'anos_garantia': 3,
        'valor_adquisicion': 1500.00,
    }
    
    print("\n" + "=" * 80)
    print("VALIDANDO FORMULARIO...")
    print("=" * 80)
    
    form = ComputadoraForm(data=form_data)
    
    if form.is_valid():
        print("\n✅ FORMULARIO VÁLIDO")
        print("\nDatos limpios:")
        for key, value in form.cleaned_data.items():
            print(f"  - {key}: {value}")
    else:
        print("\n❌ FORMULARIO INVÁLIDO")
        print("\nErrores encontrados:")
        for field, errors in form.errors.items():
            print(f"  - {field}:")
            for error in errors:
                print(f"      * {error}")
    
    print("\n" + "=" * 80)
    print("CAMPOS REQUERIDOS DEL FORMULARIO:")
    print("=" * 80)
    for field_name, field in form.fields.items():
        required_marker = "✓ REQUERIDO" if field.required else "  opcional"
        print(f"  [{required_marker}] {field_name}")

except Exception as e:
    print(f"\n❌ ERROR INESPERADO: {e}")
    import traceback
    traceback.print_exc()
