from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import frontend_views
from . import views_facturacion
from . import views_servicio_proveedor

# Crear el router para las vistas de la API
router = DefaultRouter()
router.register(r'modulos-visibles', views.ModulosVisiblesViewSet)
router.register(r'unidades-ejecutoras', views.UnidadEjecutoraViewSet)
router.register(r'unidades-asistenciales', views.UnidadAsistencialViewSet)
router.register(r'servicios-ue', views.ServicioUEViewSet)
router.register(r'tipos-garantia', views.TipoGarantiaViewSet)
router.register(r'estados', views.EstadoViewSet)
router.register(r'lugares', views.LugaresViewSet)
router.register(r'tipos-computadora', views.TipoComputadoraViewSet)
router.register(r'fabricantes', views.FabricanteViewSet)
router.register(r'modelos', views.ModeloViewSet)
router.register(r'proveedores', views.ProveedorViewSet)
router.register(r'computadoras', views.ComputadoraViewSet)
router.register(r'tipos-impresora', views.TipoImpresoraViewSet)
router.register(r'impresoras', views.ImpresoraViewSet)
router.register(r'tipos-monitor', views.TipoMonitorViewSet)
router.register(r'monitores', views.MonitorViewSet)
router.register(r'plantillas-dispositivo', views.PlantillaDispositivoViewSet)
router.register(r'tipos-networking', views.TipoNetworkingViewSet)
router.register(r'networking', views.NetworkingViewSet)
router.register(r'tipos-telefonia', views.TipoTelefoniaViewSet)
router.register(r'telefonia', views.TelefoniaViewSet)
router.register(r'tipos-periferico', views.TipoPerifericoViewSet)
router.register(r'perifericos', views.PerifericoViewSet)
router.register(r'tipos-tecnologia-medica', views.TipoTecnologiaMedicaViewSet)
router.register(r'tecnologia-medica', views.TecnologiaMedicaViewSet)
router.register(r'tipos-insumo', views.TipoInsumoViewSet)
router.register(r'insumos', views.InsumoViewSet)
router.register(r'tipos-software', views.TipoSoftwareViewSet)
router.register(r'software', views.SoftwareViewSet)
router.register(r'ordenes-servicio', views.OrdenServicioViewSet)
router.register(r'tipos-mobiliario', views.TipoMobiliarioViewSet)
router.register(r'mobiliario', views.MobiliarioViewSet)
router.register(r'tipos-vehiculo', views.TipoVehiculoViewSet)
router.register(r'vehiculos', views.VehiculoViewSet)
router.register(r'tipos-herramienta', views.TipoHerramientaViewSet)
router.register(r'herramientas', views.HerramientaViewSet)

app_name = 'inventario'

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    path(
        'api/facturacion/agregar/',
        views_facturacion.agregar_activo,
        name='facturacion_agregar',
    ),
    path(
        'api/facturacion/remover/',
        views_facturacion.remover_activo,
        name='facturacion_remover',
    ),
    path(
        'api/facturacion/obtener/',
        views_facturacion.obtener_carrito,
        name='facturacion_obtener',
    ),
    path(
        'api/facturacion/actualizar/',
        views_facturacion.actualizar_carrito,
        name='facturacion_actualizar',
    ),
    path(
        'api/facturacion/limpiar/',
        views_facturacion.limpiar_carrito,
        name='facturacion_limpiar',
    ),
    path(
        'api/facturacion/emitir/',
        views_facturacion.emitir_factura,
        name='facturacion_emitir',
    ),
    path(
        'api/facturacion/descargar/<int:factura_id>/',
        views_facturacion.descargar_factura,
        name='facturacion_descargar',
    ),
    
    # API URLs para Servicio de Proveedor
    path(
        'api/servicio-proveedor/agregar/',
        views_servicio_proveedor.agregar_activo,
        name='servicio_proveedor_agregar',
    ),
    path(
        'api/servicio-proveedor/remover/',
        views_servicio_proveedor.remover_activo,
        name='servicio_proveedor_remover',
    ),
    path(
        'api/servicio-proveedor/obtener/',
        views_servicio_proveedor.obtener_carrito,
        name='servicio_proveedor_obtener',
    ),
    path(
        'api/servicio-proveedor/actualizar/',
        views_servicio_proveedor.actualizar_carrito,
        name='servicio_proveedor_actualizar',
    ),
    path(
        'api/servicio-proveedor/limpiar/',
        views_servicio_proveedor.limpiar_carrito,
        name='servicio_proveedor_limpiar',
    ),
    path(
        'api/servicio-proveedor/emitir/',
        views_servicio_proveedor.emitir_envio,
        name='servicio_proveedor_emitir',
    ),
    
    path(
        'remitos/historico/',
        frontend_views.historico_remitos,
        name='historico_remitos',
    ),
    
    # Frontend URLs
    # Dashboard Selector
    path('dashboard/', frontend_views.dashboard_selector, name='dashboard'),

    # Dashboards Específicos
    path(
        'admin-panel/',
        frontend_views.dashboard_administrador,
        name='dashboard_admin'
    ),
    path(
        'dashboard/informatica/',
        frontend_views.dashboard_activos_informaticos,
        name='dashboard_informatica'
    ),
    path(
        'dashboard/tecnologia-medica/',
        frontend_views.dashboard_tecnologia_medica,
        name='dashboard_medica'
    ),
    path(
        'dashboard/activos-generales/',
        frontend_views.dashboard_activos_generales,
        name='dashboard_generales'
    ),
    
    path('reportes/', frontend_views.reports_menu, name='reports_menu'),
    path(
        'reportes/empresarial/',
        frontend_views.reports_enterprise,
        name='reports_enterprise',
    ),
    path(
        'configuracion/lugares/',
        frontend_views.configuracion_lugares,
        name='configuracion_lugares',
    ),
    
    # Computadoras
    path(
        'computadoras/',
        frontend_views.ComputadoraListView.as_view(),
        name='computadora_list',
    ),
    path(
        'computadoras/<int:pk>/',
        frontend_views.ComputadoraDetailView.as_view(),
        name='computadora_detail',
    ),
    path(
        'computadoras/crear/',
        frontend_views.ComputadoraCreateView.as_view(),
        name='computadora_create',
    ),
    path(
        'computadoras/<int:pk>/editar/',
        frontend_views.ComputadoraUpdateView.as_view(),
        name='computadora_update',
    ),
    path(
        'computadoras/<int:pk>/eliminar/',
        frontend_views.ComputadoraDeleteView.as_view(),
        name='computadora_delete',
    ),
    
    # Impresoras
    path(
        'impresoras/',
        frontend_views.ImpresoraListView.as_view(),
        name='impresora_list',
    ),
    path(
        'impresoras/<int:pk>/',
        frontend_views.ImpresoraDetailView.as_view(),
        name='impresora_detail',
    ),
    path(
        'impresoras/crear/',
        frontend_views.ImpresoraCreateView.as_view(),
        name='impresora_create',
    ),
    path(
        'impresoras/<int:pk>/editar/',
        frontend_views.ImpresoraUpdateView.as_view(),
        name='impresora_update',
    ),
    path(
        'impresoras/<int:pk>/eliminar/',
        frontend_views.ImpresoraDeleteView.as_view(),
        name='impresora_delete',
    ),
    
    # Monitores
    path(
        'monitores/',
        frontend_views.MonitorListView.as_view(),
        name='monitor_list',
    ),
    path(
        'monitores/<int:pk>/',
        frontend_views.MonitorDetailView.as_view(),
        name='monitor_detail',
    ),
    path(
        'monitores/crear/',
        frontend_views.MonitorCreateView.as_view(),
        name='monitor_create',
    ),
    path(
        'monitores/<int:pk>/editar/',
        frontend_views.MonitorUpdateView.as_view(),
        name='monitor_update',
    ),
    path(
        'monitores/<int:pk>/eliminar/',
        frontend_views.MonitorDeleteView.as_view(),
        name='monitor_delete',
    ),

    # Networking
    path(
        'networking/',
        frontend_views.NetworkingListView.as_view(),
        name='networking_list',
    ),
    path(
        'networking/<int:pk>/',
        frontend_views.NetworkingDetailView.as_view(),
        name='networking_detail',
    ),
    path(
        'networking/crear/',
        frontend_views.NetworkingCreateView.as_view(),
        name='networking_create',
    ),
    path(
        'networking/<int:pk>/editar/',
        frontend_views.NetworkingUpdateView.as_view(),
        name='networking_update',
    ),
    path(
        'networking/<int:pk>/eliminar/',
        frontend_views.NetworkingDeleteView.as_view(),
        name='networking_delete',
    ),

    # Telefonía
    path(
        'telefonia/',
        frontend_views.TelefoniaListView.as_view(),
        name='telefonia_list',
    ),
    path(
        'telefonia/<int:pk>/',
        frontend_views.TelefoniaDetailView.as_view(),
        name='telefonia_detail',
    ),
    path(
        'telefonia/crear/',
        frontend_views.TelefoniaCreateView.as_view(),
        name='telefonia_create',
    ),
    path(
        'telefonia/<int:pk>/editar/',
        frontend_views.TelefoniaUpdateView.as_view(),
        name='telefonia_update',
    ),
    path(
        'telefonia/<int:pk>/eliminar/',
        frontend_views.TelefoniaDeleteView.as_view(),
        name='telefonia_delete',
    ),

    # Periféricos
    path(
        'perifericos/',
        frontend_views.PerifericoListView.as_view(),
        name='periferico_list',
    ),
    path(
        'perifericos/<int:pk>/',
        frontend_views.PerifericoDetailView.as_view(),
        name='periferico_detail',
    ),
    path(
        'perifericos/crear/',
        frontend_views.PerifericoCreateView.as_view(),
        name='periferico_create',
    ),
    path(
        'perifericos/<int:pk>/editar/',
        frontend_views.PerifericoUpdateView.as_view(),
        name='periferico_update',
    ),
    path(
        'perifericos/<int:pk>/eliminar/',
        frontend_views.PerifericoDeleteView.as_view(),
        name='periferico_delete',
    ),

    # Tecnología Médica
    path(
        'tecnologia-medica/',
        frontend_views.TecnologiaMedicaListView.as_view(),
        name='tecnologia_medica_list',
    ),
    path(
        'tecnologia-medica/<int:pk>/',
        frontend_views.TecnologiaMedicaDetailView.as_view(),
        name='tecnologia_medica_detail',
    ),
    path(
        'tecnologia-medica/crear/',
        frontend_views.TecnologiaMedicaCreateView.as_view(),
        name='tecnologia_medica_create',
    ),
    path(
        'tecnologia-medica/<int:pk>/editar/',
        frontend_views.TecnologiaMedicaUpdateView.as_view(),
        name='tecnologia_medica_update',
    ),
    path(
        'tecnologia-medica/<int:pk>/eliminar/',
        frontend_views.TecnologiaMedicaDeleteView.as_view(),
        name='tecnologia_medica_delete',
    ),

    # Insumos
    path(
        'insumos/',
        frontend_views.InsumoListView.as_view(),
        name='insumo_list',
    ),
    path(
        'insumos/<int:pk>/',
        frontend_views.InsumoDetailView.as_view(),
        name='insumo_detail',
    ),
    path(
        'insumos/crear/',
        frontend_views.InsumoCreateView.as_view(),
        name='insumo_create',
    ),
    path(
        'insumos/<int:pk>/editar/',
        frontend_views.InsumoUpdateView.as_view(),
        name='insumo_update',
    ),
    path(
        'insumos/<int:pk>/eliminar/',
        frontend_views.InsumoDeleteView.as_view(),
        name='insumo_delete',
    ),

    # Software
    path(
        'software/',
        frontend_views.SoftwareListView.as_view(),
        name='software_list',
    ),
    path(
        'software/<int:pk>/',
        frontend_views.SoftwareDetailView.as_view(),
        name='software_detail',
    ),
    path(
        'software/crear/',
        frontend_views.SoftwareCreateView.as_view(),
        name='software_create',
    ),
    path(
        'software/<int:pk>/editar/',
        frontend_views.SoftwareUpdateView.as_view(),
        name='software_update',
    ),
    path(
        'software/<int:pk>/eliminar/',
        frontend_views.SoftwareDeleteView.as_view(),
        name='software_delete',
    ),

    # Órdenes de Servicio
    path(
        'ordenes-servicio/',
        frontend_views.OrdenServicioListView.as_view(),
        name='orden_servicio_list',
    ),
    path(
        'ordenes-servicio/<int:pk>/',
        frontend_views.OrdenServicioDetailView.as_view(),
        name='orden_servicio_detail',
    ),
    path(
        'ordenes-servicio/<int:pk>/pdf/',
        frontend_views.orden_servicio_pdf_view,
        name='orden_servicio_pdf',
    ),
    path(
        'ordenes-servicio/crear/',
        frontend_views.OrdenServicioCreateView.as_view(),
        name='orden_servicio_create',
    ),
    path(
        'ordenes-servicio/<int:pk>/editar/',
        frontend_views.OrdenServicioUpdateView.as_view(),
        name='orden_servicio_update',
    ),
    path(
        'ordenes-servicio/<int:pk>/eliminar/',
        frontend_views.OrdenServicioDeleteView.as_view(),
        name='orden_servicio_delete',
    ),
    
    # Mobiliario
    path(
        'mobiliario/',
        frontend_views.MobiliarioListView.as_view(),
        name='mobiliario_list',
    ),
    path(
        'mobiliario/<int:pk>/',
        frontend_views.MobiliarioDetailView.as_view(),
        name='mobiliario_detail',
    ),
    path(
        'mobiliario/crear/',
        frontend_views.MobiliarioCreateView.as_view(),
        name='mobiliario_create',
    ),
    path(
        'mobiliario/<int:pk>/editar/',
        frontend_views.MobiliarioUpdateView.as_view(),
        name='mobiliario_update',
    ),
    path(
        'mobiliario/<int:pk>/eliminar/',
        frontend_views.MobiliarioDeleteView.as_view(),
        name='mobiliario_delete',
    ),

    # Vehículos
    path(
        'vehiculos/',
        frontend_views.VehiculoListView.as_view(),
        name='vehiculo_list',
    ),
    path(
        'vehiculos/<int:pk>/',
        frontend_views.VehiculoDetailView.as_view(),
        name='vehiculo_detail',
    ),
    path(
        'vehiculos/crear/',
        frontend_views.VehiculoCreateView.as_view(),
        name='vehiculo_create',
    ),
    path(
        'vehiculos/<int:pk>/editar/',
        frontend_views.VehiculoUpdateView.as_view(),
        name='vehiculo_update',
    ),
    path(
        'vehiculos/<int:pk>/eliminar/',
        frontend_views.VehiculoDeleteView.as_view(),
        name='vehiculo_delete',
    ),

    # Herramientas
    path(
        'herramientas/',
        frontend_views.HerramientaListView.as_view(),
        name='herramienta_list',
    ),
    path(
        'herramientas/<int:pk>/',
        frontend_views.HerramientaDetailView.as_view(),
        name='herramienta_detail',
    ),
    path(
        'herramientas/crear/',
        frontend_views.HerramientaCreateView.as_view(),
        name='herramienta_create',
    ),
    path(
        'herramientas/<int:pk>/editar/',
        frontend_views.HerramientaUpdateView.as_view(),
        name='herramienta_update',
    ),
    path(
        'herramientas/<int:pk>/eliminar/',
        frontend_views.HerramientaDeleteView.as_view(),
        name='herramienta_delete',
    ),

    # Bitácoras
    path(
        'bitacoras/',
        frontend_views.BitacoraListView.as_view(),
        name='bitacora_list',
    ),
    path(
        'bitacoras/informatica/',
        frontend_views.BitacoraListViewInformatica.as_view(),
        name='bitacora_list_informatica',
    ),
    path(
        'bitacoras/tecnologia-medica/',
        frontend_views.BitacoraListViewMedica.as_view(),
        name='bitacora_list_medica',
    ),
    path(
        'bitacoras/<str:tipo_dispositivo>/<int:dispositivo_id>/',
        frontend_views.bitacora_dispositivo,
        name='bitacora_dispositivo',
    ),
    path(
        'api/registrar-evento/',
        frontend_views.registrar_evento_manual,
        name='registrar_evento_manual',
    ),
    
    # API endpoints para funcionalidades AJAX
    path(
        'api/dashboard-stats/',
        frontend_views.api_dashboard_stats,
        name='api_dashboard_stats',
    ),
    path(
        'api/search/',
        frontend_views.api_search_equipos,
        name='api_search_equipos',
    ),
]
