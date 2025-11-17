from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import (
    Computadora,
    Impresora,
    Monitor,
    Estado,
    Lugares,
    Factura,
    FacturaActivo,
    Insumo,
)
from .utils_facturacion import generar_factura_pdf

TIPO_MODEL_MAP = {
    'computadora': Computadora,
    'impresora': Impresora,
    'monitor': Monitor,
}

ESTADOS_PERMITIDOS = {'stock', 'en stock'}
ESTADOS_COMPATIBLES = {'almacen', 'en almacen'}
CARRO_SESSION_KEY = 'facturacion_carrito'


def _ensure_carrito(request: HttpRequest) -> Dict[str, Any]:
    request.session.setdefault(CARRO_SESSION_KEY, {
        'items': {},
        'lugar_destino_id': None,
        'observaciones': '',
    })
    return request.session[CARRO_SESSION_KEY]


def _serialize_activo(tipo: str, activo: Any) -> Dict[str, Any]:
    return {
        'id': activo.pk,
        'tipo': tipo,
        'nombre': getattr(activo, 'nombre', ''),
        'numero_serie': getattr(activo, 'numero_serie', ''),
        'estado': getattr(activo.estado, 'nombre', ''),
        'lugar': getattr(activo.lugar, 'nombre', ''),
    }


def _guardar_sesion(request: HttpRequest) -> None:
    request.session.modified = True


@csrf_exempt
@require_POST
def agregar_activo(request: HttpRequest) -> JsonResponse:
    tipo = request.POST.get('tipo_activo')
    activo_id = request.POST.get('activo_id')

    if not tipo or not activo_id:
        return JsonResponse({'success': False, 'error': 'Datos incompletos.'}, status=400)

    if tipo not in TIPO_MODEL_MAP:
        return JsonResponse({'success': False, 'error': 'Tipo de activo inválido.'}, status=400)

    try:
        activo = TIPO_MODEL_MAP[tipo].objects.select_related('estado', 'lugar').get(pk=activo_id)
    except TIPO_MODEL_MAP[tipo].DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Activo no encontrado.'}, status=404)

    estado_nombre = getattr(activo.estado, 'nombre', '').lower()
    if estado_nombre in ESTADOS_COMPATIBLES:
        estado_nombre = estado_nombre.replace('almacen', 'stock')

    if estado_nombre not in ESTADOS_PERMITIDOS:
        return JsonResponse({'success': False, 'error': 'Solo se pueden seleccionar activos en Stock.'}, status=400)

    carrito = _ensure_carrito(request)
    carrito.setdefault('items', {})
    carrito['items'].setdefault(tipo, {})

    if str(activo.pk) in carrito['items'][tipo]:
        return JsonResponse({'success': False, 'error': 'El activo ya está en la lista.'}, status=400)

    carrito['items'][tipo][str(activo.pk)] = _serialize_activo(tipo, activo)
    _guardar_sesion(request)

    return JsonResponse({'success': True, 'item': carrito['items'][tipo][str(activo.pk)]})


@csrf_exempt
@require_POST
def remover_activo(request: HttpRequest) -> JsonResponse:
    tipo = request.POST.get('tipo_activo')
    activo_id = request.POST.get('activo_id')

    carrito = _ensure_carrito(request)
    items_tipo = carrito.get('items', {}).get(tipo, {})

    if activo_id in items_tipo:
        del items_tipo[activo_id]
        if not items_tipo:
            carrito['items'].pop(tipo, None)
        _guardar_sesion(request)
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'El activo no está en el carrito.'}, status=404)


@require_GET
def obtener_carrito(request: HttpRequest) -> JsonResponse:
    carrito = _ensure_carrito(request)
    return JsonResponse({'success': True, 'carrito': carrito})


@csrf_exempt
@require_POST
def actualizar_carrito(request: HttpRequest) -> JsonResponse:
    carrito = _ensure_carrito(request)
    carrito['observaciones'] = request.POST.get('observaciones', '')
    carrito['lugar_destino_id'] = request.POST.get('lugar_destino_id')
    _guardar_sesion(request)
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
def limpiar_carrito(request: HttpRequest) -> JsonResponse:
    request.session[CARRO_SESSION_KEY] = {'items': {}, 'lugar_destino_id': None, 'observaciones': ''}
    _guardar_sesion(request)
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
def emitir_factura(request: HttpRequest) -> HttpResponse:
    carrito = _ensure_carrito(request)
    items = carrito.get('items', {})

    if not items:
        return JsonResponse({'success': False, 'error': 'El carrito está vacío.'}, status=400)

    lugar_destino_id = carrito.get('lugar_destino_id') or request.POST.get('lugar_destino_id')
    if not lugar_destino_id:
        return JsonResponse({'success': False, 'error': 'Debe seleccionar un lugar de destino.'}, status=400)

    try:
        lugar_destino = Lugares.objects.get(pk=lugar_destino_id)
    except Lugares.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lugar de destino inválido.'}, status=404)

    estado_stock = Estado.objects.filter(nombre__iexact='stock').first()
    if not estado_stock:
        return JsonResponse({'success': False, 'error': 'No existe el estado Stock configurado.'}, status=500)

    observaciones = carrito.get('observaciones', '')

    try:
        with transaction.atomic():
            factura = Factura.objects.create(
                lugar_destino=lugar_destino,
                observaciones=observaciones,
            )

            toner_por_insumo: Dict[int, Dict[str, Any]] = defaultdict(lambda: {'cantidad': 0, 'impresoras': []})

            for tipo, activos in items.items():
                model_cls = TIPO_MODEL_MAP.get(tipo)
                if not model_cls:
                    raise ValueError('Tipo de activo inválido.')

                for pk_str, data in activos.items():
                    activo_obj = model_cls.objects.select_related('estado', 'lugar').get(pk=pk_str)
                    estado_previo = activo_obj.estado.nombre if activo_obj.estado else ''
                    lugar_previo = activo_obj.lugar.nombre if activo_obj.lugar else ''

                    FacturaActivo.objects.create(
                        factura=factura,
                        tipo_activo=tipo,
                        activo_id=activo_obj.pk,
                        numero_serie=getattr(activo_obj, 'numero_serie', ''),
                        nombre_activo=getattr(activo_obj, 'nombre', ''),
                        estado_previo=estado_previo,
                        lugar_previo=lugar_previo,
                        cantidad=1,
                    )

                    activo_obj.estado = estado_stock
                    activo_obj.lugar = lugar_destino
                    activo_obj.save(update_fields=['estado', 'lugar'])

                    if tipo == 'impresora':
                        requiere_toner = getattr(activo_obj, 'requiere_toner_extra', False)
                        insumo_toner_id = getattr(activo_obj, 'insumo_toner_extra_id', None)
                        cantidad_toner = getattr(activo_obj, 'cantidad_toner_extra', 0)
                        if requiere_toner and insumo_toner_id and cantidad_toner > 0:
                            registro = toner_por_insumo[insumo_toner_id]
                            registro['cantidad'] += cantidad_toner
                            registro['impresoras'].append(str(activo_obj))

            for insumo_id, info in toner_por_insumo.items():
                try:
                    insumo_obj = Insumo.objects.select_for_update().get(pk=insumo_id)
                except Insumo.DoesNotExist as exc:
                    raise ValueError(f"El insumo asociado al tóner extra (ID {insumo_id}) no existe.") from exc
                requerido = info['cantidad']
                if insumo_obj.cantidad_disponible < requerido:
                    impresoras_lista = ', '.join(info['impresoras'])
                    raise ValueError(
                        (
                            f"No hay stock suficiente del insumo '{insumo_obj.nombre}' "
                            f"para las impresoras: {impresoras_lista}. Disponible: "
                            f"{insumo_obj.cantidad_disponible}, requerido: {requerido}."
                        )
                    )

                insumo_obj.cantidad_disponible -= requerido
                insumo_obj.save(update_fields=['cantidad_disponible'])

                FacturaActivo.objects.create(
                    factura=factura,
                    tipo_activo=FacturaActivo.INSUMO,
                    activo_id=insumo_obj.pk,
                    numero_serie='-',
                    nombre_activo=f"{insumo_obj.nombre} (Tóner Extra)",
                    estado_previo='Disponible',
                    lugar_previo='Almacén',
                    cantidad=requerido,
                )

    except Insumo.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Insumo de tóner extra no encontrado.'}, status=404)
    except Lugares.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lugar de destino no encontrado.'}, status=404)
    except ValueError as exc:
        return JsonResponse({'success': False, 'error': str(exc)}, status=400)
    except Exception as exc:
        return JsonResponse({'success': False, 'error': f'Error al emitir la factura: {str(exc)}'}, status=500)

    # Limpiar carrito después de emisión exitosa
    request.session[CARRO_SESSION_KEY] = {'items': {}, 'lugar_destino_id': None, 'observaciones': ''}
    _guardar_sesion(request)
    
    # Generar PDF
    try:
        resultado = generar_factura_pdf(factura.pk)
        response = HttpResponse(resultado.pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Factura_{resultado.factura.numero}.pdf"'
        return response
    except Exception as exc:
        # Si falla la generación del PDF pero la factura ya se creó, informar al usuario
        return JsonResponse({
            'success': True,
            'factura_id': factura.pk,
            'factura_numero': factura.numero,
            'error_pdf': f'La factura se creó correctamente pero hubo un error al generar el PDF: {str(exc)}'
        }, status=200)


@require_GET
def descargar_factura(request: HttpRequest, factura_id: int) -> HttpResponse:
    resultado = generar_factura_pdf(factura_id)
    response = HttpResponse(resultado.pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Factura_{resultado.factura.numero}.pdf"'
    return response
