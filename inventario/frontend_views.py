import json
import logging
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import NoReverseMatch, reverse, reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from urllib.parse import urlencode

# Configurar logger
logger = logging.getLogger(__name__)

from .forms import (
    ComputadoraForm,
    ImpresoraForm,
    InsumoForm,
    MonitorForm,
    NetworkingForm,
    OrdenServicioForm,
    PerifericoForm,
    SoftwareForm,
    TecnologiaMedicaForm,
    TelefoniaForm,
    MobiliarioForm,
    VehiculoForm,
    HerramientaForm,
)
from .models import (
    Bitacora,
    Computadora,
    Estado,
    Factura,
    FacturaActivo,
    Impresora,
    Insumo,
    Lugares,
    Monitor,
    Networking,
    OrdenServicio,
    Periferico,
    Software,
    TecnologiaMedica,
    Telefonia,
    TipoInsumo,
    TipoImpresora,
    TipoNetworking,
    TipoNivel,
    TipoComputadora,
    TipoMonitor,
    TipoPeriferico,
    TipoSoftware,
    TipoTecnologiaMedica,
    TipoTelefonia,
    TipoMobiliario, Mobiliario,
    TipoVehiculo, Vehiculo,
    TipoHerramienta, Herramienta,
)
from .models import generar_numero_inventario
from .utils_reports import (
    SEGMENT_INFORMATICA,
    SEGMENT_MEDICA,
    build_excel_report,
    build_pdf_report,
    gather_enterprise_report,
)
from .utils_orden_servicio import build_orden_servicio_pdf


DEVICE_MODEL_MAP = {
    "computadora": Computadora,
    "impresora": Impresora,
    "monitor": Monitor,
    "networking": Networking,
    "telefonia": Telefonia,
    "periferico": Periferico,
    "tecnologia_medica": TecnologiaMedica,
    "insumo": Insumo,
    "software": Software,
    "orden_servicio": OrdenServicio,
    "mobiliario": Mobiliario,
    "vehiculo": Vehiculo,
    "herramienta": Herramienta,
}


DEVICE_LABELS = {
    "computadora": "Computadora",
    "impresora": "Impresora",
    "monitor": "Monitor",
    "networking": "Networking",
    "telefonia": "Telefonía",
    "periferico": "Periférico",
    "tecnologia_medica": "Tecnología Médica",
    "insumo": "Insumo",
    "software": "Software",
    "mobiliario": "Mobiliario",
    "vehiculo": "Vehículo",
    "herramienta": "Herramienta",
}


REPORT_SEGMENT_LABELS = {
    SEGMENT_INFORMATICA: "Activos Informáticos",
    SEGMENT_MEDICA: "Tecnología Médica",
}


class RedirectToListMixin:
    """Mixin para consolidar guardado transaccional y redirecciones con `next`."""

    redirect_context_key = "redirect_to"

    def _get_candidate_url(self):
        candidate = (self.request.POST.get("next") or self.request.GET.get("next") or "").strip()
        if candidate and url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return candidate
        return ""

    def get_default_success_url(self):
        return super().get_success_url()

    def get_success_url(self):
        return self._get_candidate_url() or self.get_default_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault(
            self.redirect_context_key,
            self._get_candidate_url() or self.get_default_success_url(),
        )
        return context

    def form_valid(self, form):
        with transaction.atomic():
            return super().form_valid(form)


class LugarFilterMixin:
    """Mixin que aplica el filtro jerárquico de lugares y expone metadatos."""

    lugar_filtrado = None
    lugar_parametro = ""

    def aplicar_filtro_lugar(self, queryset):
        raw_value = (self.request.GET.get("lugar") or "").strip()
        self.lugar_parametro = raw_value
        self.lugar_filtrado = None

        if not raw_value:
            return queryset

        if raw_value.isdigit():
            try:
                lugar_obj = Lugares.objects.only(
                    "ruta_jerarquica", "nombre", "nombre_completo"
                ).get(pk=raw_value)
            except Lugares.DoesNotExist:
                # Valor inválido: se limpia para evitar inconsistencias
                self.lugar_parametro = ""
                return queryset

            self.lugar_filtrado = lugar_obj
            return queryset.filter(
                lugar__ruta_jerarquica__startswith=lugar_obj.ruta_jerarquica
            )

        return queryset.filter(lugar__nombre__icontains=raw_value)

    def obtener_contexto_lugar(self):
        if self.lugar_filtrado:
            label = (
                self.lugar_filtrado.nombre_completo
                or self.lugar_filtrado.nombre
            )
            return self.lugar_parametro, label
        return self.lugar_parametro, self.lugar_parametro

    def agregar_contexto_lugar(self, context):
        raw, label = self.obtener_contexto_lugar()
        context["selected_lugar"] = raw
        context["selected_lugar_label"] = label
        return context


class MenuContextMixin:
    """Mixin para agregar el contexto de menú según el tipo de modelo."""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Determinar menu_type según el modelo
        model_name = self.model.__name__ if hasattr(self, 'model') else None
        
        # Modelos de Tecnología Médica
        if model_name == 'TecnologiaMedica':
            context['menu_type'] = 'medica'
        # Modelos de Activos Informáticos
        elif model_name in ['Computadora', 'Impresora', 'Monitor', 'Networking',
                           'Telefonia', 'Periferico', 'Software', 'Insumo']:
            context['menu_type'] = 'informatica'
        # Modelos de Activos Generales
        elif model_name in ['Mobiliario', 'Vehiculo', 'Herramienta']:
            context['menu_type'] = 'generales'
        # Módulos compartidos (sin menú específico - muestra ambos)
        else:
            context['menu_type'] = None
        
        return context


# Dashboard Selection View
def dashboard_selector(request):
    """Pantalla de selección de dashboard."""
    # Si el usuario está autenticado, redirigir automáticamente según su grupo
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.groups.filter(name='Administrador').exists():
            return redirect('inventario:dashboard_admin')
        elif request.user.groups.filter(name='Activos Informáticos').exists():
            return redirect('inventario:dashboard_informatica')
        elif request.user.groups.filter(name='Tecnología Médica').exists():
            return redirect('inventario:dashboard_medica')
        elif request.user.groups.filter(name='Activos Generales').exists():
            return redirect('inventario:dashboard_generales')
    
    # Si no tiene grupo específico o no está autenticado, mostrar selector
    return render(request, 'inventario/dashboard_selector.html', {
        'user': request.user,
        'menu_type': 'selector'  # Menú simplificado para selector
    })


def dashboard(request):
    """Vista del dashboard - Redirige a dashboard_selector."""
    return dashboard_selector(request)


@login_required
def dashboard_administrador(request):
    """Dashboard para el perfil Administrador — vista consolidada de los 3 módulos."""
    today = timezone.now().date()
    limite_garantia = today + timedelta(days=30)

    # ── Activos Informáticos ──────────────────────────────────────────────
    from .models import Computadora, Impresora, Monitor, Networking, Telefonia, Periferico
    informatica_summary = [
        {'label': 'Computadoras', 'total': Computadora.objects.count(), 'icon': 'bi-pc-display', 'list_url': 'inventario:computadora_list'},
        {'label': 'Impresoras',   'total': Impresora.objects.count(),   'icon': 'bi-printer',    'list_url': 'inventario:impresora_list'},
        {'label': 'Monitores',    'total': Monitor.objects.count(),     'icon': 'bi-display',    'list_url': 'inventario:monitor_list'},
        {'label': 'Networking',   'total': Networking.objects.count(),  'icon': 'bi-router',     'list_url': 'inventario:networking_list'},
        {'label': 'Telefonía',    'total': Telefonia.objects.count(),   'icon': 'bi-telephone',  'list_url': 'inventario:telefonia_list'},
        {'label': 'Periféricos',  'total': Periferico.objects.count(),  'icon': 'bi-mouse',      'list_url': 'inventario:periferico_list'},
    ]
    total_informatica = sum(a['total'] for a in informatica_summary)

    # ── Tecnología Médica ─────────────────────────────────────────────────
    from .models import TecnologiaMedica
    total_medica       = TecnologiaMedica.objects.count()
    medica_activos     = TecnologiaMedica.objects.filter(estado__nombre='Activo').count()
    medica_mantenimiento = TecnologiaMedica.objects.filter(estado__nombre='Mantenimiento').count()

    # ── Activos Generales ─────────────────────────────────────────────────
    generales_summary = [
        {'label': 'Mobiliario',   'total': Mobiliario.objects.count(),  'icon': 'bi-building',  'list_url': 'inventario:mobiliario_list'},
        {'label': 'Vehículos',    'total': Vehiculo.objects.count(),    'icon': 'bi-car-front', 'list_url': 'inventario:vehiculo_list'},
        {'label': 'Herramientas', 'total': Herramienta.objects.count(), 'icon': 'bi-tools',     'list_url': 'inventario:herramienta_list'},
    ]
    total_generales = sum(a['total'] for a in generales_summary)

    # ── Garantías próximas (todos los módulos) ────────────────────────────
    garantia_proxima = []
    for model_cls, tipo_label, detail_url in [
        (Computadora,    'Computadora',   'inventario:computadora_detail'),
        (Impresora,      'Impresora',     'inventario:impresora_detail'),
        (Monitor,        'Monitor',       'inventario:monitor_detail'),
        (TecnologiaMedica, 'Tec. Médica', 'inventario:tecnologia_medica_detail'),
        (Mobiliario,     'Mobiliario',    'inventario:mobiliario_detail'),
        (Vehiculo,       'Vehículo',      'inventario:vehiculo_detail'),
        (Herramienta,    'Herramienta',   'inventario:herramienta_detail'),
    ]:
        items = model_cls.objects.filter(
            fecha_finalizacion_garantia__gte=today,
            fecha_finalizacion_garantia__lte=limite_garantia,
        ).select_related('estado')[:5]
        for item in items:
            garantia_proxima.append({
                'nombre': str(item),
                'tipo': tipo_label,
                'fecha': item.fecha_finalizacion_garantia,
                'detail_url': detail_url,
                'pk': item.pk,
            })
    garantia_proxima.sort(key=lambda x: x['fecha'])

    context = {
        'menu_type': 'admin',
        'informatica_summary': informatica_summary,
        'total_informatica': total_informatica,
        'total_medica': total_medica,
        'medica_activos': medica_activos,
        'medica_mantenimiento': medica_mantenimiento,
        'generales_summary': generales_summary,
        'total_generales': total_generales,
        'garantia_proxima': garantia_proxima[:10],
        'total_global': total_informatica + total_medica + total_generales,
    }
    return render(request, 'inventario/dashboard_administrador.html', context)


def dashboard_activos_informaticos(request):
    """Dashboard específico para Activos Informáticos (TI)."""

    today = timezone.now().date()
    limite_garantia = today + timedelta(days=30)

    asset_configs = [
        {
            "key": "computadora",
            "label": "Computadoras",
            "model": Computadora,
            "icon": "bi-pc-display",
            "gradient_class": "bg-mod-computadora",
            "list_url_name": "inventario:computadora_list",
            "create_url_name": "inventario:computadora_create",
            "detail_url_name": "inventario:computadora_detail",
            "has_estado": True,
        },
        {
            "key": "impresora",
            "label": "Impresoras",
            "model": Impresora,
            "icon": "bi-printer",
            "gradient_class": "bg-mod-impresora",
            "list_url_name": "inventario:impresora_list",
            "create_url_name": "inventario:impresora_create",
            "detail_url_name": "inventario:impresora_detail",
            "has_estado": True,
        },
        {
            "key": "monitor",
            "label": "Monitores",
            "model": Monitor,
            "icon": "bi-display",
            "gradient_class": "bg-mod-monitor",
            "list_url_name": "inventario:monitor_list",
            "create_url_name": "inventario:monitor_create",
            "detail_url_name": "inventario:monitor_detail",
            "has_estado": True,
        },
        {
            "key": "networking",
            "label": "Networking",
            "model": Networking,
            "icon": "bi-diagram-3",
            "gradient_class": "bg-mod-networking",
            "list_url_name": "inventario:networking_list",
            "create_url_name": "inventario:networking_create",
            "detail_url_name": "inventario:networking_detail",
            "has_estado": True,
        },
        {
            "key": "telefonia",
            "label": "Telefonía",
            "model": Telefonia,
            "icon": "bi-telephone-outbound",
            "gradient_class": "bg-mod-telefonia",
            "list_url_name": "inventario:telefonia_list",
            "create_url_name": "inventario:telefonia_create",
            "detail_url_name": "inventario:telefonia_detail",
            "has_estado": True,
        },
        {
            "key": "periferico",
            "label": "Periféricos",
            "model": Periferico,
            "icon": "bi-keyboard",
            "gradient_class": "bg-mod-periferico",
            "list_url_name": "inventario:periferico_list",
            "create_url_name": "inventario:periferico_create",
            "detail_url_name": "inventario:periferico_detail",
            "has_estado": True,
        },
        {
            "key": "insumo",
            "label": "Insumos TI",
            "model": Insumo,
            "icon": "bi-box-seam",
            "gradient_class": "bg-mod-insumo",
            "list_url_name": "inventario:insumo_list",
            "create_url_name": "inventario:insumo_create",
            "detail_url_name": "inventario:insumo_detail",
            "uses_boolean_activo": True,
        },
        {
            "key": "software",
            "label": "Software",
            "model": Software,
            "icon": "bi-cpu",
            "gradient_class": "bg-mod-software",
            "list_url_name": "inventario:software_list",
            "create_url_name": "inventario:software_create",
            "detail_url_name": "inventario:software_detail",
            "has_estado": True,
        },
    ]

    asset_cards = []
    estado_totales = {}
    total_equipos = 0
    total_activos = 0

    for cfg in asset_configs:
        model = cfg["model"]
        total = model.objects.count()
        activos = None

        if cfg.get("has_estado"):
            activos = model.objects.filter(estado__nombre="Activo").count()
            estado_rows = (
                model.objects.values("estado__nombre")
                .annotate(total=Count("id"))
                .order_by()
            )
            for row in estado_rows:
                nombre_estado = row["estado__nombre"] or "Sin estado"
                estado_totales[nombre_estado] = (
                    estado_totales.get(nombre_estado, 0) + row["total"]
                )
        elif cfg.get("uses_boolean_activo"):
            activos = model.objects.filter(activo=True).count()
            inactivos = total - activos
            if activos:
                estado_totales["Activo"] = (
                    estado_totales.get("Activo", 0) + activos
                )
            if inactivos:
                estado_totales["Inactivo"] = (
                    estado_totales.get("Inactivo", 0) + inactivos
                )

        active_percentage = None
        if total and activos is not None:
            active_percentage = round((activos / total) * 100)

        asset_cards.append(
            {
                "key": cfg["key"],
                "label": cfg["label"],
                "total": total,
                "active": activos,
                "active_percentage": active_percentage,
                "icon": cfg["icon"],
                "gradient_class": cfg["gradient_class"],
                "list_url": reverse(cfg["list_url_name"]),
                "create_url": reverse(cfg["create_url_name"]),
            }
        )

        total_equipos += total
        if activos is not None:
            total_activos += activos

    color_palette = [
        "#6366f1",
        "#8b5cf6",
        "#f97316",
        "#f43f5e",
        "#0ea5e9",
        "#14b8a6",
        "#facc15",
        "#38bdf8",
        "#ec4899",
    ]

    estado_items = sorted(
        estado_totales.items(), key=lambda item: item[1], reverse=True
    )
    chart_estado_labels = [item[0] for item in estado_items]
    chart_estado_data = [item[1] for item in estado_items]
    chart_estado_colors = [
        color_palette[idx % len(color_palette)]
        for idx in range(len(chart_estado_labels))
    ]

    chart_asset_labels = [card["label"] for card in asset_cards]
    chart_asset_data = [card["total"] for card in asset_cards]
    chart_asset_colors = [
        color_palette[idx % len(color_palette)]
        for idx in range(len(chart_asset_labels))
    ]

    icon_map = {cfg["key"]: cfg["icon"] for cfg in asset_configs}
    label_map = {cfg["key"]: cfg["label"] for cfg in asset_configs}
    detail_url_map = {
        cfg["key"]: cfg["detail_url_name"] for cfg in asset_configs
    }

    recent_items = []
    for cfg in asset_configs:
        model = cfg["model"]
        if not hasattr(model, "fecha_creacion"):
            continue
        queryset = model.objects.order_by("-fecha_creacion")[:5]
        for item in queryset:
            fecha_evento = getattr(item, "fecha_creacion", None)
            estado_nombre = None
            if hasattr(item, "estado") and item.estado:
                estado_nombre = item.estado.nombre
            identifier = (
                getattr(item, "numero_inventario", None)
                or getattr(item, "numero_serie", None)
                or getattr(item, "numero_linea", None)
                or getattr(item, "numero_licencia", None)
            )
            try:
                detail_url = reverse(
                    cfg["detail_url_name"], kwargs={"pk": item.pk}
                )
            except NoReverseMatch:
                detail_url = None

            recent_items.append(
                {
                    "tipo": cfg["label"],
                    "icon": cfg["icon"],
                    "nombre": item.nombre,
                    "fecha": fecha_evento or timezone.now(),
                    "estado": estado_nombre,
                    "estado_slug": (
                        estado_nombre.lower().replace(" ", "-")
                        if estado_nombre
                        else "sin-estado"
                    ),
                    "identifier": identifier,
                    "url": detail_url,
                }
            )

    recent_items.sort(
        key=lambda entry: entry["fecha"] or timezone.now(), reverse=True
    )
    recent_items = recent_items[:10]

    warranty_configs = [
        {
            "key": "computadora",
            "model": Computadora,
            "date_field": "fecha_finalizacion_garantia",
        },
        {
            "key": "impresora",
            "model": Impresora,
            "date_field": "fecha_finalizacion_garantia",
        },
        {
            "key": "monitor",
            "model": Monitor,
            "date_field": "fecha_finalizacion_garantia",
        },
        {
            "key": "networking",
            "model": Networking,
            "date_field": "fecha_finalizacion_garantia",
        },
        {
            "key": "telefonia",
            "model": Telefonia,
            "date_field": "fecha_finalizacion_garantia",
        },
        {
            "key": "periferico",
            "model": Periferico,
            "date_field": "fecha_finalizacion_garantia",
        },
        {
            "key": "software",
            "model": Software,
            "date_field": "fecha_expiracion",
        },
    ]

    warranty_alerts = []
    for cfg in warranty_configs:
        model = cfg["model"]
        date_field = cfg["date_field"]
        filtros = {
            f"{date_field}__isnull": False,
            f"{date_field}__gte": today,
            f"{date_field}__lte": limite_garantia,
        }
        queryset = model.objects.filter(**filtros).order_by(date_field)[:5]
        for item in queryset:
            fecha_vencimiento = getattr(item, date_field)
            if fecha_vencimiento is None:
                continue
            if isinstance(fecha_vencimiento, datetime):
                fecha_vencimiento = fecha_vencimiento.date()
            estado_nombre = None
            if hasattr(item, "estado") and item.estado:
                estado_nombre = item.estado.nombre
            try:
                detail_url = reverse(
                    detail_url_map[cfg["key"]], kwargs={"pk": item.pk}
                )
            except (KeyError, NoReverseMatch):
                detail_url = None

            dias_restantes = (fecha_vencimiento - today).days
            warranty_alerts.append(
                {
                    "tipo": label_map.get(cfg["key"], cfg["key"]),
                    "icon": icon_map.get(cfg["key"], "bi-shield-exclamation"),
                    "nombre": item.nombre,
                    "fecha": fecha_vencimiento,
                    "dias": dias_restantes,
                    "estado": estado_nombre,
                    "estado_slug": (
                        estado_nombre.lower().replace(" ", "-")
                        if estado_nombre
                        else "sin-estado"
                    ),
                    "url": detail_url,
                }
            )

    warranty_alerts.sort(key=lambda item: item["fecha"])
    warranty_alerts = warranty_alerts[:10]

    insumo_qs = (
        Insumo.objects.filter(
            activo=True, cantidad_disponible__lte=F("punto_reorden")
        )
        .order_by("cantidad_disponible")[:8]
    )
    insumo_restock = [
        {
            "nombre": insumo.nombre,
            "disponible": insumo.cantidad_disponible,
            "punto_reorden": insumo.punto_reorden,
            "unidad": insumo.unidad_medida,
        }
        for insumo in insumo_qs
    ]

    insumo_stats = Insumo.objects.aggregate(
        total=Coalesce(Sum("cantidad_total"), 0),
        disponible=Coalesce(Sum("cantidad_disponible"), 0),
    )
    insumo_summary = {
        "total": insumo_stats["total"],
        "disponible": insumo_stats["disponible"],
        "por_reponer": len(insumo_restock),
    }
    if insumo_summary["total"]:
        insumo_summary["porcentaje_disponible"] = round(
            (insumo_summary["disponible"] / insumo_summary["total"]) * 100
        )
    else:
        insumo_summary["porcentaje_disponible"] = 0

    bitacora_entries = Bitacora.objects.order_by("-fecha_evento")[:8]
    bitacora_feed = []
    for entry in bitacora_entries:
        url_name = detail_url_map.get(entry.tipo_dispositivo)
        try:
            detalle_url = (
                reverse(url_name, kwargs={"pk": entry.dispositivo_id})
                if url_name
                else None
            )
        except NoReverseMatch:
            detalle_url = None

        bitacora_feed.append(
            {
                "tipo_evento": entry.get_tipo_evento_display(),
                "tipo_dispositivo": entry.get_tipo_dispositivo_display(),
                "icon": icon_map.get(entry.tipo_dispositivo, "bi-activity"),
                "descripcion": entry.descripcion,
                "responsable": entry.usuario_responsable,
                "fecha": entry.fecha_evento,
                "url": detalle_url,
                "nombre": entry.dispositivo_nombre,
            }
        )

    inactive_assets = total_equipos - total_activos
    active_ratio = (
        round((total_activos / total_equipos) * 100)
        if total_equipos
        else 0
    )

    context = {
        "asset_cards": asset_cards,
        "total_assets": total_equipos,
        "active_assets": total_activos,
        "inactive_assets": inactive_assets,
        "active_ratio": active_ratio,
        "chart_asset_labels": chart_asset_labels,
        "chart_asset_data": chart_asset_data,
        "chart_asset_colors": chart_asset_colors,
        "chart_estado_labels": chart_estado_labels,
        "chart_estado_data": chart_estado_data,
        "chart_estado_colors": chart_estado_colors,
        "recent_activity": recent_items,
        "warranty_alerts": warranty_alerts,
        "insumo_summary": insumo_summary,
        "insumo_restock": insumo_restock,
        "bitacora_feed": bitacora_feed,
        "pending_warranties": len(warranty_alerts),
        "today": today,
        # Claves previas para compatibilidad con plantillas antiguas
        "equipos_recientes": recent_items,
        "equipos_garantia_vencimiento": warranty_alerts,
        "total_equipos": total_equipos,
        "equipos_activos": total_activos,
    }

    context["dashboard_type"] = "informatica"
    context["dashboard_title"] = "Activos Informáticos"
    context["menu_type"] = "informatica"  # Menú específico de TI
    
    return render(request, "inventario/dashboard.html", context)


def dashboard_tecnologia_medica(request):
    """Dashboard específico para Tecnología Médica."""

    today = timezone.now().date()
    limite_calibracion = today + timedelta(days=30)
    limite_mantenimiento = today + timedelta(days=30)

    # Estadísticas generales de tecnología médica
    total_equipos = TecnologiaMedica.objects.count()
    equipos_activos = TecnologiaMedica.objects.filter(estado__nombre="Activo").count()
    equipos_mantenimiento = TecnologiaMedica.objects.filter(estado__nombre="En mantenimiento").count()
    equipos_inactivos = TecnologiaMedica.objects.filter(estado__nombre="Inactivo").count()

    # Equipos por clasificación de riesgo
    clasificacion_stats = (
        TecnologiaMedica.objects
        .values('clasificacion_riesgo')
        .annotate(total=Count('id'))
        .order_by('clasificacion_riesgo')
    )
    
    clasificacion_labels = []
    clasificacion_data = []
    clasificacion_colors = {
        'clase_i': '#10b981',
        'clase_iia': '#3b82f6',
        'clase_iib': '#f59e0b',
        'clase_iii': '#f97316',
        'clase_iv': '#ef4444',
    }
    clasificacion_color_list = []
    
    for item in clasificacion_stats:
        if item['clasificacion_riesgo']:
            label_map = {
                'clase_i': 'Clase I',
                'clase_iia': 'Clase IIa',
                'clase_iib': 'Clase IIb',
                'clase_iii': 'Clase III',
                'clase_iv': 'Clase IV',
            }
            clasificacion_labels.append(label_map.get(item['clasificacion_riesgo'], item['clasificacion_riesgo']))
            clasificacion_data.append(item['total'])
            clasificacion_color_list.append(clasificacion_colors.get(item['clasificacion_riesgo'], '#6b7280'))

    # Equipos por tipo
    tipo_stats = (
        TecnologiaMedica.objects
        .values('tipo_tecnologia_medica__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')[:10]
    )
    
    tipo_labels = [item['tipo_tecnologia_medica__nombre'] for item in tipo_stats]
    tipo_data = [item['total'] for item in tipo_stats]
    tipo_colors = ['#dc2626', '#ef4444', '#f87171', '#fca5a5', '#fecaca', '#fee2e2', '#991b1b', '#7f1d1d', '#450a0a', '#b91c1c']

    # Equipos que requieren calibración próxima
    equipos_calibracion = []
    for equipo in TecnologiaMedica.objects.filter(requiere_calibracion=True):
        if equipo.requiere_calibracion_proxima:
            equipos_calibracion.append({
                'id': equipo.id,
                'nombre': equipo.nombre,
                'tipo': equipo.tipo_tecnologia_medica.nombre,
                'fecha_ultima': equipo.fecha_ultima_calibracion,
                'frecuencia': equipo.frecuencia_calibracion_meses,
                'clasificacion': equipo.get_clasificacion_riesgo_display() if equipo.clasificacion_riesgo else 'N/A',
                'url': reverse('inventario:tecnologia_medica_detail', kwargs={'pk': equipo.pk}),
            })

    # Equipos que requieren mantenimiento próximo
    equipos_mantenimiento_list = []
    for equipo in TecnologiaMedica.objects.filter(requiere_mantenimiento_preventivo=True):
        if equipo.requiere_mantenimiento_proximo:
            equipos_mantenimiento_list.append({
                'id': equipo.id,
                'nombre': equipo.nombre,
                'tipo': equipo.tipo_tecnologia_medica.nombre,
                'fecha_ultima': equipo.fecha_ultimo_mantenimiento,
                'frecuencia': equipo.frecuencia_mantenimiento_meses,
                'area': equipo.area_aplicacion or 'N/A',
                'url': reverse('inventario:tecnologia_medica_detail', kwargs={'pk': equipo.pk}),
            })

    # Equipos críticos (Clase III y IV)
    equipos_criticos = TecnologiaMedica.objects.filter(
        clasificacion_riesgo__in=['clase_iii', 'clase_iv']
    ).count()

    # Equipos recientes
    equipos_recientes = TecnologiaMedica.objects.select_related(
        'tipo_tecnologia_medica', 'estado', 'lugar'
    ).order_by('-fecha_creacion')[:8]
    
    recent_items = []
    for equipo in equipos_recientes:
        recent_items.append({
            'id': equipo.id,
            'nombre': equipo.nombre,
            'tipo': equipo.tipo_tecnologia_medica.nombre,
            'estado': equipo.estado.nombre,
            'lugar': equipo.lugar.nombre,
            'fecha': equipo.fecha_creacion,
            'clasificacion': equipo.get_clasificacion_riesgo_display() if equipo.clasificacion_riesgo else 'N/A',
            'url': reverse('inventario:tecnologia_medica_detail', kwargs={'pk': equipo.pk}),
        })

    # Bitácora reciente de tecnología médica
    bitacora_entries = Bitacora.objects.filter(
        tipo_dispositivo='tecnologia_medica'
    ).order_by('-fecha_evento')[:10]
    
    bitacora_feed = []
    for entry in bitacora_entries:
        try:
            detalle_url = reverse('inventario:tecnologia_medica_detail', kwargs={'pk': entry.dispositivo_id})
        except NoReverseMatch:
            detalle_url = None

        bitacora_feed.append({
            'tipo_evento': entry.get_tipo_evento_display(),
            'icon': 'bi-heart-pulse',
            'descripcion': entry.descripcion,
            'responsable': entry.usuario_responsable,
            'fecha': entry.fecha_evento,
            'url': detalle_url,
            'nombre': entry.dispositivo_nombre,
        })

    # Estadísticas por estado
    estado_stats = (
        TecnologiaMedica.objects
        .values('estado__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    
    estado_labels = [item['estado__nombre'] for item in estado_stats]
    estado_data = [item['total'] for item in estado_stats]
    estado_colors = ['#10b981', '#f59e0b', '#ef4444', '#6b7280', '#3b82f6']

    active_ratio = round((equipos_activos / total_equipos) * 100) if total_equipos else 0

    context = {
        'total_equipos': total_equipos,
        'equipos_activos': equipos_activos,
        'equipos_en_mantenimiento': equipos_mantenimiento,
        'equipos_inactivos': equipos_inactivos,
        'equipos_criticos': equipos_criticos,
        'active_ratio': active_ratio,

        # Gráficos
        'clasificacion_labels': clasificacion_labels,
        'clasificacion_data': clasificacion_data,
        'clasificacion_colors': clasificacion_color_list,

        'tipo_labels': tipo_labels,
        'tipo_data': tipo_data,
        'tipo_colors': tipo_colors[:len(tipo_labels)],

        'estado_labels': estado_labels,
        'estado_data': estado_data,
        'estado_colors': estado_colors[:len(estado_labels)],

        # Alertas y listados
        'equipos_calibracion': equipos_calibracion[:10],
        'equipos_mantenimiento': equipos_mantenimiento_list[:10],
        'equipos_recientes': recent_items,
        'bitacora_feed': bitacora_feed,

        # Contadores de alertas
        'alertas_calibracion': len(equipos_calibracion),
        'alertas_mantenimiento': len(equipos_mantenimiento_list),

        'today': today,
        'dashboard_type': 'medica',
        'dashboard_title': 'Tecnología Médica',
        'menu_type': 'medica',  # Menú específico de Tecnología Médica
    }

    return render(request, 'inventario/dashboard_tecnologia_medica.html', context)


def reports_menu(request):
    report_items = [
        {
            "title": "Reporte empresarial",
            "description": (
                "Vista consolidada de garantías, licencias, obsolescencia, "
                "compras y bajas para la gerencia."
            ),
            "icon": "bi-graph-up-arrow",
            "url_name": "inventario:reports_enterprise",
            "available": True,
        },
        {
            "title": "Reportes personalizados",
            "description": (
                "Configure tableros y métricas a medida para áreas "
                "específicas."
            ),
            "icon": "bi-kanban",
            "url_name": "",
            "available": False,
        },
        {
            "title": "Historial de exportaciones",
            "description": (
                "Acceda al registro de archivos generados para auditoría "
                "y seguimiento."
            ),
            "icon": "bi-archive",
            "url_name": "",
            "available": False,
        },
    ]

    context = {"report_items": report_items}
    return render(request, "inventario/reports/menu.html", context)


def reports_enterprise(request):
    start_param = request.GET.get("start")
    end_param = request.GET.get("end")
    segment_param = (request.GET.get("segment") or "").lower()

    segment = (
        segment_param if segment_param in REPORT_SEGMENT_LABELS else SEGMENT_INFORMATICA
    )

    start_date = parse_date(start_param) if start_param else None
    end_date = parse_date(end_param) if end_param else None

    report = gather_enterprise_report(start_date, end_date, segment=segment)

    period_slug = "{}_{}-{}".format(
        segment,
        report["start_date"].strftime("%Y%m%d"),
        report["end_date"].strftime("%Y%m%d"),
    )

    range_params = {
        "start": report["start_date"].strftime("%Y-%m-%d"),
        "end": report["end_date"].strftime("%Y-%m-%d"),
    }
    params = {**range_params, "segment": segment}
    base_query = urlencode(params)
    segment_queries = {
        key: urlencode({**range_params, "segment": key})
        for key in REPORT_SEGMENT_LABELS
    }
    segment_options = [
        {
            "key": key,
            "label": REPORT_SEGMENT_LABELS[key],
            "query": segment_queries[key],
        }
        for key in REPORT_SEGMENT_LABELS
    ]

    download = request.GET.get("download", "").lower()
    if download == "pdf":
        pdf_bytes = build_pdf_report(report)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="reporte_empresarial_{period_slug}.pdf"'
        )
        return response

    if download in {"xlsx", "excel"}:
        try:
            excel_bytes = build_excel_report(report)
        except RuntimeError as exc:
            messages.error(request, str(exc))
        else:
            response = HttpResponse(
                excel_bytes,
                content_type=(
                    "application/"
                    "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
            )
            response["Content-Disposition"] = (
                'attachment; filename="'
                f"reporte_empresarial_{period_slug}.xlsx"
                '"'
            )
            return response

    excel_available = True
    try:
        from openpyxl import Workbook  # type: ignore  # noqa: F401
    except ImportError:
        excel_available = False

    total_deliveries = sum(
        item["total"] for item in report["monthly_deliveries"]
    )

    context = {
        "report": report,
        "start_date": report["start_date"],
        "end_date": report["end_date"],
        "generated_at": report["generated_at"],
        "base_query": base_query,
        "excel_available": excel_available,
        "total_deliveries": total_deliveries,
        "segment": segment,
        "segment_label": REPORT_SEGMENT_LABELS[segment],
        "segment_queries": segment_queries,
        "segment_labels": REPORT_SEGMENT_LABELS,
        "segment_options": segment_options,
    }

    return render(
        request,
        "inventario/reports/enterprise_report.html",
        context,
    )


def configuracion_lugares(request):
    """Vista de apoyo para administrar la jerarquía de lugares"""
    lugares = (
        Lugares.objects.select_related("padre", "tipo_nivel")
        .filter(activo=True)
        .order_by("nivel", "nombre")
    )

    tree_data = []
    for lugar in lugares:
        tree_data.append(
            {
                "id": lugar.pk,
                "nombre": lugar.nombre,
                "nombre_completo": lugar.nombre_completo or lugar.nombre,
                "nivel": lugar.nivel,
                "tipo": (
                    lugar.tipo_nivel.nombre
                    if lugar.tipo_nivel
                    else f"Nivel {lugar.nivel}"
                ),
                "padre_id": lugar.padre.pk if lugar.padre else None,
                "es_hoja": not lugar.hijos.exists(),
                "codigo": lugar.codigo or "",
                "activo": lugar.activo,
                "tipo_nivel_id": lugar.tipo_nivel_id,
                "tipo_nivel_requiere_codigo": (
                    bool(lugar.tipo_nivel.requiere_codigo)
                    if lugar.tipo_nivel
                    else False
                ),
            }
        )

    tipo_niveles = TipoNivel.objects.filter(activo=True).order_by(
        "nivel", "nombre"
    )
    tipo_niveles_data = [
        {
            "id": tipo.pk,
            "nivel": tipo.nivel,
            "nombre": tipo.nombre,
            "requiere_codigo": tipo.requiere_codigo,
        }
        for tipo in tipo_niveles
    ]

    selected_value = request.GET.get("lugar", "")

    context = {
        "tree_data_json": json.dumps(tree_data),
        "selected_value": selected_value,
        "total_lugares": len(tree_data),
        "tipo_niveles_json": json.dumps(tipo_niveles_data),
    }

    return render(request, "inventario/configuracion_lugares.html", context)


# ============================================================================
# COMPUTADORAS VIEWS
# ============================================================================


class ComputadoraListView(MenuContextMixin, LugarFilterMixin, ListView):
    """Vista de lista de computadoras con filtros y búsqueda"""

    model = Computadora
    template_name = "inventario/computadora_list.html"
    context_object_name = "object_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Computadora.objects.select_related(
                "estado", "lugar", "tipo_computadora", "fabricante", "modelo"
            )
            .all()
            .order_by("-fecha_creacion")
        )

        # Filtro de búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search)
                | Q(numero_inventario__icontains=search)
                | Q(numero_serie__icontains=search)
                | Q(fabricante__nombre__icontains=search)
                | Q(modelo__nombre__icontains=search)
            )

        # Filtro por estado
        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado__nombre=estado)

        # Filtro por tipo
        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo_computadora__nombre=tipo)

        queryset = self.aplicar_filtro_lugar(queryset)

        for item in queryset:
            if not item.numero_inventario:
                descriptor = (
                    item.modelo.nombre
                    if item.modelo
                    else item.tipo_computadora.nombre
                    if item.tipo_computadora
                    else item.fabricante.nombre
                    if item.fabricante
                    else item.nombre
                )
                item.numero_inventario = generar_numero_inventario(
                    lugar=getattr(item, "lugar", None),
                    descriptor=descriptor,
                    referencia=item.numero_serie,
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["computadoras"] = context["object_list"]

        # Estadísticas para las tarjetas
        context["total_computadoras"] = Computadora.objects.count()
        context["computadoras_activas"] = Computadora.objects.filter(
            estado__nombre="Activo"
        ).count()
        context["computadoras_mantenimiento"] = Computadora.objects.filter(
            estado__nombre="Mantenimiento"
        ).count()
        context["computadoras_inactivas"] = Computadora.objects.filter(
            estado__nombre="Inactivo"
        ).count()

        # Catálogos para filtros dinámicos
        context["estados"] = Estado.objects.all().order_by("nombre")
        context["tipos"] = TipoComputadora.objects.all().order_by("nombre")

        self.agregar_contexto_lugar(context)

        return context


class ComputadoraDetailView(MenuContextMixin, DetailView):
    """Vista de detalle de una computadora"""

    model = Computadora
    template_name = "inventario/computadora_detail.html"
    context_object_name = "object"

    def get_queryset(self):
        return Computadora.objects.select_related(
            "estado",
            "lugar",
            "tipo_computadora",
            "fabricante",
            "modelo",
            "proveedor",
            "tipo_garantia",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agregar bitácoras recientes del dispositivo
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="computadora", dispositivo_id=self.object.pk
        ).order_by("-fecha_evento")[:10]

        return context


class ComputadoraCreateView(MenuContextMixin, CreateView):
    """Vista para crear una nueva computadora"""

    model = Computadora
    form_class = ComputadoraForm
    template_name = "inventario/computadora_form.html"
    success_url = reverse_lazy("inventario:computadora_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "device_type": "computadora",
                "form_id": "computadoraForm",
                "list_url": reverse("inventario:computadora_list"),
                "detail_url": None,
            }
        )
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Computadora "{form.instance.nombre}" creada exitosamente.',
        )
        return super().form_valid(form)


class ComputadoraUpdateView(MenuContextMixin, RedirectToListMixin, UpdateView):
    """Vista para editar una computadora existente"""

    model = Computadora
    form_class = ComputadoraForm
    template_name = "inventario/computadora_form.html"
    success_url = reverse_lazy("inventario:computadora_list")

    def get_context_data(self, **kwargs):
        logger.info(f"[COMPUTADORA UPDATE] GET - ID: {self.object.pk}")
        logger.info(f"  → Nombre actual: {self.object.nombre}")
        logger.info(f"  → Estado actual: {self.object.estado.nombre}")
        logger.info(f"  → Inventario actual: {self.object.numero_inventario}")
        logger.info(f"  → Comentarios actual: {self.object.comentarios}")
        
        context = super().get_context_data(**kwargs)

        # Agregar bitácoras recientes del dispositivo
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="computadora", dispositivo_id=self.object.pk
        ).order_by("-fecha_evento")[:5]

        # Variables para el sistema de plantillas
        from django.urls import reverse

        context.update(
            {
                "device_type": "computadora",
                "form_id": "computadoraForm",
                "list_url": reverse("inventario:computadora_list"),
                "detail_url": reverse(
                    "inventario:computadora_detail",
                    kwargs={"pk": self.object.pk},
                ),
            }
        )

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        logger.info(f"[COMPUTADORA UPDATE] POST - ID: {self.object.pk}")
        logger.info(f"  → Datos recibidos en POST:")
        for key, value in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                logger.info(f"     • {key}: {value}")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        logger.info(f"[COMPUTADORA UPDATE] FORM_VALID - ID: {self.object.pk}")
        logger.info(f"  → Datos ANTES de guardar:")
        logger.info(f"     • Nombre BD: {self.object.nombre}")
        logger.info(f"     • Estado BD: {self.object.estado.nombre}")
        logger.info(f"     • Comentarios BD: {self.object.comentarios}")
        logger.info(f"  → Datos del FORMULARIO (form.cleaned_data):")
        for key, value in form.cleaned_data.items():
            logger.info(f"     • {key}: {value}")
        
        messages.success(
            self.request,
            f'Computadora "{form.instance.nombre}" actualizada exitosamente.',
        )
        result = super().form_valid(form)
        
        # Refrescar desde BD para ver cambios persistidos
        self.object.refresh_from_db()
        logger.info(f"  → Datos DESPUÉS de guardar (desde BD):")
        logger.info(f"     • Nombre BD: {self.object.nombre}")
        logger.info(f"     • Estado BD: {self.object.estado.nombre}")
        logger.info(f"     • Inventario BD: {self.object.numero_inventario}")
        logger.info(f"     • Comentarios BD: {self.object.comentarios}")
        logger.info(f"  → URL de redirección: {self.get_success_url()}")
        
        return result
    
    def form_invalid(self, form):
        logger.error(f"[COMPUTADORA UPDATE] FORM_INVALID - ID: {self.object.pk}")
        logger.error(f"  → Errores del formulario:")
        for field, errors in form.errors.items():
            logger.error(f"     • {field}: {errors}")
        return super().form_invalid(form)

    def get_success_url(self):
        candidate = self.request.POST.get("next") or self.request.GET.get("next")
        if candidate and url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return candidate
        return super().get_success_url()


class ComputadoraDeleteView(DeleteView):
    """Vista para eliminar una computadora"""

    model = Computadora
    success_url = reverse_lazy("inventario:computadora_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre
        messages.success(
            request,
            f'Computadora "{nombre}" eliminada exitosamente.',
        )
        return super().delete(request, *args, **kwargs)


# ============================================================================
# IMPRESORAS VIEWS
# ============================================================================


class ImpresoraListView(MenuContextMixin, LugarFilterMixin, ListView):
    """Vista de lista de impresoras con filtros y búsqueda"""

    model = Impresora
    template_name = "inventario/impresora_list.html"
    context_object_name = "object_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Impresora.objects.select_related(
                "estado", "lugar", "tipo_impresora", "fabricante", "modelo"
            )
            .all()
            .order_by("-fecha_creacion")
        )

        # Filtro de búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search)
                | Q(numero_inventario__icontains=search)
                | Q(numero_serie__icontains=search)
                | Q(fabricante__nombre__icontains=search)
                | Q(modelo__nombre__icontains=search)
            )

        # Filtro por estado
        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado__nombre=estado)

        # Filtro por tipo
        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo_impresora__nombre=tipo)

        queryset = self.aplicar_filtro_lugar(queryset)

        for item in queryset:
            if not item.numero_inventario:
                descriptor = (
                    item.modelo.nombre
                    if item.modelo
                    else item.tipo_impresora.nombre
                    if item.tipo_impresora
                    else item.fabricante.nombre
                    if item.fabricante
                    else item.nombre
                )
                item.numero_inventario = generar_numero_inventario(
                    lugar=getattr(item, "lugar", None),
                    descriptor=descriptor,
                    referencia=item.numero_serie,
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas para las tarjetas
        context["total_impresoras"] = Impresora.objects.count()
        context["impresoras_activas"] = Impresora.objects.filter(
            estado__nombre="Activo"
        ).count()
        context["impresoras_mantenimiento"] = Impresora.objects.filter(
            estado__nombre="Mantenimiento"
        ).count()
        context["impresoras_inactivas"] = Impresora.objects.filter(
            estado__nombre="Inactivo"
        ).count()

        # Catálogos para filtros dinámicos
        context["estados"] = Estado.objects.all().order_by("nombre")
        context["tipos"] = TipoImpresora.objects.all().order_by("nombre")

        self.agregar_contexto_lugar(context)

        return context


class ImpresoraDetailView(DetailView):
    """Vista de detalle de una impresora"""

    model = Impresora
    template_name = "inventario/impresora_detail.html"
    context_object_name = "object"

    def get_queryset(self):
        return Impresora.objects.select_related(
            "estado",
            "lugar",
            "tipo_impresora",
            "fabricante",
            "modelo",
            "proveedor",
            "tipo_garantia",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agregar bitácoras recientes del dispositivo
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="impresora", dispositivo_id=self.object.pk
        ).order_by("-fecha_evento")[:10]

        return context


class ImpresoraCreateView(CreateView):
    """Vista para crear una nueva impresora"""

    model = Impresora
    form_class = ImpresoraForm
    template_name = "inventario/impresora_form.html"
    success_url = reverse_lazy("inventario:impresora_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "device_type": "impresora",
                "form_id": "impresoraForm",
                "list_url": reverse("inventario:impresora_list"),
                "detail_url": None,
            }
        )
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Impresora "{form.instance.nombre}" creada exitosamente.',
        )
        return super().form_valid(form)


class ImpresoraUpdateView(RedirectToListMixin, UpdateView):
    """Vista para editar una impresora existente"""

    model = Impresora
    form_class = ImpresoraForm
    template_name = "inventario/impresora_form.html"
    success_url = reverse_lazy("inventario:impresora_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agregar bitácoras recientes del dispositivo
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="impresora", dispositivo_id=self.object.pk
        ).order_by("-fecha_evento")[:5]

        # Variables para el sistema de plantillas
        from django.urls import reverse

        context.update(
            {
                "device_type": "impresora",
                "form_id": "impresoraForm",
                "list_url": reverse("inventario:impresora_list"),
                "detail_url": reverse(
                    "inventario:impresora_detail",
                    kwargs={"pk": self.object.pk},
                ),
            }
        )

        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Impresora "{form.instance.nombre}" actualizada exitosamente.',
        )
        return super().form_valid(form)


class ImpresoraDeleteView(DeleteView):
    """Vista para eliminar una impresora"""

    model = Impresora
    success_url = reverse_lazy("inventario:impresora_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre
        messages.success(
            request,
            f'Impresora "{nombre}" eliminada exitosamente.',
        )
        return super().delete(request, *args, **kwargs)


# ============================================================================
# MONITORES VIEWS
# ============================================================================


class MonitorListView(MenuContextMixin, LugarFilterMixin, ListView):
    """Vista de lista de monitores con filtros y búsqueda"""

    model = Monitor
    template_name = "inventario/monitor_list.html"
    context_object_name = "object_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Monitor.objects.select_related(
                "estado", "lugar", "tipo_monitor", "fabricante", "modelo"
            )
            .all()
            .order_by("-fecha_creacion")
        )

        # Filtro de búsqueda
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search)
                | Q(numero_inventario__icontains=search)
                | Q(numero_serie__icontains=search)
                | Q(fabricante__nombre__icontains=search)
                | Q(modelo__nombre__icontains=search)
            )

        # Filtro por estado
        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado__nombre=estado)

        # Filtro por tipo
        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo_monitor__nombre=tipo)

        queryset = self.aplicar_filtro_lugar(queryset)

        for item in queryset:
            if not item.numero_inventario:
                descriptor = (
                    item.modelo.nombre
                    if item.modelo
                    else item.tipo_monitor.nombre
                    if item.tipo_monitor
                    else item.fabricante.nombre
                    if item.fabricante
                    else item.nombre
                )
                item.numero_inventario = generar_numero_inventario(
                    lugar=getattr(item, "lugar", None),
                    descriptor=descriptor,
                    referencia=item.numero_serie,
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Estadísticas para las tarjetas
        context["total_monitores"] = Monitor.objects.count()
        context["monitores_activos"] = Monitor.objects.filter(
            estado__nombre="Activo"
        ).count()
        context["monitores_mantenimiento"] = Monitor.objects.filter(
            estado__nombre="Mantenimiento"
        ).count()
        context["monitores_inactivos"] = Monitor.objects.filter(
            estado__nombre="Inactivo"
        ).count()

        # Catálogos para filtros dinámicos
        context["estados"] = Estado.objects.all().order_by("nombre")
        context["tipos"] = TipoMonitor.objects.all().order_by("nombre")

        self.agregar_contexto_lugar(context)

        return context


class MonitorDetailView(DetailView):
    """Vista de detalle de un monitor"""

    model = Monitor
    template_name = "inventario/monitor_detail.html"
    context_object_name = "object"

    def get_queryset(self):
        return Monitor.objects.select_related(
            "estado",
            "lugar",
            "tipo_monitor",
            "fabricante",
            "modelo",
            "proveedor",
            "tipo_garantia",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agregar bitácoras recientes del dispositivo
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="monitor", dispositivo_id=self.object.pk
        ).order_by("-fecha_evento")[:10]

        return context


class MonitorCreateView(CreateView):
    """Vista para crear un nuevo monitor"""

    model = Monitor
    form_class = MonitorForm
    template_name = "inventario/monitor_form.html"
    success_url = reverse_lazy("inventario:monitor_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "device_type": "monitor",
                "form_id": "monitorForm",
                "list_url": reverse("inventario:monitor_list"),
                "detail_url": None,
            }
        )
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Monitor "{form.instance.nombre}" creado exitosamente.',
        )
        return super().form_valid(form)


class MonitorUpdateView(RedirectToListMixin, UpdateView):
    """Vista para editar un monitor existente"""

    model = Monitor
    form_class = MonitorForm
    template_name = "inventario/monitor_form.html"
    success_url = reverse_lazy("inventario:monitor_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agregar bitácoras recientes del dispositivo
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="monitor", dispositivo_id=self.object.pk
        ).order_by("-fecha_evento")[:5]

        # Variables para el sistema de plantillas
        context.update(
            {
                "device_type": "monitor",
                "form_id": "monitorForm",
                "list_url": reverse("inventario:monitor_list"),
                "detail_url": reverse(
                    "inventario:monitor_detail",
                    kwargs={"pk": self.object.pk},
                ),
            }
        )

        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Monitor "{form.instance.nombre}" actualizado exitosamente.',
        )
        return super().form_valid(form)


class MonitorDeleteView(DeleteView):
    """Vista para eliminar un monitor"""

    model = Monitor
    success_url = reverse_lazy("inventario:monitor_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre
        messages.success(
            request,
            f'Monitor "{nombre}" eliminado exitosamente.',
        )
        return super().delete(request, *args, **kwargs)


# ============================================================================
# NETWORKING VIEWS
# ============================================================================


class NetworkingListView(MenuContextMixin, LugarFilterMixin, ListView):
    """Vista de lista para equipos de red"""

    model = Networking
    template_name = "inventario/networking_list.html"
    context_object_name = "object_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Networking.objects.select_related(
                "estado",
                "lugar",
                "tipo_networking",
                "fabricante",
                "modelo",
            )
            .all()
            .order_by("-fecha_creacion")
        )

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search)
                | Q(numero_inventario__icontains=search)
                | Q(numero_serie__icontains=search)
                | Q(fabricante__nombre__icontains=search)
                | Q(modelo__nombre__icontains=search)
            )

        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado__nombre=estado)

        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo_networking__nombre=tipo)

        queryset = self.aplicar_filtro_lugar(queryset)

        for item in queryset:
            if not item.numero_inventario:
                descriptor = (
                    item.modelo.nombre
                    if item.modelo
                    else item.tipo_networking.nombre
                    if item.tipo_networking
                    else item.fabricante.nombre
                    if item.fabricante
                    else item.nombre
                )
                item.numero_inventario = generar_numero_inventario(
                    lugar=getattr(item, "lugar", None),
                    descriptor=descriptor,
                    referencia=item.numero_serie,
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_networking"] = Networking.objects.count()
        context["networking_activos"] = Networking.objects.filter(
            estado__nombre="Activo"
        ).count()
        context["networking_mantenimiento"] = Networking.objects.filter(
            estado__nombre="Mantenimiento"
        ).count()
        context["networking_inactivos"] = Networking.objects.filter(
            estado__nombre="Inactivo"
        ).count()
        context["estados"] = Estado.objects.all().order_by("nombre")
        context["tipos"] = TipoNetworking.objects.all().order_by("nombre")

        self.agregar_contexto_lugar(context)
        return context


class NetworkingDetailView(DetailView):
    """Vista de detalle de un equipo de networking"""

    model = Networking
    template_name = "inventario/networking_detail.html"
    context_object_name = "object"

    def get_queryset(self):
        return Networking.objects.select_related(
            "estado",
            "lugar",
            "tipo_networking",
            "fabricante",
            "modelo",
            "proveedor",
            "tipo_garantia",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="networking",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:10]
        return context


class NetworkingCreateView(CreateView):
    """Vista para crear un equipo de networking"""

    model = Networking
    form_class = NetworkingForm
    template_name = "inventario/networking_form.html"
    success_url = reverse_lazy("inventario:networking_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "device_type": "networking",
                "form_id": "networkingForm",
                "list_url": reverse("inventario:networking_list"),
                "detail_url": None,
            }
        )
        return context

    def form_valid(self, form):
        nombre = form.instance.nombre
        mensaje = f'Equipo de networking "{nombre}" creado exitosamente.'
        messages.success(self.request, mensaje)
        return super().form_valid(form)


class NetworkingUpdateView(RedirectToListMixin, UpdateView):
    """Vista para editar un equipo de networking"""

    model = Networking
    form_class = NetworkingForm
    template_name = "inventario/networking_form.html"
    success_url = reverse_lazy("inventario:networking_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="networking",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:5]
        context.update(
            {
                "device_type": "networking",
                "form_id": "networkingForm",
                "list_url": reverse("inventario:networking_list"),
                "detail_url": reverse(
                    "inventario:networking_detail",
                    kwargs={"pk": self.object.pk},
                ),
            }
        )
        return context

    def form_valid(self, form):
        nombre = form.instance.nombre
        mensaje = f'Equipo de networking "{nombre}" actualizado exitosamente.'
        messages.success(self.request, mensaje)
        return super().form_valid(form)


class NetworkingDeleteView(DeleteView):
    """Vista para eliminar un equipo de networking"""

    model = Networking
    success_url = reverse_lazy("inventario:networking_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre
        mensaje = f'Equipo de networking "{nombre}" eliminado exitosamente.'
        messages.success(request, mensaje)
        return super().delete(request, *args, **kwargs)


# ============================================================================
# TELEFONIA VIEWS
# ============================================================================


class TelefoniaListView(MenuContextMixin, LugarFilterMixin, ListView):
    """Vista de lista para dispositivos de telefonía"""

    model = Telefonia
    template_name = "inventario/telefonia_list.html"
    context_object_name = "object_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Telefonia.objects.select_related(
                "estado",
                "lugar",
                "tipo_telefonia",
                "fabricante",
                "modelo",
            )
            .all()
            .order_by("-fecha_creacion")
        )

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search)
                | Q(numero_inventario__icontains=search)
                | Q(numero_serie__icontains=search)
                | Q(fabricante__nombre__icontains=search)
                | Q(modelo__nombre__icontains=search)
                | Q(extension_interna__icontains=search)
                | Q(numero_linea__icontains=search)
            )

        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado__nombre=estado)

        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo_telefonia__nombre=tipo)

        queryset = self.aplicar_filtro_lugar(queryset)

        for item in queryset:
            if not item.numero_inventario:
                descriptor = (
                    item.modelo.nombre
                    if item.modelo
                    else item.tipo_telefonia.nombre
                    if item.tipo_telefonia
                    else item.fabricante.nombre
                    if item.fabricante
                    else item.nombre
                )
                item.numero_inventario = generar_numero_inventario(
                    lugar=getattr(item, "lugar", None),
                    descriptor=descriptor,
                    referencia=item.numero_serie or item.numero_linea,
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_telefonia"] = Telefonia.objects.count()
        context["telefonia_activa"] = Telefonia.objects.filter(
            estado__nombre="Activo"
        ).count()
        context["telefonia_mantenimiento"] = Telefonia.objects.filter(
            estado__nombre="Mantenimiento"
        ).count()
        context["telefonia_inactiva"] = Telefonia.objects.filter(
            estado__nombre="Inactivo"
        ).count()
        context["estados"] = Estado.objects.all().order_by("nombre")
        context["tipos"] = TipoTelefonia.objects.all().order_by("nombre")

        self.agregar_contexto_lugar(context)
        return context


class TelefoniaDetailView(DetailView):
    """Vista de detalle para telefonía"""

    model = Telefonia
    template_name = "inventario/telefonia_detail.html"
    context_object_name = "object"

    def get_queryset(self):
        return Telefonia.objects.select_related(
            "estado",
            "lugar",
            "tipo_telefonia",
            "fabricante",
            "modelo",
            "proveedor",
            "tipo_garantia",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="telefonia",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:10]
        return context


class TelefoniaCreateView(CreateView):
    """Vista para crear un dispositivo de telefonía"""

    model = Telefonia
    form_class = TelefoniaForm
    template_name = "inventario/telefonia_form.html"
    success_url = reverse_lazy("inventario:telefonia_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "device_type": "telefonia",
                "form_id": "telefoniaForm",
                "list_url": reverse("inventario:telefonia_list"),
                "detail_url": None,
            }
        )
        return context

    def form_valid(self, form):
        nombre = form.instance.nombre
        mensaje = f'Dispositivo de telefonía "{nombre}" creado exitosamente.'
        messages.success(self.request, mensaje)
        return super().form_valid(form)


class TelefoniaUpdateView(RedirectToListMixin, UpdateView):
    """Vista para editar telefonía"""

    model = Telefonia
    form_class = TelefoniaForm
    template_name = "inventario/telefonia_form.html"
    success_url = reverse_lazy("inventario:telefonia_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="telefonia",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:5]
        context.update(
            {
                "device_type": "telefonia",
                "form_id": "telefoniaForm",
                "list_url": reverse("inventario:telefonia_list"),
                "detail_url": reverse(
                    "inventario:telefonia_detail",
                    kwargs={"pk": self.object.pk},
                ),
            }
        )
        return context

    def form_valid(self, form):
        nombre = form.instance.nombre
        mensaje = (
            f'Dispositivo de telefonía "{nombre}" actualizado ' "exitosamente."
        )
        messages.success(self.request, mensaje)
        return super().form_valid(form)


class TelefoniaDeleteView(DeleteView):
    """Vista para eliminar un dispositivo de telefonía"""

    model = Telefonia
    success_url = reverse_lazy("inventario:telefonia_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre
        mensaje = (
            f'Dispositivo de telefonía "{nombre}" ' "eliminado exitosamente."
        )
        messages.success(request, mensaje)
        return super().delete(request, *args, **kwargs)


# ============================================================================
# PERIFERICOS VIEWS
# ============================================================================


class PerifericoListView(MenuContextMixin, LugarFilterMixin, ListView):
    """Vista de lista para periféricos"""

    model = Periferico
    template_name = "inventario/periferico_list.html"
    context_object_name = "object_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Periferico.objects.select_related(
                "estado",
                "lugar",
                "tipo_periferico",
                "fabricante",
                "modelo",
            )
            .all()
            .order_by("-fecha_creacion")
        )

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search)
                | Q(numero_inventario__icontains=search)
                | Q(numero_serie__icontains=search)
                | Q(fabricante__nombre__icontains=search)
                | Q(modelo__nombre__icontains=search)
            )

        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado__nombre=estado)

        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo_periferico__nombre=tipo)

        queryset = self.aplicar_filtro_lugar(queryset)

        for item in queryset:
            if not item.numero_inventario:
                descriptor = (
                    item.modelo.nombre
                    if item.modelo
                    else item.tipo_periferico.nombre
                    if item.tipo_periferico
                    else item.fabricante.nombre
                    if item.fabricante
                    else item.nombre
                )
                item.numero_inventario = generar_numero_inventario(
                    lugar=getattr(item, "lugar", None),
                    descriptor=descriptor,
                    referencia=item.numero_serie,
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_perifericos"] = Periferico.objects.count()
        context["perifericos_activos"] = Periferico.objects.filter(
            estado__nombre="Activo"
        ).count()
        context["perifericos_mantenimiento"] = Periferico.objects.filter(
            estado__nombre="Mantenimiento"
        ).count()
        context["perifericos_inactivos"] = Periferico.objects.filter(
            estado__nombre="Inactivo"
        ).count()
        context["estados"] = Estado.objects.all().order_by("nombre")
        context["tipos"] = TipoPeriferico.objects.all().order_by("nombre")

        self.agregar_contexto_lugar(context)
        return context


class PerifericoDetailView(DetailView):
    """Vista de detalle para periféricos"""

    model = Periferico
    template_name = "inventario/periferico_detail.html"
    context_object_name = "object"

    def get_queryset(self):
        return Periferico.objects.select_related(
            "estado",
            "lugar",
            "tipo_periferico",
            "fabricante",
            "modelo",
            "proveedor",
            "tipo_garantia",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="periferico",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:10]
        return context


class PerifericoCreateView(CreateView):
    """Vista para crear un periférico"""

    model = Periferico
    form_class = PerifericoForm
    template_name = "inventario/periferico_form.html"
    success_url = reverse_lazy("inventario:periferico_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "device_type": "periferico",
                "form_id": "perifericoForm",
                "list_url": reverse("inventario:periferico_list"),
                "detail_url": None,
            }
        )
        return context

    def form_valid(self, form):
        nombre = form.instance.nombre
        mensaje = f'Periférico "{nombre}" creado exitosamente.'
        messages.success(self.request, mensaje)
        return super().form_valid(form)


class PerifericoUpdateView(RedirectToListMixin, UpdateView):
    """Vista para editar un periférico"""

    model = Periferico
    form_class = PerifericoForm
    template_name = "inventario/periferico_form.html"
    success_url = reverse_lazy("inventario:periferico_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="periferico",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:5]
        context.update(
            {
                "device_type": "periferico",
                "form_id": "perifericoForm",
                "list_url": reverse("inventario:periferico_list"),
                "detail_url": reverse(
                    "inventario:periferico_detail",
                    kwargs={"pk": self.object.pk},
                ),
            }
        )
        return context

    def form_valid(self, form):
        nombre = form.instance.nombre
        mensaje = f'Periférico "{nombre}" actualizado exitosamente.'
        messages.success(self.request, mensaje)
        return super().form_valid(form)


class PerifericoDeleteView(DeleteView):
    """Vista para eliminar un periférico"""

    model = Periferico
    success_url = reverse_lazy("inventario:periferico_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre
        mensaje = f'Periférico "{nombre}" eliminado exitosamente.'
        messages.success(request, mensaje)
        return super().delete(request, *args, **kwargs)


# ============================================================================
# TECNOLOGÍA MÉDICA VIEWS
# ============================================================================


class TecnologiaMedicaListView(MenuContextMixin, LugarFilterMixin, ListView):
    """Vista de lista para tecnología médica"""

    model = TecnologiaMedica
    template_name = "inventario/tecnologia_medica_list.html"
    context_object_name = "object_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            TecnologiaMedica.objects.select_related(
                "estado",
                "lugar",
                "tipo_tecnologia_medica",
                "fabricante",
                "modelo",
                "proveedor",
                "tipo_garantia",
            )
            .all()
            .order_by("-fecha_creacion")
        )

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search)
                | Q(numero_inventario__icontains=search)
                | Q(numero_serie__icontains=search)
                | Q(numero_activo_fijo__icontains=search)
                | Q(registro_sanitario__icontains=search)
                | Q(fabricante__nombre__icontains=search)
                | Q(modelo__nombre__icontains=search)
                | Q(area_aplicacion__icontains=search)
            )

        lugar_id = self.request.GET.get("lugar")
        if lugar_id:
            try:
                lugar = Lugares.objects.get(pk=lugar_id)
                descendientes_ids = [
                    desc.id for desc in lugar.obtener_descendientes(incluir_self=True)
                ]
                queryset = queryset.filter(lugar_id__in=descendientes_ids)
            except Lugares.DoesNotExist:
                pass

        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo_tecnologia_medica_id=tipo)

        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado_id=estado)

        clasificacion = self.request.GET.get("clasificacion_riesgo")
        if clasificacion:
            queryset = queryset.filter(clasificacion_riesgo=clasificacion)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "tipos": TipoTecnologiaMedica.objects.all(),
                "estados": Estado.objects.all(),
                "lugares": Lugares.obtener_raices(),
                "search": self.request.GET.get("search", ""),
                "selected_tipo": self.request.GET.get("tipo", ""),
                "selected_estado": self.request.GET.get("estado", ""),
                "selected_clasificacion": self.request.GET.get("clasificacion_riesgo", ""),
                "orden_servicio_tipos": OrdenServicio.TIPO_SERVICIO_CHOICES,
                "orden_servicio_prioridades": OrdenServicio.PRIORIDAD_CHOICES,
                "orden_servicio_default_solicitante": (
                    self.request.user.get_full_name() or self.request.user.get_username()
                ),
            }
        )
        return context


class TecnologiaMedicaDetailView(MenuContextMixin, DetailView):
    """Vista de detalle para tecnología médica"""

    model = TecnologiaMedica
    template_name = "inventario/tecnologia_medica_detail.html"
    context_object_name = "object"

    def get_queryset(self):
        return TecnologiaMedica.objects.select_related(
            "estado",
            "lugar",
            "tipo_tecnologia_medica",
            "fabricante",
            "modelo",
            "proveedor",
            "tipo_garantia",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras"] = Bitacora.objects.filter(
            tipo_dispositivo="tecnologia_medica",
            dispositivo_id=self.object.id
        ).order_by("-fecha_evento")[:10]
        return context


class TecnologiaMedicaCreateView(MenuContextMixin, CreateView):
    """Vista para crear un equipo de tecnología médica"""

    model = TecnologiaMedica
    form_class = TecnologiaMedicaForm
    template_name = "inventario/tecnologia_medica_form.html"
    success_url = reverse_lazy("inventario:tecnologia_medica_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Agregar Tecnología Médica",
                "submit_text": "Guardar",
                "tipos": TipoTecnologiaMedica.objects.all(),
                "estados": Estado.objects.all(),
                "lugares": Lugares.obtener_raices(),
            }
        )
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Equipo de tecnología médica "{form.instance.nombre}" '
            f'creado exitosamente.'
        )
        return super().form_valid(form)


class TecnologiaMedicaUpdateView(MenuContextMixin, RedirectToListMixin, UpdateView):
    """Vista para editar un equipo de tecnología médica"""

    model = TecnologiaMedica
    form_class = TecnologiaMedicaForm
    template_name = "inventario/tecnologia_medica_form.html"
    success_url = reverse_lazy("inventario:tecnologia_medica_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="tecnologia_medica",
            dispositivo_id=self.object.id
        ).order_by("-fecha_evento")[:5]
        context.update(
            {
                "title": f"Editar {self.object.nombre}",
                "submit_text": "Actualizar",
                "tipos": TipoTecnologiaMedica.objects.all(),
                "estados": Estado.objects.all(),
                "lugares": Lugares.obtener_raices(),
            }
        )
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Equipo de tecnología médica "{form.instance.nombre}" '
            f'actualizado exitosamente.'
        )
        return super().form_valid(form)


class TecnologiaMedicaDeleteView(DeleteView):
    """Vista para eliminar un equipo de tecnología médica"""

    model = TecnologiaMedica
    success_url = reverse_lazy("inventario:tecnologia_medica_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre
        mensaje = f'Equipo de tecnología médica "{nombre}" eliminado exitosamente.'
        messages.success(request, mensaje)
        return super().delete(request, *args, **kwargs)


# ============================================================================
# INSUMOS VIEWS
# ============================================================================


class InsumoListView(MenuContextMixin, ListView):
    """Vista de lista para insumos"""

    model = Insumo
    template_name = "inventario/insumo_list.html"
    context_object_name = "object_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = Insumo.objects.select_related(
            "tipo_insumo", "proveedor"
        ).all()

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search)
                | Q(tipo_insumo__nombre__icontains=search)
                | Q(proveedor__nombre__icontains=search)
            )

        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo_insumo__nombre=tipo)

        activo = self.request.GET.get("activo")
        if activo in {"si", "no"}:
            queryset = queryset.filter(activo=(activo == "si"))

        return queryset.order_by("nombre")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_insumos"] = Insumo.objects.count()
        context["insumos_activos"] = Insumo.objects.filter(activo=True).count()
        context["insumos_inactivos"] = Insumo.objects.filter(
            activo=False
        ).count()
        context["insumos_reorden"] = Insumo.objects.filter(
            cantidad_disponible__lte=F("punto_reorden")
        ).count()
        context["tipos"] = TipoInsumo.objects.all().order_by("nombre")
        return context


class InsumoDetailView(DetailView):
    """Vista de detalle para insumos"""

    model = Insumo
    template_name = "inventario/insumo_detail.html"
    context_object_name = "object"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="insumo",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:10]
        return context


class InsumoCreateView(CreateView):
    """Vista para crear un insumo"""

    model = Insumo
    form_class = InsumoForm
    template_name = "inventario/insumo_form.html"
    success_url = reverse_lazy("inventario:insumo_list")

    def get_context_data(self, **kwargs):
        from django.urls import reverse

        context = super().get_context_data(**kwargs)
        context.update(
            {
                "device_type": "insumo",
                "form_id": "insumoForm",
                "list_url": reverse("inventario:insumo_list"),
                "detail_url": None,
            }
        )
        return context

    def form_valid(self, form):
        nombre = form.instance.nombre
        mensaje = f'Insumo "{nombre}" creado exitosamente.'
        messages.success(self.request, mensaje)
        return super().form_valid(form)


class InsumoUpdateView(RedirectToListMixin, UpdateView):
    """Vista para editar un insumo"""

    model = Insumo
    form_class = InsumoForm
    template_name = "inventario/insumo_form.html"
    success_url = reverse_lazy("inventario:insumo_list")

    def get_context_data(self, **kwargs):
        from django.urls import reverse

        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="insumo",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:5]
        context.update(
            {
                "device_type": "insumo",
                "form_id": "insumoForm",
                "list_url": reverse("inventario:insumo_list"),
                "detail_url": reverse(
                    "inventario:insumo_detail",
                    kwargs={"pk": self.object.pk},
                ),
            }
        )
        return context

    def form_valid(self, form):
        nombre = form.instance.nombre
        mensaje = f'Insumo "{nombre}" actualizado exitosamente.'
        messages.success(self.request, mensaje)
        return super().form_valid(form)


class InsumoDeleteView(DeleteView):
    """Vista para eliminar un insumo"""

    model = Insumo
    success_url = reverse_lazy("inventario:insumo_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre
        mensaje = f'Insumo "{nombre}" eliminado exitosamente.'
        messages.success(request, mensaje)
        return super().delete(request, *args, **kwargs)


# ============================================================================
# SOFTWARE VIEWS
# ============================================================================


class SoftwareListView(MenuContextMixin, ListView):
    """Vista de lista para software"""

    model = Software
    template_name = "inventario/software_list.html"
    context_object_name = "object_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Software.objects.select_related(
                "estado",
                "tipo_software",
                "fabricante",
                "proveedor",
                "lugar",
            )
            .all()
            .order_by("-fecha_creacion")
        )

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search)
                | Q(numero_licencia__icontains=search)
                | Q(fabricante__nombre__icontains=search)
                | Q(proveedor__nombre__icontains=search)
            )

        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado__nombre=estado)

        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo_software__nombre=tipo)

        lugar = self.request.GET.get("lugar")
        if lugar:
            queryset = queryset.filter(lugar__nombre__icontains=lugar)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_software"] = Software.objects.count()
        context["software_activo"] = Software.objects.filter(
            estado__nombre="Activo"
        ).count()
        context["software_mantenimiento"] = Software.objects.filter(
            estado__nombre="Mantenimiento"
        ).count()
        context["software_inactivo"] = Software.objects.filter(
            estado__nombre="Inactivo"
        ).count()
        context["software_vencido"] = Software.objects.filter(
            fecha_expiracion__lt=timezone.now().date()
        ).count()
        context["estados"] = Estado.objects.all().order_by("nombre")
        context["tipos"] = TipoSoftware.objects.all().order_by("nombre")
        return context


class SoftwareDetailView(DetailView):
    """Vista de detalle para software"""

    model = Software
    template_name = "inventario/software_detail.html"
    context_object_name = "object"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="software",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:10]
        return context


class SoftwareCreateView(CreateView):
    """Vista para crear software"""

    model = Software
    form_class = SoftwareForm
    template_name = "inventario/software_form.html"
    success_url = reverse_lazy("inventario:software_list")

    def get_context_data(self, **kwargs):
        from django.urls import reverse

        context = super().get_context_data(**kwargs)
        context.update(
            {
                "device_type": "software",
                "form_id": "softwareForm",
                "list_url": reverse("inventario:software_list"),
                "detail_url": None,
            }
        )
        return context

    def form_valid(self, form):
        nombre = form.instance.nombre
        mensaje = f'Software "{nombre}" creado exitosamente.'
        messages.success(self.request, mensaje)
        return super().form_valid(form)


class SoftwareUpdateView(RedirectToListMixin, UpdateView):
    """Vista para editar software"""

    model = Software
    form_class = SoftwareForm
    template_name = "inventario/software_form.html"
    success_url = reverse_lazy("inventario:software_list")

    def get_context_data(self, **kwargs):
        from django.urls import reverse

        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="software",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:5]
        context.update(
            {
                "device_type": "software",
                "form_id": "softwareForm",
                "list_url": reverse("inventario:software_list"),
                "detail_url": reverse(
                    "inventario:software_detail",
                    kwargs={"pk": self.object.pk},
                ),
            }
        )
        return context

    def form_valid(self, form):
        nombre = form.instance.nombre
        mensaje = f'Software "{nombre}" actualizado exitosamente.'
        messages.success(self.request, mensaje)
        return super().form_valid(form)


class SoftwareDeleteView(DeleteView):
    """Vista para eliminar software"""

    model = Software
    success_url = reverse_lazy("inventario:software_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = self.object.nombre
        mensaje = f'Software "{nombre}" eliminado exitosamente.'
        messages.success(request, mensaje)
        return super().delete(request, *args, **kwargs)


# ============================================================================
# API VIEWS (Para funcionalidades AJAX)
# ============================================================================


def api_dashboard_stats(request):
    """API endpoint para obtener estadísticas del dashboard"""

    def estado_stats(model):
        return {
            "total": model.objects.count(),
            "activos": model.objects.filter(estado__nombre="Activo").count(),
            "mantenimiento": model.objects.filter(
                estado__nombre="Mantenimiento"
            ).count(),
            "inactivos": model.objects.filter(
                estado__nombre="Inactivo"
            ).count(),
        }

    stats = {
        "computadoras": estado_stats(Computadora),
        "impresoras": estado_stats(Impresora),
        "monitores": estado_stats(Monitor),
        "networking": estado_stats(Networking),
        "telefonia": estado_stats(Telefonia),
        "perifericos": estado_stats(Periferico),
        "software": {
            **estado_stats(Software),
            "vencidos": Software.objects.filter(
                fecha_expiracion__lt=timezone.now().date()
            ).count(),
        },
        "insumos": {
            "total": Insumo.objects.count(),
            "activos": Insumo.objects.filter(activo=True).count(),
            "inactivos": Insumo.objects.filter(activo=False).count(),
            "reorden": Insumo.objects.filter(
                cantidad_disponible__lte=F("punto_reorden")
            ).count(),
        },
    }

    return JsonResponse(stats)


def api_search_equipos(request):
    """API endpoint para búsqueda global de equipos"""
    query = request.GET.get("q", "")

    if len(query) < 2:
        return JsonResponse({"results": []})

    results = []
    from django.urls import reverse

    search_definitions = [
        {
            "tipo": "Computadora",
            "model": Computadora,
            "fields": [
                "nombre__icontains",
                "numero_inventario__icontains",
                "numero_serie__icontains",
            ],
            "url_name": "inventario:computadora_detail",
        },
        {
            "tipo": "Impresora",
            "model": Impresora,
            "fields": [
                "nombre__icontains",
                "numero_inventario__icontains",
                "numero_serie__icontains",
            ],
            "url_name": "inventario:impresora_detail",
        },
        {
            "tipo": "Monitor",
            "model": Monitor,
            "fields": [
                "nombre__icontains",
                "numero_inventario__icontains",
                "numero_serie__icontains",
            ],
            "url_name": "inventario:monitor_detail",
        },
        {
            "tipo": "Networking",
            "model": Networking,
            "fields": [
                "nombre__icontains",
                "numero_inventario__icontains",
                "numero_serie__icontains",
                "direccion_ip__icontains",
            ],
            "url_name": "inventario:networking_detail",
        },
        {
            "tipo": "Telefonía",
            "model": Telefonia,
            "fields": [
                "nombre__icontains",
                "numero_inventario__icontains",
                "numero_serie__icontains",
                "extension_interna__icontains",
                "numero_linea__icontains",
            ],
            "url_name": "inventario:telefonia_detail",
        },
        {
            "tipo": "Periférico",
            "model": Periferico,
            "fields": [
                "nombre__icontains",
                "numero_inventario__icontains",
                "numero_serie__icontains",
            ],
            "url_name": "inventario:periferico_detail",
        },
        {
            "tipo": "Insumo",
            "model": Insumo,
            "fields": [
                "nombre__icontains",
                "tipo_insumo__nombre__icontains",
            ],
            "url_name": "inventario:insumo_detail",
            "numero_attr": None,
        },
        {
            "tipo": "Software",
            "model": Software,
            "fields": [
                "nombre__icontains",
                "numero_licencia__icontains",
                "version__icontains",
            ],
            "url_name": "inventario:software_detail",
            "numero_attr": "numero_licencia",
        },
    ]

    for config in search_definitions:
        query_filter = Q()
        for lookup in config["fields"]:
            query_filter |= Q(**{lookup: query})

        queryset = config["model"].objects.filter(query_filter)[:5]

        numero_attr = config.get("numero_attr", "numero_inventario")

        for obj in queryset:
            numero_valor = getattr(obj, numero_attr, "") if numero_attr else ""
            results.append(
                {
                    "tipo": config["tipo"],
                    "nombre": obj.nombre,
                    "numero_inventario": numero_valor,
                    "url": reverse(config["url_name"], kwargs={"pk": obj.pk}),
                }
            )

    return JsonResponse({"results": results})


# Vistas de Bitácora

# Tipos de dispositivos para cada categoría
TIPOS_DISPOSITIVO_INFORMATICA = [
    'computadora',
    'impresora',
    'monitor',
    'networking',
    'telefonia',
    'periferico',
    'software',
    'insumo',
]

TIPOS_DISPOSITIVO_MEDICA = [
    'tecnologia_medica',
]


class BitacoraListView(ListView):
    """Vista genérica para mostrar bitácoras (mantener para compatibilidad)"""

    model = Bitacora
    template_name = "inventario/bitacora_list.html"
    context_object_name = "bitacoras"
    paginate_by = 50

    def get_queryset(self):
        queryset = Bitacora.objects.all()

        # Filtros
        tipo_dispositivo = self.request.GET.get("tipo_dispositivo")
        tipo_evento = self.request.GET.get("tipo_evento")
        dispositivo_nombre = self.request.GET.get("dispositivo_nombre")
        fecha_desde = self.request.GET.get("fecha_desde")
        fecha_hasta = self.request.GET.get("fecha_hasta")

        if tipo_dispositivo:
            queryset = queryset.filter(tipo_dispositivo=tipo_dispositivo)

        if tipo_evento:
            queryset = queryset.filter(tipo_evento=tipo_evento)

        if dispositivo_nombre:
            queryset = queryset.filter(
                dispositivo_nombre__icontains=dispositivo_nombre
            )

        if fecha_desde:
            try:
                fecha_desde_obj = datetime.strptime(fecha_desde, "%Y-%m-%d")
                queryset = queryset.filter(fecha_evento__gte=fecha_desde_obj)
            except ValueError:
                pass

        if fecha_hasta:
            try:
                fecha_hasta_obj = datetime.strptime(fecha_hasta, "%Y-%m-%d")
                # Agregar 23:59:59 para incluir todo el día
                fecha_hasta_obj = fecha_hasta_obj.replace(
                    hour=23,
                    minute=59,
                    second=59,
                )
                queryset = queryset.filter(fecha_evento__lte=fecha_hasta_obj)
            except ValueError:
                pass

        return queryset.order_by("-fecha_evento")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agregar opciones para filtros
        context["tipos_dispositivo"] = Bitacora.TIPO_DISPOSITIVO_CHOICES
        context["tipos_evento"] = Bitacora.TIPO_EVENTO_CHOICES

        # Mantener valores de filtros en el contexto
        context["filtros"] = {
            "tipo_dispositivo": self.request.GET.get("tipo_dispositivo", ""),
            "tipo_evento": self.request.GET.get("tipo_evento", ""),
            "dispositivo_nombre": self.request.GET.get(
                "dispositivo_nombre",
                "",
            ),
            "fecha_desde": self.request.GET.get("fecha_desde", ""),
            "fecha_hasta": self.request.GET.get("fecha_hasta", ""),
        }

        return context


class BitacoraListViewInformatica(MenuContextMixin, ListView):
    """Vista para mostrar bitácoras de activos informáticos"""

    model = Bitacora
    template_name = "inventario/bitacora_list.html"
    context_object_name = "bitacoras"
    paginate_by = 50

    def get_queryset(self):
        # Filtrar solo dispositivos de TI
        queryset = Bitacora.objects.filter(
            tipo_dispositivo__in=TIPOS_DISPOSITIVO_INFORMATICA
        )

        # Filtros adicionales
        tipo_dispositivo = self.request.GET.get("tipo_dispositivo")
        tipo_evento = self.request.GET.get("tipo_evento")
        dispositivo_nombre = self.request.GET.get("dispositivo_nombre")
        fecha_desde = self.request.GET.get("fecha_desde")
        fecha_hasta = self.request.GET.get("fecha_hasta")

        if tipo_dispositivo:
            # Asegurar que el filtro solo muestre tipos de TI
            if tipo_dispositivo in TIPOS_DISPOSITIVO_INFORMATICA:
                queryset = queryset.filter(tipo_dispositivo=tipo_dispositivo)

        if tipo_evento:
            queryset = queryset.filter(tipo_evento=tipo_evento)

        if dispositivo_nombre:
            queryset = queryset.filter(
                dispositivo_nombre__icontains=dispositivo_nombre
            )

        if fecha_desde:
            try:
                fecha_desde_obj = datetime.strptime(fecha_desde, "%Y-%m-%d")
                queryset = queryset.filter(fecha_evento__gte=fecha_desde_obj)
            except ValueError:
                pass

        if fecha_hasta:
            try:
                fecha_hasta_obj = datetime.strptime(fecha_hasta, "%Y-%m-%d")
                fecha_hasta_obj = fecha_hasta_obj.replace(
                    hour=23,
                    minute=59,
                    second=59,
                )
                queryset = queryset.filter(fecha_evento__lte=fecha_hasta_obj)
            except ValueError:
                pass

        return queryset.order_by("-fecha_evento")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Solo mostrar tipos de dispositivos de TI en los filtros
        context["tipos_dispositivo"] = [
            choice for choice in Bitacora.TIPO_DISPOSITIVO_CHOICES
            if choice[0] in TIPOS_DISPOSITIVO_INFORMATICA
        ]
        context["tipos_evento"] = Bitacora.TIPO_EVENTO_CHOICES
        context["bitacora_tipo"] = "informatica"
        context["bitacora_titulo"] = "Bitácora - Activos Informáticos"
        context["menu_type"] = "informatica"  # Forzar menú de TI

        # Mantener valores de filtros en el contexto
        context["filtros"] = {
            "tipo_dispositivo": self.request.GET.get("tipo_dispositivo", ""),
            "tipo_evento": self.request.GET.get("tipo_evento", ""),
            "dispositivo_nombre": self.request.GET.get(
                "dispositivo_nombre",
                "",
            ),
            "fecha_desde": self.request.GET.get("fecha_desde", ""),
            "fecha_hasta": self.request.GET.get("fecha_hasta", ""),
        }

        return context


class BitacoraListViewMedica(MenuContextMixin, ListView):
    """Vista para mostrar bitácoras de tecnología médica"""

    model = Bitacora
    template_name = "inventario/bitacora_list.html"
    context_object_name = "bitacoras"
    paginate_by = 50

    def get_queryset(self):
        # Filtrar solo dispositivos médicos
        queryset = Bitacora.objects.filter(
            tipo_dispositivo__in=TIPOS_DISPOSITIVO_MEDICA
        )

        # Filtros adicionales
        tipo_dispositivo = self.request.GET.get("tipo_dispositivo")
        tipo_evento = self.request.GET.get("tipo_evento")
        dispositivo_nombre = self.request.GET.get("dispositivo_nombre")
        fecha_desde = self.request.GET.get("fecha_desde")
        fecha_hasta = self.request.GET.get("fecha_hasta")

        if tipo_dispositivo:
            # Asegurar que el filtro solo muestre tipos médicos
            if tipo_dispositivo in TIPOS_DISPOSITIVO_MEDICA:
                queryset = queryset.filter(tipo_dispositivo=tipo_dispositivo)

        if tipo_evento:
            queryset = queryset.filter(tipo_evento=tipo_evento)

        if dispositivo_nombre:
            queryset = queryset.filter(
                dispositivo_nombre__icontains=dispositivo_nombre
            )

        if fecha_desde:
            try:
                fecha_desde_obj = datetime.strptime(fecha_desde, "%Y-%m-%d")
                queryset = queryset.filter(fecha_evento__gte=fecha_desde_obj)
            except ValueError:
                pass

        if fecha_hasta:
            try:
                fecha_hasta_obj = datetime.strptime(fecha_hasta, "%Y-%m-%d")
                fecha_hasta_obj = fecha_hasta_obj.replace(
                    hour=23,
                    minute=59,
                    second=59,
                )
                queryset = queryset.filter(fecha_evento__lte=fecha_hasta_obj)
            except ValueError:
                pass

        return queryset.order_by("-fecha_evento")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Solo mostrar tipos de dispositivos médicos en los filtros
        context["tipos_dispositivo"] = [
            choice for choice in Bitacora.TIPO_DISPOSITIVO_CHOICES
            if choice[0] in TIPOS_DISPOSITIVO_MEDICA
        ]
        context["tipos_evento"] = Bitacora.TIPO_EVENTO_CHOICES
        context["bitacora_tipo"] = "medica"
        context["bitacora_titulo"] = "Bitácora - Tecnología Médica"
        context["menu_type"] = "medica"  # Forzar menú de Tecnología Médica

        # Mantener valores de filtros en el contexto
        context["filtros"] = {
            "tipo_dispositivo": self.request.GET.get("tipo_dispositivo", ""),
            "tipo_evento": self.request.GET.get("tipo_evento", ""),
            "dispositivo_nombre": self.request.GET.get(
                "dispositivo_nombre",
                "",
            ),
            "fecha_desde": self.request.GET.get("fecha_desde", ""),
            "fecha_hasta": self.request.GET.get("fecha_hasta", ""),
        }

        return context


def bitacora_dispositivo(request, tipo_dispositivo, dispositivo_id):
    """Vista para mostrar la bitácora específica de un dispositivo"""

    # Validar tipo de dispositivo
    if tipo_dispositivo not in DEVICE_MODEL_MAP:
        messages.error(request, "Tipo de dispositivo no válido.")
        return redirect("inventario:dashboard")

    # Obtener el dispositivo según su tipo
    modelo = DEVICE_MODEL_MAP[tipo_dispositivo]
    dispositivo = get_object_or_404(modelo, pk=dispositivo_id)

    # Obtener bitácoras del dispositivo
    bitacoras = Bitacora.objects.filter(
        tipo_dispositivo=tipo_dispositivo, dispositivo_id=dispositivo_id
    ).order_by("-fecha_evento")

    # Paginación
    paginator = Paginator(bitacoras, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Determinar el tipo de bitácora según el dispositivo
    if tipo_dispositivo in TIPOS_DISPOSITIVO_INFORMATICA:
        bitacora_tipo = 'informatica'
        menu_type = 'informatica'
    elif tipo_dispositivo in TIPOS_DISPOSITIVO_MEDICA:
        bitacora_tipo = 'medica'
        menu_type = 'medica'
    else:
        bitacora_tipo = None
        menu_type = None

    context = {
        "dispositivo": dispositivo,
        "tipo_dispositivo": tipo_dispositivo,
        "tipo_dispositivo_label": DEVICE_LABELS.get(
            tipo_dispositivo,
            tipo_dispositivo,
        ),
        "bitacoras": page_obj,
        "page_obj": page_obj,
        "bitacora_tipo": bitacora_tipo,
        "menu_type": menu_type,
    }

    return render(request, "inventario/bitacora_dispositivo.html", context)


def registrar_evento_manual(request):
    """Vista para registrar eventos manuales en la bitácora"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            tipo_dispositivo = data.get("tipo_dispositivo")
            dispositivo_id = data.get("dispositivo_id")
            tipo_evento = data.get("tipo_evento")
            descripcion = data.get("descripcion")
            observaciones = data.get("observaciones", "")
            usuario = data.get("usuario", "Sistema")

            # Validar datos requeridos
            required = [
                tipo_dispositivo,
                dispositivo_id,
                tipo_evento,
                descripcion,
            ]
            if not all(required):
                return JsonResponse(
                    {"success": False, "error": "Faltan datos requeridos"}
                )

            # Obtener el dispositivo para validar que existe
            if tipo_dispositivo not in DEVICE_MODEL_MAP:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Tipo de dispositivo no válido",
                    }
                )
            modelo = DEVICE_MODEL_MAP[tipo_dispositivo]
            dispositivo = get_object_or_404(modelo, pk=dispositivo_id)

            # Registrar el evento
            Bitacora.registrar_evento(
                tipo_dispositivo=tipo_dispositivo,
                dispositivo_obj=dispositivo,
                tipo_evento=tipo_evento,
                descripcion=descripcion,
                observaciones=observaciones,
                usuario=usuario,
            )

            return JsonResponse(
                {"success": True, "message": "Evento registrado exitosamente"}
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método no permitido"})


def historico_remitos(request):
    """Vista para mostrar el historial de remitos/facturas emitidos."""
    # Obtener todas las facturas ordenadas por fecha descendente (más recientes primero)
    facturas_list = Factura.objects.select_related(
        'lugar_destino', 'lugar_origen'
    ).prefetch_related('activos').order_by('-fecha_emision')
    
    # Filtros opcionales
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    lugar_destino = request.GET.get('lugar_destino')
    
    if fecha_desde:
        try:
            fecha_desde_parsed = parse_date(fecha_desde)
            if fecha_desde_parsed:
                facturas_list = facturas_list.filter(fecha_emision__gte=fecha_desde_parsed)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_parsed = parse_date(fecha_hasta)
            if fecha_hasta_parsed:
                # Agregar un día para incluir todo el día hasta
                fecha_hasta_parsed = datetime.combine(fecha_hasta_parsed, datetime.max.time())
                facturas_list = facturas_list.filter(fecha_emision__lte=fecha_hasta_parsed)
        except ValueError:
            pass
    
    if lugar_destino:
        facturas_list = facturas_list.filter(lugar_destino_id=lugar_destino)
    
    # Paginación
    paginator = Paginator(facturas_list, 20)  # 20 facturas por página
    page_number = request.GET.get('page')
    facturas = paginator.get_page(page_number)
    
    # Obtener todos los lugares para el filtro
    lugares = Lugares.objects.all().order_by('nombre')
    
    # Obtener modo de vista (tarjetas o lista)
    vista = request.GET.get('vista', 'lista')  # Por defecto lista
    
    context = {
        'facturas': facturas,
        'lugares': lugares,
        'fecha_desde': fecha_desde or '',
        'fecha_hasta': fecha_hasta or '',
        'lugar_destino': lugar_destino or '',
        'vista': vista,
    }
    
    return render(request, 'inventario/historico_remitos.html', context)


# ============================================================================
# ÓRDENES DE SERVICIO VIEWS
# ============================================================================


class OrdenServicioListView(ListView):
    """Vista de lista para órdenes de servicio"""

    model = OrdenServicio
    template_name = "inventario/orden_servicio_list.html"
    context_object_name = "object_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = OrdenServicio.objects.all().order_by("-fecha_solicitud")

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(numero_orden__icontains=search)
                | Q(dispositivo_nombre__icontains=search)
                | Q(dispositivo_numero_serie__icontains=search)
                | Q(solicitante__icontains=search)
                | Q(tecnico_asignado__icontains=search)
                | Q(descripcion_problema__icontains=search)
            )

        tipo_servicio = self.request.GET.get("tipo_servicio")
        if tipo_servicio:
            queryset = queryset.filter(tipo_servicio=tipo_servicio)

        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado=estado)

        prioridad = self.request.GET.get("prioridad")
        if prioridad:
            queryset = queryset.filter(prioridad=prioridad)

        tipo_dispositivo = self.request.GET.get("tipo_dispositivo")
        if tipo_dispositivo:
            queryset = queryset.filter(tipo_dispositivo=tipo_dispositivo)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas
        ordenes = OrdenServicio.objects.all()
        context.update(
            {
                "total_ordenes": ordenes.count(),
                "ordenes_pendientes": ordenes.filter(estado='pendiente').count(),
                "ordenes_en_proceso": ordenes.filter(estado='en_proceso').count(),
                "ordenes_completadas": ordenes.filter(estado='completada').count(),
                "search": self.request.GET.get("search", ""),
                "selected_tipo_servicio": self.request.GET.get("tipo_servicio", ""),
                "selected_estado": self.request.GET.get("estado", ""),
                "selected_prioridad": self.request.GET.get("prioridad", ""),
                "selected_tipo_dispositivo": self.request.GET.get("tipo_dispositivo", ""),
            }
        )
        return context


class OrdenServicioDetailView(DetailView):
    """Vista de detalle para orden de servicio"""

    model = OrdenServicio
    template_name = "inventario/orden_servicio_detail.html"
    context_object_name = "orden"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el dispositivo relacionado
        device_models = {
            'computadora': Computadora,
            'impresora': Impresora,
            'monitor': Monitor,
            'networking': Networking,
            'telefonia': Telefonia,
            'periferico': Periferico,
            'tecnologia_medica': TecnologiaMedica,
            'insumo': Insumo,
            'software': Software,
        }
        
        model_class = device_models.get(self.object.tipo_dispositivo)
        dispositivo = None
        if model_class:
            try:
                dispositivo = model_class.objects.get(pk=self.object.dispositivo_id)
            except model_class.DoesNotExist:
                pass
        
        context["dispositivo"] = dispositivo
        return context


@login_required
def orden_servicio_pdf_view(request, pk: int) -> HttpResponse:
    """Genera y retorna el PDF imprimible de una orden de servicio."""
    orden = get_object_or_404(OrdenServicio, pk=pk)
    pdf_bytes = build_orden_servicio_pdf(orden)

    filename = f"orden-servicio-{orden.numero_orden}.pdf"
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f"inline; filename=\"{filename}\""
    return response


class OrdenServicioCreateView(CreateView):
    """Vista para crear una orden de servicio"""

    model = OrdenServicio
    form_class = OrdenServicioForm
    template_name = "inventario/orden_servicio_form.html"
    success_url = reverse_lazy("inventario:orden_servicio_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Crear Orden de Servicio",
                "submit_text": "Crear Orden",
            }
        )
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Orden de servicio "{form.instance.numero_orden}" creada exitosamente.'
        )
        return super().form_valid(form)


class OrdenServicioUpdateView(RedirectToListMixin, UpdateView):
    """Vista para editar una orden de servicio"""

    model = OrdenServicio
    form_class = OrdenServicioForm
    template_name = "inventario/orden_servicio_form.html"
    success_url = reverse_lazy("inventario:orden_servicio_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": f"Editar Orden {self.object.numero_orden}",
                "submit_text": "Actualizar",
            }
        )
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Orden de servicio "{form.instance.numero_orden}" actualizada exitosamente.'
        )
        return super().form_valid(form)


class OrdenServicioDeleteView(DeleteView):
    """Vista para eliminar una orden de servicio"""

    model = OrdenServicio
    success_url = reverse_lazy("inventario:orden_servicio_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        numero = self.object.numero_orden
        mensaje = f'Orden de servicio "{numero}" eliminada exitosamente.'
        messages.success(request, mensaje)
        return super().delete(request, *args, **kwargs)


# ============================================================================
# ACTIVOS GENERALES — DASHBOARD
# ============================================================================


@login_required
def dashboard_activos_generales(request):
    """Dashboard específico para Activos Generales (Mobiliario, Vehículos, Herramientas)."""
    today = timezone.now().date()
    limite_garantia = today + timedelta(days=30)

    asset_configs = [
        {
            "key": "mobiliario",
            "label": "Mobiliario",
            "model": Mobiliario,
            "icon": "bi-building",
            "gradient_class": "bg-mod-mobiliario",
            "list_url_name": "inventario:mobiliario_list",
            "create_url_name": "inventario:mobiliario_create",
            "detail_url_name": "inventario:mobiliario_detail",
            "has_estado": True,
        },
        {
            "key": "vehiculo",
            "label": "Vehículos",
            "model": Vehiculo,
            "icon": "bi-car-front",
            "gradient_class": "bg-mod-vehiculo",
            "list_url_name": "inventario:vehiculo_list",
            "create_url_name": "inventario:vehiculo_create",
            "detail_url_name": "inventario:vehiculo_detail",
            "has_estado": True,
        },
        {
            "key": "herramienta",
            "label": "Herramientas",
            "model": Herramienta,
            "icon": "bi-tools",
            "gradient_class": "bg-mod-herramienta",
            "list_url_name": "inventario:herramienta_list",
            "create_url_name": "inventario:herramienta_create",
            "detail_url_name": "inventario:herramienta_detail",
            "has_estado": True,
        },
    ]

    asset_summary = []
    for cfg in asset_configs:
        model = cfg["model"]
        total = model.objects.count()
        activos = model.objects.filter(estado__nombre="Activo").count() if cfg["has_estado"] else total
        mantenimiento = model.objects.filter(estado__nombre="Mantenimiento").count() if cfg["has_estado"] else 0
        garantia_proxima = model.objects.filter(
            fecha_finalizacion_garantia__gte=today,
            fecha_finalizacion_garantia__lte=limite_garantia,
        ).count()
        asset_summary.append({
            "key": cfg["key"],
            "label": cfg["label"],
            "icon": cfg["icon"],
            "gradient_class": cfg["gradient_class"],
            "total": total,
            "activos": activos,
            "mantenimiento": mantenimiento,
            "garantia_proxima": garantia_proxima,
            "list_url_name": cfg["list_url_name"],
            "create_url_name": cfg["create_url_name"],
        })

    # Activos con garantía próxima a vencer
    garantia_proxima_list = []
    for cfg in asset_configs:
        model = cfg["model"]
        items = model.objects.filter(
            fecha_finalizacion_garantia__gte=today,
            fecha_finalizacion_garantia__lte=limite_garantia,
        ).select_related("estado", "lugar")[:5]
        for item in items:
            garantia_proxima_list.append({
                "nombre": str(item),
                "tipo": cfg["label"],
                "fecha_finalizacion_garantia": item.fecha_finalizacion_garantia,
                "detail_url_name": cfg["detail_url_name"],
                "pk": item.pk,
            })

    context = {
        "menu_type": "generales",
        "asset_summary": asset_summary,
        "garantia_proxima_list": garantia_proxima_list,
        "total_activos_generales": sum(a["total"] for a in asset_summary),
    }
    return render(request, "inventario/dashboard_activos_generales.html", context)


# ============================================================================
# ACTIVOS GENERALES — MOBILIARIO
# ============================================================================


class MobiliarioListView(MenuContextMixin, LugarFilterMixin, ListView):
    """Vista de lista para mobiliario"""

    model = Mobiliario
    template_name = "inventario/mobiliario_list.html"
    context_object_name = "object_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Mobiliario.objects.select_related(
                "estado", "lugar", "tipo_mobiliario", "fabricante", "modelo",
            )
            .all()
            .order_by("-fecha_creacion")
        )

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search)
                | Q(numero_inventario__icontains=search)
                | Q(numero_serie__icontains=search)
                | Q(material__icontains=search)
                | Q(fabricante__nombre__icontains=search)
            )

        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado__nombre=estado)

        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo_mobiliario__nombre=tipo)

        queryset = self.aplicar_filtro_lugar(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_mobiliario"] = Mobiliario.objects.count()
        context["mobiliario_activo"] = Mobiliario.objects.filter(estado__nombre="Activo").count()
        context["mobiliario_mantenimiento"] = Mobiliario.objects.filter(estado__nombre="Mantenimiento").count()
        context["mobiliario_inactivo"] = Mobiliario.objects.filter(estado__nombre="Inactivo").count()
        context["estados"] = Estado.objects.all().order_by("nombre")
        context["tipos"] = TipoMobiliario.objects.all().order_by("nombre")
        self.agregar_contexto_lugar(context)
        return context


class MobiliarioDetailView(DetailView):
    """Vista de detalle para mobiliario"""

    model = Mobiliario
    template_name = "inventario/mobiliario_detail.html"
    context_object_name = "object"

    def get_queryset(self):
        return Mobiliario.objects.select_related(
            "estado", "lugar", "tipo_mobiliario", "fabricante", "modelo", "proveedor", "tipo_garantia",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="mobiliario",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:10]
        return context


class MobiliarioCreateView(CreateView):
    """Vista para crear mobiliario"""

    model = Mobiliario
    form_class = MobiliarioForm
    template_name = "inventario/mobiliario_form.html"
    success_url = reverse_lazy("inventario:mobiliario_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "device_type": "mobiliario",
            "form_id": "mobiliarioForm",
            "list_url": reverse("inventario:mobiliario_list"),
            "detail_url": None,
        })
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Mobiliario "{form.instance.nombre}" creado exitosamente.')
        return super().form_valid(form)


class MobiliarioUpdateView(RedirectToListMixin, UpdateView):
    """Vista para editar mobiliario"""

    model = Mobiliario
    form_class = MobiliarioForm
    template_name = "inventario/mobiliario_form.html"
    success_url = reverse_lazy("inventario:mobiliario_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="mobiliario",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:5]
        context.update({
            "device_type": "mobiliario",
            "form_id": "mobiliarioForm",
            "list_url": reverse("inventario:mobiliario_list"),
            "detail_url": reverse("inventario:mobiliario_detail", kwargs={"pk": self.object.pk}),
        })
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Mobiliario "{form.instance.nombre}" actualizado exitosamente.')
        return super().form_valid(form)


class MobiliarioDeleteView(DeleteView):
    """Vista para eliminar mobiliario"""

    model = Mobiliario
    success_url = reverse_lazy("inventario:mobiliario_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f'Mobiliario "{self.object.nombre}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# ACTIVOS GENERALES — VEHÍCULOS
# ============================================================================


class VehiculoListView(MenuContextMixin, LugarFilterMixin, ListView):
    """Vista de lista para vehículos"""

    model = Vehiculo
    template_name = "inventario/vehiculo_list.html"
    context_object_name = "object_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Vehiculo.objects.select_related(
                "estado", "lugar", "tipo_vehiculo", "fabricante", "modelo",
            )
            .all()
            .order_by("-fecha_creacion")
        )

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search)
                | Q(numero_inventario__icontains=search)
                | Q(matricula__icontains=search)
                | Q(color__icontains=search)
                | Q(fabricante__nombre__icontains=search)
            )

        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado__nombre=estado)

        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo_vehiculo__nombre=tipo)

        queryset = self.aplicar_filtro_lugar(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_vehiculos"] = Vehiculo.objects.count()
        context["vehiculos_activos"] = Vehiculo.objects.filter(estado__nombre="Activo").count()
        context["vehiculos_mantenimiento"] = Vehiculo.objects.filter(estado__nombre="Mantenimiento").count()
        context["vehiculos_inactivos"] = Vehiculo.objects.filter(estado__nombre="Inactivo").count()
        context["estados"] = Estado.objects.all().order_by("nombre")
        context["tipos"] = TipoVehiculo.objects.all().order_by("nombre")
        self.agregar_contexto_lugar(context)
        return context


class VehiculoDetailView(DetailView):
    """Vista de detalle para vehículos"""

    model = Vehiculo
    template_name = "inventario/vehiculo_detail.html"
    context_object_name = "object"

    def get_queryset(self):
        return Vehiculo.objects.select_related(
            "estado", "lugar", "tipo_vehiculo", "fabricante", "modelo", "proveedor", "tipo_garantia",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="vehiculo",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:10]
        return context


class VehiculoCreateView(CreateView):
    """Vista para crear vehículos"""

    model = Vehiculo
    form_class = VehiculoForm
    template_name = "inventario/vehiculo_form.html"
    success_url = reverse_lazy("inventario:vehiculo_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "device_type": "vehiculo",
            "form_id": "vehiculoForm",
            "list_url": reverse("inventario:vehiculo_list"),
            "detail_url": None,
        })
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Vehículo "{form.instance.nombre}" creado exitosamente.')
        return super().form_valid(form)


class VehiculoUpdateView(RedirectToListMixin, UpdateView):
    """Vista para editar vehículos"""

    model = Vehiculo
    form_class = VehiculoForm
    template_name = "inventario/vehiculo_form.html"
    success_url = reverse_lazy("inventario:vehiculo_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="vehiculo",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:5]
        context.update({
            "device_type": "vehiculo",
            "form_id": "vehiculoForm",
            "list_url": reverse("inventario:vehiculo_list"),
            "detail_url": reverse("inventario:vehiculo_detail", kwargs={"pk": self.object.pk}),
        })
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Vehículo "{form.instance.nombre}" actualizado exitosamente.')
        return super().form_valid(form)


class VehiculoDeleteView(DeleteView):
    """Vista para eliminar vehículos"""

    model = Vehiculo
    success_url = reverse_lazy("inventario:vehiculo_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f'Vehículo "{self.object.nombre}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# ACTIVOS GENERALES — HERRAMIENTAS
# ============================================================================


class HerramientaListView(MenuContextMixin, LugarFilterMixin, ListView):
    """Vista de lista para herramientas"""

    model = Herramienta
    template_name = "inventario/herramienta_list.html"
    context_object_name = "object_list"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Herramienta.objects.select_related(
                "estado", "lugar", "tipo_herramienta", "fabricante", "modelo",
            )
            .all()
            .order_by("-fecha_creacion")
        )

        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search)
                | Q(numero_inventario__icontains=search)
                | Q(numero_serie__icontains=search)
                | Q(fabricante__nombre__icontains=search)
            )

        estado = self.request.GET.get("estado")
        if estado:
            queryset = queryset.filter(estado__nombre=estado)

        tipo = self.request.GET.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo_herramienta__nombre=tipo)

        calibracion = self.request.GET.get("calibracion")
        if calibracion == "1":
            queryset = queryset.filter(requiere_calibracion=True)

        queryset = self.aplicar_filtro_lugar(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_herramientas"] = Herramienta.objects.count()
        context["herramientas_activas"] = Herramienta.objects.filter(estado__nombre="Activo").count()
        context["herramientas_mantenimiento"] = Herramienta.objects.filter(estado__nombre="Mantenimiento").count()
        context["herramientas_inactivas"] = Herramienta.objects.filter(estado__nombre="Inactivo").count()
        context["herramientas_calibracion"] = Herramienta.objects.filter(requiere_calibracion=True).count()
        context["estados"] = Estado.objects.all().order_by("nombre")
        context["tipos"] = TipoHerramienta.objects.all().order_by("nombre")
        self.agregar_contexto_lugar(context)
        return context


class HerramientaDetailView(DetailView):
    """Vista de detalle para herramientas"""

    model = Herramienta
    template_name = "inventario/herramienta_detail.html"
    context_object_name = "object"

    def get_queryset(self):
        return Herramienta.objects.select_related(
            "estado", "lugar", "tipo_herramienta", "fabricante", "modelo", "proveedor", "tipo_garantia",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="herramienta",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:10]
        return context


class HerramientaCreateView(CreateView):
    """Vista para crear herramientas"""

    model = Herramienta
    form_class = HerramientaForm
    template_name = "inventario/herramienta_form.html"
    success_url = reverse_lazy("inventario:herramienta_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "device_type": "herramienta",
            "form_id": "herramientaForm",
            "list_url": reverse("inventario:herramienta_list"),
            "detail_url": None,
        })
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Herramienta "{form.instance.nombre}" creada exitosamente.')
        return super().form_valid(form)


class HerramientaUpdateView(RedirectToListMixin, UpdateView):
    """Vista para editar herramientas"""

    model = Herramienta
    form_class = HerramientaForm
    template_name = "inventario/herramienta_form.html"
    success_url = reverse_lazy("inventario:herramienta_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bitacoras_recientes"] = Bitacora.objects.filter(
            tipo_dispositivo="herramienta",
            dispositivo_id=self.object.pk,
        ).order_by("-fecha_evento")[:5]
        context.update({
            "device_type": "herramienta",
            "form_id": "herramientaForm",
            "list_url": reverse("inventario:herramienta_list"),
            "detail_url": reverse("inventario:herramienta_detail", kwargs={"pk": self.object.pk}),
        })
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Herramienta "{form.instance.nombre}" actualizada exitosamente.')
        return super().form_valid(form)


class HerramientaDeleteView(DeleteView):
    """Vista para eliminar herramientas"""

    model = Herramienta
    success_url = reverse_lazy("inventario:herramienta_list")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.success(request, f'Herramienta "{self.object.nombre}" eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)
