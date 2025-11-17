"""Views for sending assets to provider service (cart system)."""
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
    Networking,
    Telefonia,
    Periferico,
    TecnologiaMedica,
    Estado,
    Proveedor,
    EnvioServicioProveedor,
    EnvioServicioActivo,
)

# Map of device types to models
TIPO_MODEL_MAP = {
    'computadora': Computadora,
    'impresora': Impresora,
    'monitor': Monitor,
    'networking': Networking,
    'telefonia': Telefonia,
    'periferico': Periferico,
    'tecnologia_medica': TecnologiaMedica,
}

# Session key for cart
CARRO_SERVICIO_SESSION_KEY = 'servicio_proveedor_carrito'


def _ensure_carrito(request: HttpRequest) -> Dict[str, Any]:
    """Ensure cart exists in session."""
    request.session.setdefault(CARRO_SERVICIO_SESSION_KEY, {
        'items': {},
        'proveedor_id': None,
        'motivo_envio': '',
        'observaciones': '',
        'fecha_estimada_retorno': '',
    })
    return request.session[CARRO_SERVICIO_SESSION_KEY]


def _serialize_activo(tipo: str, activo: Any) -> Dict[str, Any]:
    """Serialize asset data for cart."""
    return {
        'id': activo.pk,
        'tipo': tipo,
        'numero_serie': getattr(activo, 'numero_serie', ''),
        'nombre': getattr(activo, 'nombre', str(activo)),
        'estado': getattr(activo.estado, 'nombre', '') if hasattr(activo, 'estado') and activo.estado else '',
        'lugar': getattr(activo.lugar, 'nombre', '') if hasattr(activo, 'lugar') and activo.lugar else '',
    }


def _guardar_sesion(request: HttpRequest) -> None:
    """Mark session as modified."""
    request.session.modified = True


@csrf_exempt
@require_POST
@login_required
def agregar_activo(request: HttpRequest) -> JsonResponse:
    """Add asset to service cart."""
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

    # No restrictions on estado for service - any asset can go to service
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
@login_required
def remover_activo(request: HttpRequest) -> JsonResponse:
    """Remove asset from service cart."""
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
@login_required
def obtener_carrito(request: HttpRequest) -> JsonResponse:
    """Get current cart contents."""
    carrito = _ensure_carrito(request)
    return JsonResponse({'success': True, 'carrito': carrito})


@csrf_exempt
@require_POST
@login_required
def actualizar_carrito(request: HttpRequest) -> JsonResponse:
    """Update cart metadata (provider, reason, dates)."""
    carrito = _ensure_carrito(request)
    
    proveedor_id = request.POST.get('proveedor_id')
    if proveedor_id:
        carrito['proveedor_id'] = proveedor_id
    
    motivo = request.POST.get('motivo_envio', '')
    if motivo:
        carrito['motivo_envio'] = motivo
    
    observaciones = request.POST.get('observaciones', '')
    carrito['observaciones'] = observaciones
    
    fecha_estimada = request.POST.get('fecha_estimada_retorno', '')
    carrito['fecha_estimada_retorno'] = fecha_estimada
    
    _guardar_sesion(request)
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
@login_required
def limpiar_carrito(request: HttpRequest) -> JsonResponse:
    """Clear cart."""
    request.session[CARRO_SERVICIO_SESSION_KEY] = {
        'items': {},
        'proveedor_id': None,
        'motivo_envio': '',
        'observaciones': '',
        'fecha_estimada_retorno': '',
    }
    _guardar_sesion(request)
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
@login_required
def emitir_envio(request: HttpRequest) -> HttpResponse:
    """Create service shipping record and update assets."""

    carrito = _ensure_carrito(request)
    items = carrito.get('items', {})
    proveedor_id = carrito.get('proveedor_id')

    if not items:
        return JsonResponse({'success': False, 'error': 'El carrito está vacío.'}, status=400)

    if not proveedor_id:
        return JsonResponse({'success': False, 'error': 'Debe seleccionar un proveedor.'}, status=400)

    try:
        proveedor = Proveedor.objects.get(pk=proveedor_id)
    except Proveedor.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Proveedor no encontrado.'}, status=404)

    motivo_envio = carrito.get('motivo_envio', '')
    if not motivo_envio:
        return JsonResponse({'success': False, 'error': 'Debe especificar el motivo del envío.'}, status=400)

    observaciones = carrito.get('observaciones', '')
    fecha_estimada_str = carrito.get('fecha_estimada_retorno', '')
    
    # Parse fecha estimada
    fecha_estimada_retorno = None
    if fecha_estimada_str:
        from datetime import datetime
        try:
            fecha_estimada_retorno = datetime.strptime(fecha_estimada_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    # Get "En Servicio" state
    try:
        estado_servicio = Estado.objects.get(nombre__iexact='en servicio')
    except Estado.DoesNotExist:
        try:
            estado_servicio = Estado.objects.get(nombre__icontains='servicio')
        except Estado.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No se encontró el estado "En Servicio". Créelo en el sistema.'
            }, status=500)

    try:
        with transaction.atomic():
            # Create envio record
            envio = EnvioServicioProveedor.objects.create(
                proveedor=proveedor,
                motivo_envio=motivo_envio,
                observaciones=observaciones,
                fecha_estimada_retorno=fecha_estimada_retorno,
                emitido_por=request.user.get_full_name() or request.user.username,
            )

            # Process each asset
            for tipo, activos in items.items():
                model_cls = TIPO_MODEL_MAP.get(tipo)
                if not model_cls:
                    raise ValueError('Tipo de activo inválido.')

                for pk_str, data in activos.items():
                    activo_obj = model_cls.objects.select_related('estado', 'lugar').get(pk=pk_str)
                    estado_previo = activo_obj.estado.nombre if activo_obj.estado else ''
                    lugar_previo = activo_obj.lugar.nombre if activo_obj.lugar else ''

                    # Create envio activo record
                    EnvioServicioActivo.objects.create(
                        envio=envio,
                        tipo_activo=tipo,
                        activo_id=activo_obj.pk,
                        numero_serie=getattr(activo_obj, 'numero_serie', ''),
                        nombre_activo=getattr(activo_obj, 'nombre', str(activo_obj)),
                        estado_previo=estado_previo,
                        lugar_previo=lugar_previo,
                        problema_reportado=motivo_envio,
                    )

                    # Update asset state to "En Servicio"
                    activo_obj.estado = estado_servicio
                    activo_obj.save(update_fields=['estado'])

            # Clear cart
            limpiar_carrito(request)

            return JsonResponse({
                'success': True,
                'envio_numero': envio.numero,
                'mensaje': f'Envío {envio.numero} creado exitosamente. {len([a for t in items.values() for a in t])} activos enviados a servicio.'
            })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

