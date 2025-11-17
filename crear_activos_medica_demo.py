#!/usr/bin/env python
"""
Script para crear activos de tecnología médica como demo
"""

import os
import sys
import django
from datetime import timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgai.settings')
django.setup()

from django.utils import timezone
from inventario.models import (
    TecnologiaMedica, TipoTecnologiaMedica, Estado, Lugares,
    Fabricante, Modelo, TipoGarantia, Proveedor, TipoNivel
)


def obtener_o_crear_tipo_nivel(nivel, nombre, requiere_codigo=False):
    """Obtener o crear un tipo de nivel asegurando consistencia"""
    existentes = list(TipoNivel.objects.filter(nivel=nivel).order_by('id'))

    if existentes:
        tipo = existentes[0]
        if len(existentes) > 1:
            print(
                f"⚠ Se encontraron {len(existentes)} tipos de nivel para el nivel {nivel}. "
                "Se utilizará el primero y se actualizarán sus datos."
            )
    else:
        tipo = TipoNivel.objects.create(
            nivel=nivel,
            nombre=nombre,
            requiere_codigo=requiere_codigo,
            descripcion='',
            activo=True
        )

    cambios = False
    if tipo.nombre != nombre:
        tipo.nombre = nombre
        cambios = True
    if tipo.requiere_codigo != requiere_codigo:
        tipo.requiere_codigo = requiere_codigo
        cambios = True
    if not tipo.activo:
        tipo.activo = True
        cambios = True

    if cambios:
        tipo.save(update_fields=['nombre', 'requiere_codigo', 'activo'])

    return tipo


def obtener_o_crear_lugar(nombre, tipo_nivel, padre=None, codigo=None, comentarios=""):
    """Crear u obtener un lugar garantizando reglas de jerarquía"""
    lugar = Lugares.objects.filter(nombre=nombre, padre=padre).first()

    if lugar:
        cambios = False

        if lugar.tipo_nivel_id != tipo_nivel.id:
            lugar.tipo_nivel = tipo_nivel
            cambios = True

        if codigo and lugar.codigo != codigo:
            lugar.codigo = codigo
            cambios = True

        if tipo_nivel.requiere_codigo and not lugar.codigo and codigo:
            lugar.codigo = codigo
            cambios = True

        if not lugar.activo:
            lugar.activo = True
            cambios = True

        if cambios:
            lugar.save()
    else:
        lugar = Lugares(
            nombre=nombre,
            tipo_nivel=tipo_nivel,
            padre=padre,
            comentarios=comentarios,
            activo=True
        )

        if tipo_nivel.requiere_codigo:
            lugar.codigo = codigo or f"AUTO-{tipo_nivel.nivel:02d}"
        elif codigo:
            lugar.codigo = codigo

        lugar.save()

    return lugar


def crear_datos_base():
    """Crear datos base necesarios"""
    print("Creando datos base...")

    # Tipos de nivel necesarios para la jerarquía básica
    tipos_nivel = {
        1: obtener_o_crear_tipo_nivel(1, 'Unidad Ejecutora', requiere_codigo=True),
        2: obtener_o_crear_tipo_nivel(2, 'Unidad Asistencial'),
        3: obtener_o_crear_tipo_nivel(3, 'Servicio'),
        4: obtener_o_crear_tipo_nivel(4, 'Área'),
    }
    
    # Estados
    estados = ['Stock', 'En Uso', 'En Mantenimiento', 'En Servicio', 'Baja Técnica']
    for nombre in estados:
        Estado.objects.get_or_create(nombre=nombre)
    
    # Lugares jerárquicos mínimos
    hospital_central = obtener_o_crear_lugar(
        nombre='Hospital Central',
        tipo_nivel=tipos_nivel[1],
        codigo='HC-001',
        comentarios='Unidad ejecutora principal'
    )

    policlinica_norte = obtener_o_crear_lugar(
        nombre='Policlínica Norte',
        tipo_nivel=tipos_nivel[1],
        codigo='PN-001',
        comentarios='Unidad ejecutora de policlínica zona norte'
    )

    policlinica_este = obtener_o_crear_lugar(
        nombre='Policlínica Este',
        tipo_nivel=tipos_nivel[1],
        codigo='PE-001',
        comentarios='Unidad ejecutora de policlínica zona este'
    )

    lugares_detalle = [
        (hospital_central, 'Hospital Central - UCI'),
        (hospital_central, 'Hospital Central - Quirófano 1'),
        (hospital_central, 'Hospital Central - Quirófano 2'),
        (hospital_central, 'Hospital Central - Cardiología'),
        (policlinica_norte, 'Policlínica Norte - Consultorios'),
        (policlinica_este, 'Policlínica Este - Emergencia'),
    ]

    for padre, nombre in lugares_detalle:
        obtener_o_crear_lugar(
            nombre=nombre,
            tipo_nivel=tipos_nivel[2],
            padre=padre
        )
    
    # Fabricantes
    fabricantes = ['Philips', 'GE Healthcare', 'Siemens', 'Mindray', 'Drager']
    for nombre in fabricantes:
        Fabricante.objects.get_or_create(nombre=nombre)
    
    # Tipos de Tecnología Médica
    tipos = [
        'Monitor de Paciente',
        'Ventilador Mecánico',
        'Desfibrilador',
        'Electrocardiografo',
        'Bomba de Infusión',
        'Oxímetro',
        'Equipo de Rayos X',
        'Ecógrafo'
    ]
    
    for nombre in tipos:
        TipoTecnologiaMedica.objects.get_or_create(nombre=nombre)
    
    # Proveedores
    proveedores = ['Biomédica SA', 'Tecnología Hospitalaria', 'MedEquip Uruguay']
    for nombre in proveedores:
        Proveedor.objects.get_or_create(nombre=nombre)
    
    # Tipos de Garantía
    TipoGarantia.objects.get_or_create(
        nombre='Fabricante',
        defaults={'descripcion': 'Garantía estándar del fabricante (12 meses)'}
    )
    TipoGarantia.objects.get_or_create(
        nombre='Extendida',
        defaults={'descripcion': 'Garantía extendida provista por el proveedor'}
    )
    
    print("✓ Datos base creados")


def crear_activos_demo():
    """Crear activos de tecnología médica demo"""
    print("\nCreando activos de tecnología médica demo...")
    
    # Obtener datos base
    estado_stock = Estado.objects.get(nombre='Stock')
    estado_uso = Estado.objects.get(nombre='En Uso')
    
    fabricantes = {f.nombre: f for f in Fabricante.objects.all()}
    tipos = {t.nombre: t for t in TipoTecnologiaMedica.objects.all()}
    garantia = TipoGarantia.objects.filter(nombre='Fabricante').first() or TipoGarantia.objects.first()
    proveedores = {p.nombre: p for p in Proveedor.objects.all()}
    proveedor_default = proveedores.get('Biomédica SA') or next(iter(proveedores.values()), None)

    if not garantia:
        raise RuntimeError('Debe existir al menos un tipo de garantía para crear los activos demo')

    if not proveedor_default:
        raise RuntimeError('Debe existir al menos un proveedor para crear los activos demo')
    
    # Crear modelos
    modelos_data = [
        ('Philips', 'IntelliVue MP60'),
        ('Philips', 'IntelliVue MP70'),
        ('GE Healthcare', 'Carescape B450'),
        ('Siemens', 'SC 9000XL'),
        ('Mindray', 'BeneView T5'),
        ('Drager', 'Infinity Delta'),
    ]
    
    modelos = {}
    for fab_nombre, modelo_nombre in modelos_data:
        modelo, created = Modelo.objects.get_or_create(
            nombre=modelo_nombre,
            fabricante=fabricantes[fab_nombre]
        )
        modelos[modelo_nombre] = modelo
        if created:
            print(f"✓ Modelo creado: {fab_nombre} {modelo_nombre}")
    
    # Crear activos demo
    activos_demo = [
        {
            'nombre': 'Monitor de Paciente UCI-001',
            'numero_serie': 'PHI-MP60-001',
            'tipo': 'Monitor de Paciente',
            'modelo': 'IntelliVue MP60',
            'lugar': 'Hospital Central - UCI',
            'estado': 'En Uso',
            'observaciones': 'Monitor principal UCI, pantalla 19 pulgadas',
            'area_aplicacion': 'UCI',
            'anos_garantia': 3,
            'frecuencia_calibracion_meses': 12,
            'frecuencia_mantenimiento_meses': 6,
            'dias_desde_calibracion': 45,
            'dias_desde_mantenimiento': 60,
            'dias_desde_adquisicion': 620,
            'clasificacion_riesgo': 'clase_iib',
            'requiere_personal_especializado': False,
            'valor_adquisicion': Decimal('18500'),
            'moneda': 'USD',
            'proveedor': 'Biomédica SA'
        },
        {
            'nombre': 'Monitor de Paciente UCI-002',
            'numero_serie': 'PHI-MP60-002',
            'tipo': 'Monitor de Paciente',
            'modelo': 'IntelliVue MP60',
            'lugar': 'Hospital Central - UCI',
            'estado': 'Stock',
            'observaciones': 'Monitor de respaldo, calibrado 10/2025',
            'area_aplicacion': 'UCI',
            'anos_garantia': 2,
            'frecuencia_calibracion_meses': 12,
            'frecuencia_mantenimiento_meses': 6,
            'dias_desde_calibracion': 90,
            'dias_desde_mantenimiento': 120,
            'dias_desde_adquisicion': 240,
            'clasificacion_riesgo': 'clase_iia',
            'requiere_personal_especializado': False,
            'valor_adquisicion': Decimal('17800'),
            'moneda': 'USD',
            'proveedor': 'Biomédica SA'
        },
        {
            'nombre': 'Monitor Cardiología CAR-001',
            'numero_serie': 'GE-B450-001',
            'tipo': 'Monitor de Paciente',
            'modelo': 'Carescape B450',
            'lugar': 'Hospital Central - Cardiología',
            'estado': 'En Uso',
            'observaciones': 'Monitor especializado para cardiología',
            'area_aplicacion': 'Cardiología',
            'anos_garantia': 3,
            'frecuencia_calibracion_meses': 12,
            'frecuencia_mantenimiento_meses': 6,
            'dias_desde_calibracion': 60,
            'dias_desde_mantenimiento': 90,
            'dias_desde_adquisicion': 480,
            'clasificacion_riesgo': 'clase_iia',
            'requiere_personal_especializado': False,
            'valor_adquisicion': Decimal('19500'),
            'moneda': 'USD',
            'proveedor': 'Tecnología Hospitalaria'
        },
        {
            'nombre': 'Ventilador Quirófano Q1-001',
            'numero_serie': 'SIE-9000-001',
            'tipo': 'Ventilador Mecánico',
            'modelo': 'SC 9000XL',
            'lugar': 'Hospital Central - Quirófano 1',
            'estado': 'En Uso',
            'observaciones': 'Ventilador de alta gama para cirugías',
            'area_aplicacion': 'Quirófano',
            'anos_garantia': 2,
            'frecuencia_calibracion_meses': 6,
            'frecuencia_mantenimiento_meses': 3,
            'dias_desde_calibracion': 30,
            'dias_desde_mantenimiento': 25,
            'dias_desde_adquisicion': 540,
            'clasificacion_riesgo': 'clase_iii',
            'requiere_personal_especializado': True,
            'valor_adquisicion': Decimal('42000'),
            'moneda': 'USD',
            'potencia': '1200 VA',
            'voltaje_operacion': '220V',
            'proveedor': 'MedEquip Uruguay'
        },
        {
            'nombre': 'Monitor Básico POL-001',
            'numero_serie': 'MIN-T5-001',
            'tipo': 'Monitor de Paciente',
            'modelo': 'BeneView T5',
            'lugar': 'Policlínica Norte - Consultorios',
            'estado': 'Stock',
            'observaciones': 'Monitor básico para consultas ambulatorias',
            'area_aplicacion': 'Consultorios',
            'anos_garantia': 2,
            'frecuencia_calibracion_meses': 12,
            'frecuencia_mantenimiento_meses': 6,
            'dias_desde_calibracion': 120,
            'dias_desde_mantenimiento': 150,
            'dias_desde_adquisicion': 300,
            'clasificacion_riesgo': 'clase_i',
            'requiere_personal_especializado': False,
            'valor_adquisicion': Decimal('9200'),
            'moneda': 'USD',
            'proveedor': 'Tecnología Hospitalaria'
        },
        {
            'nombre': 'Monitor Emergencia EMG-001',
            'numero_serie': 'DRA-DELTA-001',
            'tipo': 'Monitor de Paciente',
            'modelo': 'Infinity Delta',
            'lugar': 'Policlínica Este - Emergencia',
            'estado': 'En Mantenimiento',
            'observaciones': 'En mantenimiento preventivo, vence garantía 03/2026',
            'area_aplicacion': 'Emergencia',
            'anos_garantia': 4,
            'frecuencia_calibracion_meses': 12,
            'frecuencia_mantenimiento_meses': 6,
            'dias_desde_calibracion': 20,
            'dias_desde_mantenimiento': 5,
            'dias_desde_adquisicion': 720,
            'clasificacion_riesgo': 'clase_iib',
            'requiere_personal_especializado': True,
            'valor_adquisicion': Decimal('21500'),
            'moneda': 'USD',
            'voltaje_operacion': '220V',
            'proveedor': 'MedEquip Uruguay'
        },
    ]
    
    activos_creados = []
    
    for activo_data in activos_demo:
        # Verificar si ya existe
        if TecnologiaMedica.objects.filter(numero_serie=activo_data['numero_serie']).exists():
            print(f"⚠ Activo ya existe: {activo_data['numero_serie']}")
            continue
            
        # Crear activo
        requiere_calibracion = activo_data.get('requiere_calibracion', True)
        requiere_mantenimiento = activo_data.get('requiere_mantenimiento_preventivo', True)
        fecha_hoy = timezone.now().date()
        fecha_adquisicion = fecha_hoy - timedelta(days=activo_data.get('dias_desde_adquisicion', 365))
        fecha_ultima_calibracion = (
            fecha_hoy - timedelta(days=activo_data.get('dias_desde_calibracion', 90))
            if requiere_calibracion else None
        )
        fecha_ultimo_mantenimiento = (
            fecha_hoy - timedelta(days=activo_data.get('dias_desde_mantenimiento', 60))
            if requiere_mantenimiento else None
        )

        proveedor_equipo = proveedores.get(activo_data.get('proveedor')) or proveedor_default

        valor_adquisicion = activo_data.get('valor_adquisicion')
        if valor_adquisicion is not None and not isinstance(valor_adquisicion, Decimal):
            valor_adquisicion = Decimal(str(valor_adquisicion))

        activo = TecnologiaMedica.objects.create(
            nombre=activo_data['nombre'],
            numero_serie=activo_data['numero_serie'],
            tipo_tecnologia_medica=tipos[activo_data['tipo']],
            fabricante=modelos[activo_data['modelo']].fabricante,
            modelo=modelos[activo_data['modelo']],
            lugar=Lugares.objects.get(nombre=activo_data['lugar']),
            estado=Estado.objects.get(nombre=activo_data['estado']),
            fecha_adquisicion=fecha_adquisicion,
            comentarios=activo_data['observaciones'],
            tipo_garantia=garantia,
            proveedor=proveedor_equipo,
            numero_inventario=f"TM-{len(activos_creados)+1:04d}",
            anos_garantia=activo_data.get('anos_garantia', 2),
            valor_adquisicion=valor_adquisicion,
            moneda=activo_data.get('moneda', 'USD'),
            requiere_calibracion=requiere_calibracion,
            frecuencia_calibracion_meses=(
                activo_data.get('frecuencia_calibracion_meses', 12)
                if requiere_calibracion else None
            ),
            fecha_ultima_calibracion=fecha_ultima_calibracion,
            requiere_mantenimiento_preventivo=requiere_mantenimiento,
            frecuencia_mantenimiento_meses=(
                activo_data.get('frecuencia_mantenimiento_meses', 6)
                if requiere_mantenimiento else None
            ),
            fecha_ultimo_mantenimiento=fecha_ultimo_mantenimiento,
            clasificacion_riesgo=activo_data.get('clasificacion_riesgo', 'clase_iia'),
            area_aplicacion=activo_data.get('area_aplicacion'),
            requiere_personal_especializado=activo_data.get('requiere_personal_especializado', False),
            voltaje_operacion=activo_data.get('voltaje_operacion'),
            potencia=activo_data.get('potencia')
        )
        
        activos_creados.append(activo)
        print(f"✓ Creado: {activo.nombre} ({activo.numero_serie})")
    
    print(f"\n✓ {len(activos_creados)} activos de tecnología médica creados")
    return activos_creados


def main():
    print("=== CREACIÓN DE ACTIVOS TECNOLOGÍA MÉDICA DEMO ===\n")
    
    try:
        crear_datos_base()
        activos = crear_activos_demo()
        
        print("\n=== RESUMEN ===")
        print(f"✓ {len(activos)} activos de tecnología médica disponibles")
        print("\nTipos de equipos demo creados:")
        print("- Monitores de paciente (UCI, Cardiología, Emergencia)")
        print("- Ventilador mecánico (Quirófano)")
        print("- Equipos en diferentes estados (Stock, En Uso, Mantenimiento)")
        print("\nAhora puedes:")
        print("1. Ver los activos en el dashboard de Tecnología Médica")
        print("2. Agregarlos al carrito de servicio")
        print("3. Generar remitos de servicio en PDF")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()