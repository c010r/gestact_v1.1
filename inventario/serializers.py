from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import (
    ModulosVisibles, UnidadEjecutora, UnidadAsistencial, ServicioUE,
    TipoGarantia, Estado, Lugares, TipoComputadora, Fabricante,
    Modelo, Proveedor, Computadora, TipoImpresora, Impresora,
    TipoMonitor, Monitor, PlantillaDispositivo, TipoNetworking,
    Networking, TipoTelefonia, Telefonia, TipoPeriferico, Periferico,
    TipoTecnologiaMedica, TecnologiaMedica,
    TipoInsumo, Insumo, TipoSoftware, Software, OrdenServicio
)


class ModulosVisiblesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModulosVisibles
        fields = '__all__'


class UnidadEjecutoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadEjecutora
        fields = '__all__'


class UnidadAsistencialSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadAsistencial
        fields = '__all__'


class ServicioUESerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicioUE
        fields = '__all__'


class TipoGarantiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoGarantia
        fields = '__all__'


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = '__all__'


class LugaresSerializer(serializers.ModelSerializer):
    tipo_nivel_nombre = serializers.CharField(
        source='tipo_nivel.nombre',
        read_only=True
    )
    padre_nombre = serializers.CharField(
        source='padre.nombre_completo',
        read_only=True
    )
    numero_ue = serializers.SerializerMethodField()

    class Meta:
        model = Lugares
        fields = [
            'id',
            'nombre',
            'codigo',
            'numero_ue',
            'tipo_nivel',
            'tipo_nivel_nombre',
            'padre',
            'padre_nombre',
            'nombre_completo',
            'nivel',
            'ruta_jerarquica',
            'comentarios',
            'activo',
            'fecha_creacion',
            'fecha_modificacion',
        ]
        read_only_fields = (
            'nombre_completo',
            'nivel',
            'ruta_jerarquica',
            'fecha_creacion',
            'fecha_modificacion',
        )

    def get_numero_ue(self, obj):
        """Obtiene el código de la UE raíz de este lugar"""
        if obj.nivel == 1:
            return obj.codigo
        # Navegar hasta el nivel 1
        actual = obj
        while actual.padre:
            actual = actual.padre
        return actual.codigo if actual else None

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except ValidationError as error:
            raise serializers.ValidationError(error.message_dict)

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except ValidationError as error:
            raise serializers.ValidationError(error.message_dict)


class TipoComputadoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoComputadora
        fields = '__all__'


class FabricanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fabricante
        fields = '__all__'


class ModeloSerializer(serializers.ModelSerializer):
    fabricante_nombre = serializers.CharField(
        source='fabricante.nombre',
        read_only=True
    )

    class Meta:
        model = Modelo
        fields = '__all__'


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'


class ComputadoraSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para mostrar nombres relacionados
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre',
        read_only=True
    )
    tipo_computadora_nombre = serializers.CharField(
        source='tipo_computadora.nombre',
        read_only=True
    )
    fabricante_nombre = serializers.CharField(
        source='fabricante.nombre',
        read_only=True
    )
    modelo_nombre = serializers.CharField(
        source='modelo.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre',
        read_only=True
    )
    tipo_garantia_nombre = serializers.CharField(
        source='tipo_garantia.nombre',
        read_only=True
    )

    # Campos calculados
    garantia_vigente = serializers.ReadOnlyField()
    fecha_finalizacion_garantia = serializers.ReadOnlyField()
    
    class Meta:
        model = Computadora
        fields = '__all__'
        read_only_fields = ('fecha_creacion', 'fecha_modificacion')


class ComputadoraListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre',
        read_only=True
    )
    fabricante_nombre = serializers.CharField(
        source='fabricante.nombre',
        read_only=True
    )
    modelo_nombre = serializers.CharField(
        source='modelo.nombre',
        read_only=True
    )
    garantia_vigente = serializers.ReadOnlyField()

    class Meta:
        model = Computadora
        fields = [
            'id', 'nombre', 'numero_serie', 'numero_inventario',
            'estado', 'estado_nombre', 'lugar', 'lugar_nombre',
            'fabricante', 'fabricante_nombre', 'modelo', 'modelo_nombre',
            'fecha_adquisicion', 'garantia_vigente'
        ]


class PlantillaDispositivoSerializer(serializers.ModelSerializer):
    # Campos relacionados para mostrar nombres
    fabricante_nombre = serializers.CharField(
        source='fabricante.nombre',
        read_only=True
    )
    modelo_nombre = serializers.CharField(
        source='modelo.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre',
        read_only=True
    )
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre',
        read_only=True
    )
    tipo_garantia_nombre = serializers.CharField(
        source='tipo_garantia.nombre',
        read_only=True
    )
    tipo_computadora_nombre = serializers.CharField(
        source='tipo_computadora.nombre',
        read_only=True
    )
    tipo_monitor_nombre = serializers.CharField(
        source='tipo_monitor.nombre',
        read_only=True
    )
    tipo_impresora_nombre = serializers.CharField(
        source='tipo_impresora.nombre',
        read_only=True
    )

    class Meta:
        model = PlantillaDispositivo
        fields = '__all__'
        read_only_fields = ('fecha_creacion', 'fecha_modificacion')


class TipoImpresoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoImpresora
        fields = '__all__'


class ImpresoraSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para mostrar nombres relacionados
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre',
        read_only=True
    )
    tipo_impresora_nombre = serializers.CharField(
        source='tipo_impresora.nombre',
        read_only=True
    )
    fabricante_nombre = serializers.CharField(
        source='fabricante.nombre',
        read_only=True
    )
    modelo_nombre = serializers.CharField(
        source='modelo.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre',
        read_only=True
    )
    tipo_garantia_nombre = serializers.CharField(
        source='tipo_garantia.nombre',
        read_only=True
    )

    # Campos calculados
    garantia_vigente = serializers.ReadOnlyField()
    fecha_finalizacion_garantia = serializers.ReadOnlyField()
    
    class Meta:
        model = Impresora
        fields = '__all__'
        read_only_fields = ('fecha_creacion', 'fecha_modificacion')


class ImpresoraListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listado de impresoras"""
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre',
        read_only=True
    )
    fabricante_nombre = serializers.CharField(
        source='fabricante.nombre',
        read_only=True
    )
    modelo_nombre = serializers.CharField(
        source='modelo.nombre',
        read_only=True
    )
    garantia_vigente = serializers.ReadOnlyField()

    class Meta:
        model = Impresora
        fields = [
            'id', 'nombre', 'numero_serie', 'numero_inventario',
            'estado', 'estado_nombre', 'lugar', 'lugar_nombre',
            'fabricante', 'fabricante_nombre', 'modelo', 'modelo_nombre',
            'fecha_adquisicion', 'garantia_vigente'
        ]


class TipoMonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoMonitor
        fields = '__all__'


class MonitorSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para mostrar nombres relacionados
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre',
        read_only=True
    )
    tipo_monitor_nombre = serializers.CharField(
        source='tipo_monitor.nombre',
        read_only=True
    )
    fabricante_nombre = serializers.CharField(
        source='fabricante.nombre',
        read_only=True
    )
    modelo_nombre = serializers.CharField(
        source='modelo.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre',
        read_only=True
    )
    tipo_garantia_nombre = serializers.CharField(
        source='tipo_garantia.nombre',
        read_only=True
    )

    # Campos calculados
    garantia_vigente = serializers.ReadOnlyField()
    fecha_finalizacion_garantia = serializers.ReadOnlyField()
    
    class Meta:
        model = Monitor
        fields = '__all__'
        read_only_fields = ('fecha_creacion', 'fecha_modificacion')


class MonitorListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listado de monitores"""
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre',
        read_only=True
    )
    fabricante_nombre = serializers.CharField(
        source='fabricante.nombre',
        read_only=True
    )
    modelo_nombre = serializers.CharField(
        source='modelo.nombre',
        read_only=True
    )
    garantia_vigente = serializers.ReadOnlyField()

    class Meta:
        model = Monitor
        fields = [
            'id', 'nombre', 'numero_serie', 'numero_inventario',
            'estado', 'estado_nombre', 'lugar', 'lugar_nombre',
            'fabricante', 'fabricante_nombre', 'modelo', 'modelo_nombre',
            'fecha_adquisicion', 'garantia_vigente'
        ]


class TipoNetworkingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoNetworking
        fields = '__all__'


class NetworkingSerializer(serializers.ModelSerializer):
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre',
        read_only=True
    )
    tipo_networking_nombre = serializers.CharField(
        source='tipo_networking.nombre',
        read_only=True
    )
    fabricante_nombre = serializers.CharField(
        source='fabricante.nombre',
        read_only=True
    )
    modelo_nombre = serializers.CharField(
        source='modelo.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre',
        read_only=True
    )
    tipo_garantia_nombre = serializers.CharField(
        source='tipo_garantia.nombre',
        read_only=True
    )
    garantia_vigente = serializers.ReadOnlyField()
    dias_restantes_garantia = serializers.ReadOnlyField()

    class Meta:
        model = Networking
        fields = '__all__'
        read_only_fields = (
            'fecha_creacion',
            'fecha_modificacion',
            'fecha_finalizacion_garantia',
        )


class NetworkingListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listado de equipos de networking"""
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre',
        read_only=True
    )
    tipo_networking_nombre = serializers.CharField(
        source='tipo_networking.nombre',
        read_only=True
    )
    garantia_vigente = serializers.ReadOnlyField()

    class Meta:
        model = Networking
        fields = [
            'id', 'nombre', 'numero_serie', 'numero_inventario',
            'estado', 'estado_nombre', 'lugar', 'lugar_nombre',
            'tipo_networking', 'tipo_networking_nombre',
            'fecha_adquisicion', 'garantia_vigente'
        ]


class TipoTelefoniaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTelefonia
        fields = '__all__'


class TelefoniaSerializer(serializers.ModelSerializer):
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre',
        read_only=True
    )
    tipo_telefonia_nombre = serializers.CharField(
        source='tipo_telefonia.nombre',
        read_only=True
    )
    fabricante_nombre = serializers.CharField(
        source='fabricante.nombre',
        read_only=True
    )
    modelo_nombre = serializers.CharField(
        source='modelo.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre',
        read_only=True
    )
    tipo_garantia_nombre = serializers.CharField(
        source='tipo_garantia.nombre',
        read_only=True
    )
    garantia_vigente = serializers.ReadOnlyField()
    dias_restantes_garantia = serializers.ReadOnlyField()

    class Meta:
        model = Telefonia
        fields = '__all__'
        read_only_fields = (
            'fecha_creacion',
            'fecha_modificacion',
            'fecha_finalizacion_garantia',
        )


class TelefoniaListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listado de telefonía"""
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre',
        read_only=True
    )
    tipo_telefonia_nombre = serializers.CharField(
        source='tipo_telefonia.nombre',
        read_only=True
    )
    garantia_vigente = serializers.ReadOnlyField()

    class Meta:
        model = Telefonia
        fields = [
            'id', 'nombre', 'numero_serie', 'numero_inventario',
            'estado', 'estado_nombre', 'lugar', 'lugar_nombre',
            'tipo_telefonia', 'tipo_telefonia_nombre',
            'extension_interna', 'numero_linea',
            'garantia_vigente'
        ]


class TipoPerifericoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPeriferico
        fields = '__all__'


class PerifericoSerializer(serializers.ModelSerializer):
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre',
        read_only=True
    )
    tipo_periferico_nombre = serializers.CharField(
        source='tipo_periferico.nombre',
        read_only=True
    )
    fabricante_nombre = serializers.CharField(
        source='fabricante.nombre',
        read_only=True
    )
    modelo_nombre = serializers.CharField(
        source='modelo.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre',
        read_only=True
    )
    tipo_garantia_nombre = serializers.CharField(
        source='tipo_garantia.nombre',
        read_only=True
    )
    garantia_vigente = serializers.ReadOnlyField()
    dias_restantes_garantia = serializers.ReadOnlyField()

    class Meta:
        model = Periferico
        fields = '__all__'
        read_only_fields = (
            'fecha_creacion',
            'fecha_modificacion',
            'fecha_finalizacion_garantia',
        )


class PerifericoListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listado de periféricos"""
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre',
        read_only=True
    )
    tipo_periferico_nombre = serializers.CharField(
        source='tipo_periferico.nombre',
        read_only=True
    )
    garantia_vigente = serializers.ReadOnlyField()

    class Meta:
        model = Periferico
        fields = [
            'id', 'nombre', 'numero_serie', 'numero_inventario',
            'estado', 'estado_nombre', 'lugar', 'lugar_nombre',
            'tipo_periferico', 'tipo_periferico_nombre',
            'tipo_conexion', 'es_inalambrico',
            'garantia_vigente'
        ]


class TipoInsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoInsumo
        fields = '__all__'


class InsumoSerializer(serializers.ModelSerializer):
    tipo_insumo_nombre = serializers.CharField(
        source='tipo_insumo.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre',
        read_only=True
    )
    necesita_reorden = serializers.ReadOnlyField()

    class Meta:
        model = Insumo
        fields = '__all__'
        read_only_fields = (
            'fecha_creacion',
            'ultima_actualizacion',
        )


class InsumoListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listado de insumos"""
    tipo_insumo_nombre = serializers.CharField(
        source='tipo_insumo.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre',
        read_only=True
    )
    necesita_reorden = serializers.ReadOnlyField()

    class Meta:
        model = Insumo
        fields = [
            'id', 'nombre', 'tipo_insumo', 'tipo_insumo_nombre',
            'cantidad_total', 'cantidad_disponible', 'punto_reorden',
            'unidad_medida', 'necesita_reorden'
        ]


class TipoSoftwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoSoftware
        fields = '__all__'


class SoftwareSerializer(serializers.ModelSerializer):
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    tipo_software_nombre = serializers.CharField(
        source='tipo_software.nombre',
        read_only=True
    )
    fabricante_nombre = serializers.CharField(
        source='fabricante.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre',
        read_only=True
    )
    licencias_disponibles = serializers.ReadOnlyField()
    esta_vigente = serializers.ReadOnlyField()

    class Meta:
        model = Software
        fields = '__all__'
        read_only_fields = (
            'fecha_creacion',
            'fecha_modificacion',
        )


class SoftwareListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listado de software"""
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    tipo_software_nombre = serializers.CharField(
        source='tipo_software.nombre',
        read_only=True
    )
    fabricante_nombre = serializers.CharField(
        source='fabricante.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre',
        read_only=True
    )
    licencias_disponibles = serializers.ReadOnlyField()
    esta_vigente = serializers.ReadOnlyField()

    class Meta:
        model = Software
        fields = [
            'id', 'nombre', 'estado', 'estado_nombre',
            'tipo_software', 'tipo_software_nombre',
            'fabricante', 'fabricante_nombre',
            'proveedor', 'proveedor_nombre',
            'version', 'cantidad_licencias', 'licencias_en_uso',
            'licencias_disponibles', 'esta_vigente'
        ]


class TipoTecnologiaMedicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTecnologiaMedica
        fields = '__all__'


class TecnologiaMedicaSerializer(serializers.ModelSerializer):
    """Serializer para tecnología médica"""
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre_completo',
        read_only=True
    )
    tipo_tecnologia_medica_nombre = serializers.CharField(
        source='tipo_tecnologia_medica.nombre',
        read_only=True
    )
    fabricante_nombre = serializers.CharField(
        source='fabricante.nombre',
        read_only=True
    )
    modelo_nombre = serializers.CharField(
        source='modelo.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre',
        read_only=True
    )
    tipo_garantia_nombre = serializers.CharField(
        source='tipo_garantia.nombre',
        read_only=True
    )
    garantia_vigente = serializers.ReadOnlyField()
    dias_restantes_garantia = serializers.ReadOnlyField()
    requiere_calibracion_proxima = serializers.ReadOnlyField()
    requiere_mantenimiento_proximo = serializers.ReadOnlyField()

    class Meta:
        model = TecnologiaMedica
        fields = '__all__'
        read_only_fields = (
            'fecha_finalizacion_garantia',
            'fecha_creacion',
            'fecha_modificacion',
        )

    def validate(self, data):
        """Validación personalizada"""
        modelo = data.get('modelo')
        fabricante = data.get('fabricante')
        
        if modelo and fabricante:
            if modelo.fabricante != fabricante:
                raise serializers.ValidationError({
                    'modelo': (
                        'El modelo seleccionado no corresponde al '
                        'fabricante indicado.'
                    )
                })
        
        if data.get('requiere_calibracion') and not data.get('frecuencia_calibracion_meses'):
            raise serializers.ValidationError({
                'frecuencia_calibracion_meses': (
                    'Debe especificar la frecuencia de calibración.'
                )
            })
        
        if data.get('requiere_mantenimiento_preventivo') and not data.get('frecuencia_mantenimiento_meses'):
            raise serializers.ValidationError({
                'frecuencia_mantenimiento_meses': (
                    'Debe especificar la frecuencia de mantenimiento.'
                )
            })
        
        return data


class TecnologiaMedicaListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listado de tecnología médica"""
    estado_nombre = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )
    lugar_nombre = serializers.CharField(
        source='lugar.nombre_completo',
        read_only=True
    )
    tipo_tecnologia_medica_nombre = serializers.CharField(
        source='tipo_tecnologia_medica.nombre',
        read_only=True
    )
    fabricante_nombre = serializers.CharField(
        source='fabricante.nombre',
        read_only=True
    )
    modelo_nombre = serializers.CharField(
        source='modelo.nombre',
        read_only=True
    )
    garantia_vigente = serializers.ReadOnlyField()
    requiere_calibracion_proxima = serializers.ReadOnlyField()
    requiere_mantenimiento_proximo = serializers.ReadOnlyField()

    class Meta:
        model = TecnologiaMedica
        fields = [
            'id', 'nombre', 'estado', 'estado_nombre',
            'lugar', 'lugar_nombre',
            'tipo_tecnologia_medica', 'tipo_tecnologia_medica_nombre',
            'fabricante', 'fabricante_nombre',
            'modelo', 'modelo_nombre',
            'numero_serie', 'numero_inventario',
            'registro_sanitario', 'clasificacion_riesgo',
            'area_aplicacion', 'garantia_vigente',
            'requiere_calibracion', 'requiere_calibracion_proxima',
            'requiere_mantenimiento_preventivo', 'requiere_mantenimiento_proximo'
        ]


class OrdenServicioSerializer(serializers.ModelSerializer):
    """Serializer para órdenes de servicio"""
    tipo_servicio_display = serializers.CharField(
        source='get_tipo_servicio_display',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )
    prioridad_display = serializers.CharField(
        source='get_prioridad_display',
        read_only=True
    )
    tipo_dispositivo_display = serializers.CharField(
        source='get_tipo_dispositivo_display',
        read_only=True
    )
    tiempo_resolucion = serializers.ReadOnlyField()
    esta_vencida = serializers.ReadOnlyField()
    dias_pendiente = serializers.ReadOnlyField()
    
    class Meta:
        model = OrdenServicio
        fields = '__all__'
        read_only_fields = (
            'numero_orden',
            'dispositivo_nombre',
            'dispositivo_numero_serie',
            'costo_total',
            'fecha_creacion',
            'fecha_modificacion',
        )
    
    def validate(self, data):
        """Validación personalizada"""
        # Validar que si está completada, tenga fecha de finalización
        if data.get('estado') == 'completada' and not data.get('fecha_finalizacion'):
            raise serializers.ValidationError({
                'fecha_finalizacion': 'Debe especificar la fecha de finalización para órdenes completadas.'
            })
        
        # Validar que si está en proceso, tenga fecha de inicio
        if data.get('estado') == 'en_proceso' and not data.get('fecha_inicio'):
            raise serializers.ValidationError({
                'fecha_inicio': 'Debe especificar la fecha de inicio para órdenes en proceso.'
            })
        
        return data


class OrdenServicioListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listado de órdenes de servicio"""
    tipo_servicio_display = serializers.CharField(
        source='get_tipo_servicio_display',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )
    prioridad_display = serializers.CharField(
        source='get_prioridad_display',
        read_only=True
    )
    tipo_dispositivo_display = serializers.CharField(
        source='get_tipo_dispositivo_display',
        read_only=True
    )
    dias_pendiente = serializers.ReadOnlyField()
    esta_vencida = serializers.ReadOnlyField()
    
    class Meta:
        model = OrdenServicio
        fields = [
            'id', 'numero_orden', 'tipo_servicio', 'tipo_servicio_display',
            'estado', 'estado_display', 'prioridad', 'prioridad_display',
            'tipo_dispositivo', 'tipo_dispositivo_display',
            'dispositivo_nombre', 'dispositivo_numero_serie',
            'solicitante', 'tecnico_asignado',
            'fecha_solicitud', 'fecha_estimada', 'fecha_finalizacion',
            'dias_pendiente', 'esta_vencida', 'costo_total'
        ]
