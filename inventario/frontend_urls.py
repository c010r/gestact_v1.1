from django.urls import path
from . import frontend_views

app_name = 'inventario'

urlpatterns = [
    # Dashboard
    path('', frontend_views.dashboard, name='dashboard'),
    path('admin-panel/', frontend_views.dashboard_administrador, name='dashboard_admin'),
    
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
    
    # API endpoints
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

    # ──────────────────────────────────────────────
    # Activos Generales
    # ──────────────────────────────────────────────
    path(
        'generales/',
        frontend_views.dashboard_activos_generales,
        name='dashboard_generales',
    ),

    # Mobiliario
    path('mobiliario/', frontend_views.MobiliarioListView.as_view(), name='mobiliario_list'),
    path('mobiliario/<int:pk>/', frontend_views.MobiliarioDetailView.as_view(), name='mobiliario_detail'),
    path('mobiliario/crear/', frontend_views.MobiliarioCreateView.as_view(), name='mobiliario_create'),
    path('mobiliario/<int:pk>/editar/', frontend_views.MobiliarioUpdateView.as_view(), name='mobiliario_update'),
    path('mobiliario/<int:pk>/eliminar/', frontend_views.MobiliarioDeleteView.as_view(), name='mobiliario_delete'),

    # Vehículos
    path('vehiculos/', frontend_views.VehiculoListView.as_view(), name='vehiculo_list'),
    path('vehiculos/<int:pk>/', frontend_views.VehiculoDetailView.as_view(), name='vehiculo_detail'),
    path('vehiculos/crear/', frontend_views.VehiculoCreateView.as_view(), name='vehiculo_create'),
    path('vehiculos/<int:pk>/editar/', frontend_views.VehiculoUpdateView.as_view(), name='vehiculo_update'),
    path('vehiculos/<int:pk>/eliminar/', frontend_views.VehiculoDeleteView.as_view(), name='vehiculo_delete'),

    # Herramientas
    path('herramientas/', frontend_views.HerramientaListView.as_view(), name='herramienta_list'),
    path('herramientas/<int:pk>/', frontend_views.HerramientaDetailView.as_view(), name='herramienta_detail'),
    path('herramientas/crear/', frontend_views.HerramientaCreateView.as_view(), name='herramienta_create'),
    path('herramientas/<int:pk>/editar/', frontend_views.HerramientaUpdateView.as_view(), name='herramienta_update'),
    path('herramientas/<int:pk>/eliminar/', frontend_views.HerramientaDeleteView.as_view(), name='herramienta_delete'),
]
