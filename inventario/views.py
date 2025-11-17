from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)
from .models import (
    ModulosVisibles, UnidadEjecutora, UnidadAsistencial, ServicioUE,
    TipoGarantia, Estado, Lugares, TipoComputadora, Fabricante,
    Modelo, Proveedor, Computadora, TipoImpresora, Impresora,
    TipoMonitor, Monitor, PlantillaDispositivo, TipoNetworking,
    Networking, TipoTelefonia, Telefonia, TipoPeriferico, Periferico,
    TipoTecnologiaMedica, TecnologiaMedica,
    TipoInsumo, Insumo, TipoSoftware, Software, OrdenServicio
)
from .serializers import (
    ModulosVisiblesSerializer, UnidadEjecutoraSerializer, UnidadAsistencialSerializer,
    ServicioUESerializer, TipoGarantiaSerializer, EstadoSerializer, LugaresSerializer,
    TipoComputadoraSerializer, FabricanteSerializer, ModeloSerializer, ProveedorSerializer,
    ComputadoraSerializer, ComputadoraListSerializer, TipoImpresoraSerializer,
    ImpresoraSerializer, ImpresoraListSerializer, TipoMonitorSerializer,
    MonitorSerializer, MonitorListSerializer, PlantillaDispositivoSerializer,
    TipoNetworkingSerializer, NetworkingSerializer, NetworkingListSerializer,
    TipoTelefoniaSerializer, TelefoniaSerializer, TelefoniaListSerializer,
    TipoPerifericoSerializer, PerifericoSerializer, PerifericoListSerializer,
    TipoTecnologiaMedicaSerializer, TecnologiaMedicaSerializer, TecnologiaMedicaListSerializer,
    TipoInsumoSerializer, InsumoSerializer, InsumoListSerializer,
    TipoSoftwareSerializer, SoftwareSerializer, SoftwareListSerializer,
    OrdenServicioSerializer, OrdenServicioListSerializer
)


class ModulosVisiblesViewSet(viewsets.ModelViewSet):
    queryset = ModulosVisibles.objects.all()
    serializer_class = ModulosVisiblesSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class UnidadEjecutoraViewSet(viewsets.ModelViewSet):
    queryset = UnidadEjecutora.objects.all()
    serializer_class = UnidadEjecutoraSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'numero_ue']
    ordering_fields = ['nombre', 'numero_ue']
    ordering = ['nombre']


class UnidadAsistencialViewSet(viewsets.ModelViewSet):
    queryset = UnidadAsistencial.objects.all()
    serializer_class = UnidadAsistencialSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class ServicioUEViewSet(viewsets.ModelViewSet):
    queryset = ServicioUE.objects.all()
    serializer_class = ServicioUESerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class TipoGarantiaViewSet(viewsets.ModelViewSet):
    queryset = TipoGarantia.objects.all()
    serializer_class = TipoGarantiaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class EstadoViewSet(viewsets.ModelViewSet):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'comentarios']
    filterset_fields = ['visibilidad']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class LugaresViewSet(viewsets.ModelViewSet):
    queryset = Lugares.objects.select_related('padre', 'tipo_nivel').all()
    serializer_class = LugaresSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'codigo', 'comentarios', 'nombre_completo']
    filterset_fields = ['tipo_nivel', 'nivel', 'padre', 'activo']
    ordering_fields = ['nombre', 'nivel', 'tipo_nivel']
    ordering = ['nivel', 'nombre']


class TipoComputadoraViewSet(viewsets.ModelViewSet):
    queryset = TipoComputadora.objects.all()
    serializer_class = TipoComputadoraSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'comentarios']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class FabricanteViewSet(viewsets.ModelViewSet):
    queryset = Fabricante.objects.all()
    serializer_class = FabricanteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'sitio_web']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class ModeloViewSet(viewsets.ModelViewSet):
    queryset = Modelo.objects.select_related('fabricante').all()
    serializer_class = ModeloSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'fabricante__nombre']
    filterset_fields = ['fabricante']
    ordering_fields = ['nombre', 'fabricante__nombre']
    ordering = ['fabricante__nombre', 'nombre']


class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'email', 'telefono']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class ComputadoraViewSet(viewsets.ModelViewSet):
    queryset = Computadora.objects.select_related(
        'estado', 'lugar', 'tipo_computadora', 'fabricante', 
        'modelo', 'proveedor', 'tipo_garantia'
    ).all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = [
        'nombre', 'numero_serie', 'numero_inventario',
        'fabricante__nombre', 'modelo__nombre'
    ]
    filterset_fields = [
        'estado', 'tipo_computadora', 'fabricante', 
        'lugar__unidad_ejecutora', 'tipo_garantia'
    ]
    ordering_fields = [
        'nombre', 'numero_serie', 'fecha_adquisicion', 
        'fabricante__nombre', 'modelo__nombre'
    ]
    ordering = ['nombre']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ComputadoraListSerializer
        return ComputadoraSerializer
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Endpoint para obtener estadísticas básicas"""
        total = self.get_queryset().count()
        por_estado = {}
        for estado in Estado.objects.all():
            count = self.get_queryset().filter(estado=estado).count()
            por_estado[estado.nombre] = count
        
        return Response({
            'total_computadoras': total,
            'por_estado': por_estado,
            'con_garantia_vigente': self.get_queryset().filter(
                fecha_finalizacion_garantia__gte=timezone.now().date()
            ).count() if total > 0 else 0
        })
    
    @action(detail=True, methods=['post'])
    def vincular_monitor(self, request, pk=None):
        """Vincula un monitor a la computadora"""
        try:
            computadora = self.get_object()
            monitor_id = request.data.get('monitor_id')
            
            if not monitor_id:
                return Response({'error': 'ID del monitor es requerido'}, status=400)
            
            try:
                monitor = Monitor.objects.get(id=monitor_id)
            except Monitor.DoesNotExist:
                return Response({'error': 'Monitor no encontrado'}, status=404)
            
            if computadora.vincular_monitor(monitor):
                return Response({'message': f'Monitor {monitor.nombre} vinculado exitosamente'})
            else:
                return Response({'error': 'El monitor ya está vinculado a esta computadora'}, status=400)
                
        except Exception as e:
            logger.error(f"Error al vincular monitor: {str(e)}")
            return Response({'error': 'Error interno del servidor'}, status=500)
    
    @action(detail=True, methods=['post'])
    def desvincular_monitor(self, request, pk=None):
        """Desvincula un monitor de la computadora"""
        try:
            computadora = self.get_object()
            monitor_id = request.data.get('monitor_id')
            
            if not monitor_id:
                return Response({'error': 'ID del monitor es requerido'}, status=400)
            
            try:
                monitor = Monitor.objects.get(id=monitor_id)
            except Monitor.DoesNotExist:
                return Response({'error': 'Monitor no encontrado'}, status=404)
            
            if computadora.desvincular_monitor(monitor):
                return Response({'message': f'Monitor {monitor.nombre} desvinculado exitosamente'})
            else:
                return Response({'error': 'El monitor no está vinculado a esta computadora'}, status=400)
                
        except Exception as e:
            logger.error(f"Error al desvincular monitor: {str(e)}")
            return Response({'error': 'Error interno del servidor'}, status=500)
    
    @action(detail=True, methods=['post'])
    def vincular_impresora(self, request, pk=None):
        """Vincula una impresora a la computadora"""
        try:
            computadora = self.get_object()
            impresora_id = request.data.get('impresora_id')
            
            if not impresora_id:
                return Response({'error': 'ID de la impresora es requerido'}, status=400)
            
            try:
                impresora = Impresora.objects.get(id=impresora_id)
            except Impresora.DoesNotExist:
                return Response({'error': 'Impresora no encontrada'}, status=404)
            
            if computadora.vincular_impresora(impresora):
                return Response({'message': f'Impresora {impresora.nombre} vinculada exitosamente'})
            else:
                return Response({'error': 'La impresora ya está vinculada a esta computadora'}, status=400)
                
        except Exception as e:
            logger.error(f"Error al vincular impresora: {str(e)}")
            return Response({'error': 'Error interno del servidor'}, status=500)
    
    @action(detail=True, methods=['post'])
    def desvincular_impresora(self, request, pk=None):
        """Desvincula una impresora de la computadora"""
        try:
            computadora = self.get_object()
            impresora_id = request.data.get('impresora_id')
            
            if not impresora_id:
                return Response({'error': 'ID de la impresora es requerido'}, status=400)
            
            try:
                impresora = Impresora.objects.get(id=impresora_id)
            except Impresora.DoesNotExist:
                return Response({'error': 'Impresora no encontrada'}, status=404)
            
            if computadora.desvincular_impresora(impresora):
                return Response({'message': f'Impresora {impresora.nombre} desvinculada exitosamente'})
            else:
                return Response({'error': 'La impresora no está vinculada a esta computadora'}, status=400)
                
        except Exception as e:
            logger.error(f"Error al desvincular impresora: {str(e)}")
            return Response({'error': 'Error interno del servidor'}, status=500)
    
    @action(detail=True, methods=['get'])
    def dispositivos_vinculados(self, request, pk=None):
        """Obtiene todos los dispositivos vinculados a la computadora"""
        try:
            computadora = self.get_object()
            dispositivos = computadora.obtener_dispositivos_vinculados()
            
            # Serializar los datos
            from .serializers import MonitorListSerializer, ImpresoraListSerializer
            
            monitores_data = MonitorListSerializer(dispositivos['monitores'], many=True).data
            impresoras_data = ImpresoraListSerializer(dispositivos['impresoras'], many=True).data
            
            return Response({
                'monitores': monitores_data,
                'impresoras': impresoras_data,
                'total_monitores': dispositivos['total_monitores'],
                'total_impresoras': dispositivos['total_impresoras']
            })
            
        except Exception as e:
            logger.error(f"Error al obtener dispositivos vinculados: {str(e)}")
            return Response({'error': 'Error interno del servidor'}, status=500)


class TipoImpresoraViewSet(viewsets.ModelViewSet):
    queryset = TipoImpresora.objects.all()
    serializer_class = TipoImpresoraSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'comentarios']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class ImpresoraViewSet(viewsets.ModelViewSet):
    queryset = Impresora.objects.select_related(
        'estado', 'lugar', 'tipo_impresora', 'fabricante', 
        'modelo', 'proveedor', 'tipo_garantia'
    ).all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = [
        'nombre', 'numero_serie', 'numero_inventario',
        'fabricante__nombre', 'modelo__nombre'
    ]
    filterset_fields = [
        'estado', 'tipo_impresora', 'fabricante', 
        'lugar__unidad_ejecutora', 'tipo_garantia'
    ]
    ordering_fields = [
        'nombre', 'numero_serie', 'fecha_adquisicion', 
        'fabricante__nombre', 'modelo__nombre'
    ]
    ordering = ['nombre']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ImpresoraListSerializer
        return ImpresoraSerializer
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Endpoint para obtener estadísticas básicas"""
        total = self.get_queryset().count()
        por_estado = {}
        for estado in Estado.objects.all():
            count = self.get_queryset().filter(estado=estado).count()
            por_estado[estado.nombre] = count
        
        return Response({
            'total_impresoras': total,
            'por_estado': por_estado,
            'con_garantia_vigente': self.get_queryset().filter(
                fecha_finalizacion_garantia__gte=timezone.now().date()
            ).count() if total > 0 else 0
        })


class TipoMonitorViewSet(viewsets.ModelViewSet):
    queryset = TipoMonitor.objects.all()
    serializer_class = TipoMonitorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'comentarios']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class MonitorViewSet(viewsets.ModelViewSet):
    queryset = Monitor.objects.select_related(
        'estado', 'lugar', 'tipo_monitor', 'fabricante', 
        'modelo', 'proveedor', 'tipo_garantia'
    ).all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = [
        'nombre', 'numero_serie', 'numero_inventario',
        'fabricante__nombre', 'modelo__nombre'
    ]
    filterset_fields = [
        'estado', 'tipo_monitor', 'fabricante', 
        'lugar__unidad_ejecutora', 'tipo_garantia'
    ]
    ordering_fields = [
        'nombre', 'numero_serie', 'fecha_adquisicion', 
        'fabricante__nombre', 'modelo__nombre'
    ]
    ordering = ['nombre']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MonitorListSerializer
        return MonitorSerializer
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Endpoint para obtener estadísticas básicas"""
        total = self.get_queryset().count()
        por_estado = {}
        for estado in Estado.objects.all():
            count = self.get_queryset().filter(estado=estado).count()
            por_estado[estado.nombre] = count
        
        return Response({
            'total_monitores': total,
            'por_estado': por_estado,
            'con_garantia_vigente': self.get_queryset().filter(
                fecha_finalizacion_garantia__gte=timezone.now().date()
            ).count() if total > 0 else 0
        })


class PlantillaDispositivoViewSet(viewsets.ModelViewSet):
    queryset = PlantillaDispositivo.objects.select_related(
        'fabricante', 'modelo', 'lugar', 'estado', 'proveedor',
        'tipo_garantia', 'tipo_computadora', 'tipo_monitor', 'tipo_impresora'
    ).all()
    serializer_class = PlantillaDispositivoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'descripcion']
    filterset_fields = ['tipo_dispositivo']
    ordering_fields = ['nombre', 'fecha_creacion']
    ordering = ['-fecha_creacion']
    pagination_class = None  # Desactivar paginación para plantillas
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """Obtener plantillas agrupadas por tipo de dispositivo"""
        tipos = [
            'computadora',
            'impresora',
            'monitor',
            'networking',
            'telefonia',
            'periferico',
            'insumo',
            'software',
        ]
        resultado = {}
        
        for tipo in tipos:
            plantillas = self.get_queryset().filter(tipo_dispositivo=tipo)
            serializer = PlantillaDispositivoSerializer(
                plantillas,
                many=True,
            )
            resultado[tipo] = serializer.data
            
        return Response(resultado)


class TipoNetworkingViewSet(viewsets.ModelViewSet):
    queryset = TipoNetworking.objects.all()
    serializer_class = TipoNetworkingSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['nombre', 'comentarios']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class NetworkingViewSet(viewsets.ModelViewSet):
    queryset = Networking.objects.select_related(
        'estado', 'lugar', 'tipo_networking', 'fabricante',
        'modelo', 'proveedor', 'tipo_garantia'
    ).all()
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        'nombre', 'numero_serie', 'numero_inventario',
        'fabricante__nombre', 'modelo__nombre',
        'tipo_networking__nombre'
    ]
    filterset_fields = [
        'estado', 'tipo_networking', 'lugar__unidad_ejecutora',
        'tipo_garantia'
    ]
    ordering_fields = [
        'nombre', 'numero_serie', 'fecha_adquisicion',
        'fabricante__nombre', 'modelo__nombre'
    ]
    ordering = ['nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return NetworkingListSerializer
        return NetworkingSerializer


class TipoTelefoniaViewSet(viewsets.ModelViewSet):
    queryset = TipoTelefonia.objects.all()
    serializer_class = TipoTelefoniaSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['nombre', 'comentarios']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class TelefoniaViewSet(viewsets.ModelViewSet):
    queryset = Telefonia.objects.select_related(
        'estado', 'lugar', 'tipo_telefonia', 'fabricante',
        'modelo', 'proveedor', 'tipo_garantia'
    ).all()
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        'nombre', 'numero_serie', 'numero_inventario',
        'fabricante__nombre', 'modelo__nombre',
        'extension_interna', 'numero_linea'
    ]
    filterset_fields = [
        'estado', 'tipo_telefonia', 'lugar__unidad_ejecutora',
        'tipo_garantia'
    ]
    ordering_fields = [
        'nombre', 'numero_serie', 'fecha_adquisicion',
        'fabricante__nombre', 'modelo__nombre'
    ]
    ordering = ['nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return TelefoniaListSerializer
        return TelefoniaSerializer


class TipoPerifericoViewSet(viewsets.ModelViewSet):
    queryset = TipoPeriferico.objects.all()
    serializer_class = TipoPerifericoSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['nombre', 'comentarios']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class PerifericoViewSet(viewsets.ModelViewSet):
    queryset = Periferico.objects.select_related(
        'estado', 'lugar', 'tipo_periferico', 'fabricante',
        'modelo', 'proveedor', 'tipo_garantia'
    ).all()
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        'nombre', 'numero_serie', 'numero_inventario',
        'fabricante__nombre', 'modelo__nombre'
    ]
    filterset_fields = [
        'estado', 'tipo_periferico', 'lugar__unidad_ejecutora',
        'tipo_garantia', 'es_inalambrico'
    ]
    ordering_fields = [
        'nombre', 'numero_serie', 'fecha_adquisicion',
        'fabricante__nombre', 'modelo__nombre'
    ]
    ordering = ['nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return PerifericoListSerializer
        return PerifericoSerializer


class TipoTecnologiaMedicaViewSet(viewsets.ModelViewSet):
    queryset = TipoTecnologiaMedica.objects.all()
    serializer_class = TipoTecnologiaMedicaSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['nombre', 'comentarios']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class TecnologiaMedicaViewSet(viewsets.ModelViewSet):
    queryset = TecnologiaMedica.objects.select_related(
        'estado', 'lugar', 'tipo_tecnologia_medica', 'fabricante',
        'modelo', 'proveedor', 'tipo_garantia'
    ).all()
    serializer_class = TecnologiaMedicaSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        'nombre', 'numero_serie', 'numero_inventario',
        'numero_activo_fijo', 'registro_sanitario',
        'fabricante__nombre', 'modelo__nombre',
        'lugar__nombre', 'area_aplicacion'
    ]
    filterset_fields = [
        'estado', 'lugar', 'tipo_tecnologia_medica',
        'fabricante', 'proveedor', 'clasificacion_riesgo',
        'requiere_calibracion', 'requiere_mantenimiento_preventivo',
        'requiere_personal_especializado'
    ]
    ordering_fields = [
        'nombre', 'fecha_adquisicion', 'numero_inventario',
        'clasificacion_riesgo'
    ]
    ordering = ['nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return TecnologiaMedicaListSerializer
        return TecnologiaMedicaSerializer
    
    @action(detail=False, methods=['get'])
    def requieren_calibracion(self, request):
        """Retorna equipos que requieren calibración próxima"""
        equipos = [
            equipo for equipo in self.get_queryset() 
            if equipo.requiere_calibracion_proxima
        ]
        serializer = self.get_serializer(equipos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def requieren_mantenimiento(self, request):
        """Retorna equipos que requieren mantenimiento próximo"""
        equipos = [
            equipo for equipo in self.get_queryset() 
            if equipo.requiere_mantenimiento_proximo
        ]
        serializer = self.get_serializer(equipos, many=True)
        return Response(serializer.data)


class TipoInsumoViewSet(viewsets.ModelViewSet):
    queryset = TipoInsumo.objects.all()
    serializer_class = TipoInsumoSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['nombre', 'comentarios']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.select_related('tipo_insumo', 'proveedor').all()
    serializer_class = InsumoSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        'nombre', 'descripcion', 'tipo_insumo__nombre',
        'proveedor__nombre'
    ]
    filterset_fields = [
        'tipo_insumo', 'proveedor', 'activo'
    ]
    ordering_fields = [
        'nombre', 'cantidad_disponible', 'punto_reorden'
    ]
    ordering = ['nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return InsumoListSerializer
        return InsumoSerializer


class TipoSoftwareViewSet(viewsets.ModelViewSet):
    queryset = TipoSoftware.objects.all()
    serializer_class = TipoSoftwareSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['nombre', 'comentarios']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class SoftwareViewSet(viewsets.ModelViewSet):
    queryset = Software.objects.select_related(
        'estado', 'tipo_software', 'fabricante',
        'proveedor', 'lugar'
    ).all()
    serializer_class = SoftwareSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        'nombre', 'version', 'numero_licencia',
        'fabricante__nombre', 'proveedor__nombre'
    ]
    filterset_fields = [
        'estado', 'tipo_software', 'fabricante',
        'proveedor'
    ]
    ordering_fields = [
        'nombre', 'version', 'fecha_adquisicion',
        'fecha_expiracion'
    ]
    ordering = ['nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return SoftwareListSerializer
        return SoftwareSerializer
    
    @action(detail=True, methods=['post'])
    def aplicar_a_dispositivo(self, request, pk=None):
        """Aplicar plantilla a un nuevo dispositivo"""
        plantilla = self.get_object()
        tipo_dispositivo = request.data.get('tipo_dispositivo')
        
        if tipo_dispositivo and tipo_dispositivo != plantilla.tipo_dispositivo:
            return Response(
                {
                    'error': (
                        'El tipo de dispositivo no coincide con la '
                        'plantilla'
                    )
                },
                status=400
            )
        
        # Crear datos base desde la plantilla
        campos_comunes = [
            'estado', 'lugar', 'fabricante', 'modelo', 'proveedor',
            'tipo_garantia', 'anos_garantia', 'valor_adquisicion',
            'comentarios'
        ]
        
        datos_dispositivo = {}
        
        # Aplicar campos comunes
        for campo in campos_comunes:
            valor = getattr(plantilla, campo)
            if valor is not None:
                if hasattr(valor, 'id'):
                    datos_dispositivo[campo] = valor.id
                    datos_dispositivo[f'{campo}_nombre'] = str(valor)
                else:
                    datos_dispositivo[campo] = valor
        
        # Aplicar campos específicos según el tipo de dispositivo
        if plantilla.tipo_dispositivo == 'computadora':
            campos_especificos = [
                'tipo_computadora',
                'direccion_ip',
                'direccion_mac',
            ]
        elif plantilla.tipo_dispositivo == 'impresora':
            campos_especificos = ['tipo_impresora']
        elif plantilla.tipo_dispositivo == 'monitor':
            campos_especificos = ['tipo_monitor']
        else:
            campos_especificos = []
        
        for campo in campos_especificos:
            valor = getattr(plantilla, campo)
            if valor is not None:
                if hasattr(valor, 'id'):
                    datos_dispositivo[campo] = valor.id
                    datos_dispositivo[f'{campo}_nombre'] = str(valor)
                else:
                    datos_dispositivo[campo] = valor
        
        return Response({
            'datos_plantilla': datos_dispositivo,
            'tipo_dispositivo': plantilla.tipo_dispositivo,
            'mensaje': f'Plantilla "{plantilla.nombre}" aplicada correctamente'
        })


class OrdenServicioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar órdenes de servicio"""
    queryset = OrdenServicio.objects.all()
    serializer_class = OrdenServicioSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        'numero_orden', 'dispositivo_nombre', 'dispositivo_numero_serie',
        'descripcion_problema', 'diagnostico', 'solucion_aplicada',
        'solicitante', 'tecnico_asignado'
    ]
    filterset_fields = [
        'tipo_servicio', 'estado', 'prioridad', 'tipo_dispositivo',
        'tecnico_asignado'
    ]
    ordering_fields = [
        'fecha_solicitud', 'fecha_estimada', 'fecha_finalizacion',
        'prioridad', 'estado'
    ]
    ordering = ['-fecha_solicitud']

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if response.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED):
            orden_id = response.data.get('id') if isinstance(response.data, dict) else None
            if orden_id:
                pdf_url = request.build_absolute_uri(
                    reverse('inventario:orden_servicio_pdf', args=[orden_id])
                )
                response.data['pdf_url'] = pdf_url

        return response

    def get_serializer_class(self):
        if self.action == 'list':
            return OrdenServicioListSerializer
        return OrdenServicioSerializer
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Retorna órdenes pendientes"""
        ordenes = self.get_queryset().filter(estado='pendiente')
        serializer = self.get_serializer(ordenes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def en_proceso(self, request):
        """Retorna órdenes en proceso"""
        ordenes = self.get_queryset().filter(estado='en_proceso')
        serializer = self.get_serializer(ordenes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def vencidas(self, request):
        """Retorna órdenes vencidas"""
        ordenes = [orden for orden in self.get_queryset() if orden.esta_vencida]
        serializer = self.get_serializer(ordenes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_dispositivo(self, request):
        """Retorna órdenes de servicio de un dispositivo específico"""
        tipo = request.query_params.get('tipo_dispositivo')
        dispositivo_id = request.query_params.get('dispositivo_id')
        
        if not tipo or not dispositivo_id:
            return Response(
                {'error': 'Debe proporcionar tipo_dispositivo y dispositivo_id'},
                status=400
            )
        
        ordenes = self.get_queryset().filter(
            tipo_dispositivo=tipo,
            dispositivo_id=dispositivo_id
        )
        serializer = self.get_serializer(ordenes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        """Inicia una orden de servicio"""
        orden = self.get_object()
        if orden.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden iniciar órdenes pendientes'},
                status=400
            )
        
        orden.estado = 'en_proceso'
        orden.fecha_inicio = timezone.now()
        orden.tecnico_asignado = request.data.get('tecnico_asignado', orden.tecnico_asignado)
        orden.save()
        
        return Response({'mensaje': f'Orden {orden.numero_orden} iniciada'})
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Completa una orden de servicio"""
        orden = self.get_object()
        if orden.estado not in ['en_proceso', 'en_espera_repuesto']:
            return Response(
                {'error': 'Solo se pueden completar órdenes en proceso o en espera'},
                status=400
            )
        
        orden.estado = 'completada'
        orden.fecha_finalizacion = timezone.now()
        orden.solucion_aplicada = request.data.get('solucion_aplicada', orden.solucion_aplicada)
        orden.costo_mano_obra = request.data.get('costo_mano_obra', orden.costo_mano_obra)
        orden.costo_repuestos = request.data.get('costo_repuestos', orden.costo_repuestos)
        orden.save()
        
        return Response({'mensaje': f'Orden {orden.numero_orden} completada'})
