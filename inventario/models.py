from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta
import uuid as uuid_lib
from django.utils import timezone


def _sanitize_inventory_segment(value):
    if not value:
        return ""
    return str(value).strip().replace("/", "-")


def _obtener_codigo_unidad_ejecutora(lugar):
    if not lugar:
        return ""

    visitados = set()
    actual = lugar

    while actual and actual.pk not in visitados:
        if actual.codigo:
            return actual.codigo
        visitados.add(actual.pk)
        actual = actual.padre

    return ""


def generar_numero_inventario(lugar=None, descriptor=None, referencia=None):
    partes = []

    codigo = _obtener_codigo_unidad_ejecutora(lugar)
    if codigo:
        partes.append(_sanitize_inventory_segment(codigo))

    if descriptor:
        partes.append(_sanitize_inventory_segment(descriptor))

    if referencia:
        partes.append(_sanitize_inventory_segment(referencia))

    return "/".join(partes)


# Constantes para monedas
MONEDA_CHOICES = [
    ('UYU', 'Pesos Uruguayos ($)'),
    ('USD', 'Dólares (US$)'),
    ('EUR', 'Euros (€)'),
]


class ModulosVisibles(models.Model):
    """Tabla para definir módulos visibles"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Módulo Visible"
        verbose_name_plural = "Módulos Visibles"
    
    def __str__(self):
        return self.nombre


class UnidadEjecutora(models.Model):
    """Tabla de unidades ejecutoras"""
    numero_ue = models.CharField(max_length=50, unique=True, verbose_name="Número UE")
    nombre = models.CharField(max_length=200, unique=True)
    comentarios = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Unidad Ejecutora"
        verbose_name_plural = "Unidades Ejecutoras"
    
    def __str__(self):
        return self.nombre


class UnidadAsistencial(models.Model):
    """Tabla de unidades asistenciales"""
    nombre = models.CharField(max_length=200, unique=True)
    comentarios = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Unidad Asistencial"
        verbose_name_plural = "Unidades Asistenciales"
    
    def __str__(self):
        return self.nombre


class ServicioUE(models.Model):
    """Tabla de servicios de unidad ejecutora"""
    nombre = models.CharField(max_length=200, unique=True)
    comentarios = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Servicio UE"
        verbose_name_plural = "Servicios UE"
    
    def __str__(self):
        return self.nombre


class TipoGarantia(models.Model):
    """Tabla de tipos de garantía"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Tipo de Garantía"
        verbose_name_plural = "Tipos de Garantía"
    
    def __str__(self):
        return self.nombre


class Estado(models.Model):
    """Tabla de estados"""
    nombre = models.CharField(max_length=100, unique=True)
    comentarios = models.TextField(blank=True, null=True)
    visibilidad = models.ForeignKey(
        ModulosVisibles, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Visibilidad"
    )
    
    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
    
    def __str__(self):
        return self.nombre


class TipoNivel(models.Model):
    """Tabla de tipos de nivel jerárquico para lugares"""
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del Tipo de Nivel"
    )
    nivel = models.PositiveIntegerField(
        verbose_name="Nivel Jerárquico",
        help_text="1 = Nivel superior, 2-7 = Niveles inferiores"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción"
    )
    requiere_codigo = models.BooleanField(
        default=False,
        verbose_name="Requiere Código",
        help_text="Si este nivel requiere un código identificador"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )

    class Meta:
        verbose_name = "Tipo de Nivel"
        verbose_name_plural = "Tipos de Nivel"
        ordering = ['nivel', 'nombre']
        unique_together = ['nombre', 'nivel']

    def __str__(self):
        return f"Nivel {self.nivel} - {self.nombre}"


class Lugares(models.Model):
    """Tabla de lugares con estructura jerárquica de hasta 7 niveles"""
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del Lugar"
    )
    codigo = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Código",
        help_text="Código identificador del lugar (ej: número UE)"
    )
    tipo_nivel = models.ForeignKey(
        TipoNivel,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Nivel",
        help_text="Tipo de nivel jerárquico de este lugar"
    )
    padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='hijos',
        verbose_name="Lugar Padre",
        help_text="Lugar jerárquico superior (dejar vacío para nivel raíz)"
    )
    nombre_completo = models.CharField(
        max_length=500,
        editable=False,
        verbose_name="Nombre Completo (Ruta Jerárquica)"
    )
    nivel = models.PositiveIntegerField(
        editable=False,
        verbose_name="Nivel",
        help_text="Nivel en la jerarquía (1-7)"
    )
    ruta_jerarquica = models.TextField(
        editable=False,
        verbose_name="Ruta Jerárquica",
        help_text="Almacena la ruta completa de IDs: /1/5/12/"
    )
    comentarios = models.TextField(
        blank=True,
        null=True,
        verbose_name="Comentarios"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Modificación"
    )

    class Meta:
        verbose_name = "Lugar"
        verbose_name_plural = "Lugares"
        ordering = ['nivel', 'nombre']
        indexes = [
            models.Index(fields=['nivel']),
            models.Index(fields=['padre']),
            models.Index(fields=['tipo_nivel']),
            models.Index(fields=['ruta_jerarquica']),
        ]

    def clean(self):
        """Validaciones personalizadas"""
        # Validar nivel máximo
        if self.padre:
            nivel_calculado = self.padre.nivel + 1
            if nivel_calculado > 7:
                raise ValidationError({
                    'padre': 'No se pueden crear más de 7 niveles jerárquicos'
                })

            # Validar que el tipo de nivel corresponda al nivel calculado
            if self.tipo_nivel.nivel != nivel_calculado:
                raise ValidationError({
                    'tipo_nivel': f'El tipo de nivel debe ser de nivel '
                                  f'{nivel_calculado} para este padre'
                })
        else:
            # Es un nodo raíz, debe ser nivel 1
            if self.tipo_nivel.nivel != 1:
                raise ValidationError({
                    'tipo_nivel': 'Los lugares sin padre deben ser de nivel 1'
                })

        # Validar código si es requerido
        if self.tipo_nivel.requiere_codigo and not self.codigo:
            msg_codigo = (
                f'El código es requerido para el tipo de nivel '
                f'{self.tipo_nivel.nombre}'
            )
            raise ValidationError({'codigo': msg_codigo})

        # Validar unicidad de nombre dentro del mismo padre
        queryset = Lugares.objects.filter(
            nombre=self.nombre,
            padre=self.padre
        )
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        if queryset.exists():
            msg_nombre = (
                'Ya existe un lugar con este nombre en el '
                'mismo nivel jerárquico'
            )
            raise ValidationError({'nombre': msg_nombre})

    def save(self, *args, **kwargs):
        """Guardar con cálculo automático de campos jerárquicos"""
        # Calcular el nivel
        if self.padre:
            self.nivel = self.padre.nivel + 1
        else:
            self.nivel = 1

        # Validar antes de guardar
        self.full_clean()

        # Guardar temporalmente para obtener el ID
        super().save(*args, **kwargs)

        # Construir la ruta jerárquica
        if self.padre:
            self.ruta_jerarquica = f"{self.padre.ruta_jerarquica}{self.pk}/"
        else:
            self.ruta_jerarquica = f"/{self.pk}/"

        # Construir el nombre completo jerárquico
        ancestros = self.obtener_ancestros()
        if ancestros:
            nombres = [a.nombre for a in ancestros] + [self.nombre]
            self.nombre_completo = " > ".join(nombres)
        else:
            self.nombre_completo = self.nombre

        # Guardar nuevamente con los campos calculados
        super().save(update_fields=[
            'ruta_jerarquica',
            'nombre_completo'
        ])

    def __str__(self):
        return self.nombre_completo

    def obtener_ancestros(self):
        """Obtiene todos los ancestros ordenados desde la raíz"""
        ancestros = []
        actual = self.padre
        while actual:
            ancestros.insert(0, actual)
            actual = actual.padre
        return ancestros

    def obtener_descendientes(self, incluir_self=False):
        """Obtiene todos los descendientes de forma recursiva"""
        descendientes = []
        if incluir_self:
            descendientes.append(self)

        for hijo in self.hijos.all():
            descendientes.append(hijo)
            descendientes.extend(hijo.obtener_descendientes())

        return descendientes

    def obtener_ruta_completa(self):
        """Obtiene la ruta completa como lista de lugares"""
        ancestros = self.obtener_ancestros()
        return ancestros + [self]

    def es_hoja(self):
        """Verifica si es un nodo hoja (sin hijos)"""
        return not self.hijos.exists()

    def es_raiz(self):
        """Verifica si es un nodo raíz (sin padre)"""
        return self.padre is None

    def puede_tener_hijos(self):
        """Verifica si puede tener hijos (nivel < 7)"""
        return self.nivel < 7

    def obtener_nivel_nombre(self):
        """Obtiene una representación del nivel"""
        return f"Nivel {self.nivel} - {self.tipo_nivel.nombre}"

    @classmethod
    def obtener_raices(cls):
        """Obtiene todos los nodos raíz"""
        return cls.objects.filter(padre__isnull=True, activo=True)

    @classmethod
    def obtener_por_nivel(cls, nivel):
        """Obtiene todos los lugares de un nivel específico"""
        return cls.objects.filter(nivel=nivel, activo=True)


class TipoComputadora(models.Model):
    """Tabla de tipos de computadora"""
    nombre = models.CharField(max_length=100, unique=True)
    comentarios = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Tipo de Computadora"
        verbose_name_plural = "Tipos de Computadora"
    
    def __str__(self):
        return self.nombre


class Fabricante(models.Model):
    """Tabla de fabricantes"""
    nombre = models.CharField(max_length=100, unique=True)
    comentarios = models.TextField(blank=True, null=True)
    sitio_web = models.URLField(blank=True, null=True, verbose_name="Sitio Web")
    
    class Meta:
        verbose_name = "Fabricante"
        verbose_name_plural = "Fabricantes"
    
    def __str__(self):
        return self.nombre


class Modelo(models.Model):
    """Tabla de modelos"""
    nombre = models.CharField(max_length=100)
    fabricante = models.ForeignKey(
        Fabricante, 
        on_delete=models.PROTECT,
        verbose_name="Fabricante"
    )
    comentarios = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Modelo"
        verbose_name_plural = "Modelos"
        unique_together = ['nombre', 'fabricante']
    
    def __str__(self):
        return f"{self.fabricante.nombre} - {self.nombre}"


class Proveedor(models.Model):
    """Tabla de proveedores"""
    nombre = models.CharField(max_length=200, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=300, blank=True, null=True)
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
    
    def __str__(self):
        return self.nombre


class Computadora(models.Model):
    """Tabla principal de computadoras"""
    nombre = models.CharField(max_length=200)
    estado = models.ForeignKey(
        Estado, 
        on_delete=models.PROTECT,
        verbose_name="Estado"
    )
    lugar = models.ForeignKey(
        Lugares, 
        on_delete=models.PROTECT,
        verbose_name="Lugar"
    )
    tipo_computadora = models.ForeignKey(
        TipoComputadora, 
        on_delete=models.PROTECT,
        verbose_name="Tipo de Computadora"
    )
    fabricante = models.ForeignKey(
        Fabricante, 
        on_delete=models.PROTECT,
        verbose_name="Fabricante"
    )
    modelo = models.ForeignKey(
        Modelo, 
        on_delete=models.PROTECT,
        verbose_name="Modelo"
    )
    numero_serie = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Número de Serie"
    )
    numero_inventario = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Número de Inventario"
    )
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Proveedor"
    )
    comentarios = models.TextField(blank=True, null=True)
    tipo_garantia = models.ForeignKey(
        TipoGarantia, 
        on_delete=models.PROTECT,
        verbose_name="Tipo de Garantía"
    )
    fecha_adquisicion = models.DateField(verbose_name="Fecha de Adquisición")
    anos_garantia = models.PositiveIntegerField(
        verbose_name="Años de Garantía",
        help_text="Número de años de garantía"
    )
    fecha_finalizacion_garantia = models.DateField(
        verbose_name="Fecha de Finalización de Garantía",
        editable=False
    )
    valor_adquisicion = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name="Valor de Adquisición"
    )
    moneda = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default='UYU',
        verbose_name="Moneda"
    )
    direccion_ip = models.GenericIPAddressField(
        blank=True, 
        null=True,
        verbose_name="Dirección IP"
    )
    direccion_mac = models.CharField(
        max_length=17, 
        blank=True, 
        null=True,
        verbose_name="Dirección MAC",
        help_text="Formato: AA:BB:CC:DD:EE:FF"
    )
    
    # Relaciones con otros dispositivos
    monitores_vinculados = models.ManyToManyField(
        'Monitor',
        blank=True,
        verbose_name="Monitores Vinculados",
        help_text="Monitores asociados a esta computadora",
        related_name="computadoras_vinculadas"
    )
    impresoras_vinculadas = models.ManyToManyField(
        'Impresora',
        blank=True,
        verbose_name="Impresoras Vinculadas",
        help_text="Impresoras asociadas a esta computadora",
        related_name="computadoras_vinculadas"
    )

    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Computadora"
        verbose_name_plural = "Computadoras"
        ordering = ['nombre']
    
    def clean(self):
        # Validar que el modelo pertenezca al fabricante seleccionado
        if self.modelo and self.fabricante:
            if self.modelo.fabricante != self.fabricante:
                raise ValidationError({
                    'modelo': (
                        'El modelo {modelo} no pertenece al fabricante '
                        '{fabricante}'
                    ).format(
                        modelo=self.modelo.nombre,
                        fabricante=self.fabricante.nombre
                    )
                })
    
    def save(self, *args, **kwargs):
        # Detectar si es una creación o actualización
        is_new = self.pk is None
        
        # Obtener valores anteriores para detectar cambios
        old_values = {}
        if not is_new:
            try:
                old_obj = Computadora.objects.get(pk=self.pk)
                old_values = {
                    'estado': (
                        old_obj.estado.nombre if old_obj.estado else None
                    ),
                    'lugar': old_obj.lugar.nombre if old_obj.lugar else None,
                    'valor_adquisicion': old_obj.valor_adquisicion,
                }
            except Computadora.DoesNotExist:
                pass
        
        # Calcular fecha de finalización de garantía automáticamente
        if self.fecha_adquisicion and self.anos_garantia:
            self.fecha_finalizacion_garantia = self.fecha_adquisicion + relativedelta(years=self.anos_garantia)
        
        if not self.numero_inventario:
            descriptor = None
            if self.modelo_id:
                descriptor = self.modelo.nombre
            elif self.tipo_computadora_id:
                descriptor = self.tipo_computadora.nombre
            elif self.fabricante_id:
                descriptor = self.fabricante.nombre
            generated = generar_numero_inventario(
                lugar=getattr(self, "lugar", None),
                descriptor=descriptor or self.nombre,
                referencia=self.numero_serie,
            )
            if generated:
                self.numero_inventario = generated

        # Validar antes de guardar
        self.full_clean()
        
        super().save(*args, **kwargs)
        
        # Registrar eventos en bitácora
        if is_new:
            # Registro inicial
            Bitacora.registrar_evento(
                tipo_dispositivo='computadora',
                dispositivo_obj=self,
                tipo_evento='registro',
                descripcion=f'Computadora registrada en el sistema. Modelo: {self.modelo.nombre}, Fabricante: {self.fabricante.nombre}',
                observaciones=f'Número de serie: {self.numero_serie}, Ubicación: {self.lugar.nombre}'
            )
        else:
            # Detectar cambios específicos
            if old_values.get('estado') != self.estado.nombre:
                Bitacora.registrar_evento(
                    tipo_dispositivo='computadora',
                    dispositivo_obj=self,
                    tipo_evento='cambio_estado',
                    descripcion=f'Cambio de estado de {old_values.get("estado")} a {self.estado.nombre}',
                    valor_anterior=old_values.get('estado'),
                    valor_nuevo=self.estado.nombre
                )
            
            if old_values.get('lugar') != self.lugar.nombre:
                Bitacora.registrar_evento(
                    tipo_dispositivo='computadora',
                    dispositivo_obj=self,
                    tipo_evento='cambio_ubicacion',
                    descripcion=f'Cambio de ubicación de {old_values.get("lugar")} a {self.lugar.nombre}',
                    valor_anterior=old_values.get('lugar'),
                    valor_nuevo=self.lugar.nombre
                )
            
            if old_values.get('valor_adquisicion') != self.valor_adquisicion:
                Bitacora.registrar_evento(
                    tipo_dispositivo='computadora',
                    dispositivo_obj=self,
                    tipo_evento='actualizacion',
                    descripcion=f'Actualización del valor de adquisición',
                    valor_anterior=str(old_values.get('valor_adquisicion')) if old_values.get('valor_adquisicion') else 'No definido',
                    valor_nuevo=str(self.valor_adquisicion) if self.valor_adquisicion else 'No definido'
                )
    
    def __str__(self):
        return f"{self.nombre} - {self.numero_serie}"
    
    @property
    def garantia_vigente(self):
        """Retorna True si la garantía está vigente"""
        return date.today() <= self.fecha_finalizacion_garantia
    
    @property
    def dias_restantes_garantia(self):
        """Calcula los días restantes de garantía"""
        if self.garantia_vigente:
            return (self.fecha_finalizacion_garantia - date.today()).days
        return 0
    
    def vincular_monitor(self, monitor):
        """Vincula un monitor a esta computadora"""
        if monitor and monitor not in self.monitores_vinculados.all():
            self.monitores_vinculados.add(monitor)
            # Registrar en bitácora
            Bitacora.registrar_evento(
                tipo_dispositivo='computadora',
                dispositivo_obj=self,
                tipo_evento='asignacion_personal',
                descripcion=f'Monitor {monitor.nombre} vinculado a la computadora',
                observaciones=f'Monitor S/N: {monitor.numero_serie}'
            )
            return True
        return False
    
    def desvincular_monitor(self, monitor):
        """Desvincula un monitor de esta computadora"""
        if monitor and monitor in self.monitores_vinculados.all():
            self.monitores_vinculados.remove(monitor)
            # Registrar en bitácora
            Bitacora.registrar_evento(
                tipo_dispositivo='computadora',
                dispositivo_obj=self,
                tipo_evento='cambio_estado',
                descripcion=f'Monitor {monitor.nombre} desvinculado de la computadora',
                observaciones=f'Monitor S/N: {monitor.numero_serie}'
            )
            return True
        return False
    
    def vincular_impresora(self, impresora):
        """Vincula una impresora a esta computadora"""
        if impresora and impresora not in self.impresoras_vinculadas.all():
            self.impresoras_vinculadas.add(impresora)
            # Registrar en bitácora
            Bitacora.registrar_evento(
                tipo_dispositivo='computadora',
                dispositivo_obj=self,
                tipo_evento='asignacion_personal',
                descripcion=f'Impresora {impresora.nombre} vinculada a la computadora',
                observaciones=f'Impresora S/N: {impresora.numero_serie}'
            )
            return True
        return False
    
    def desvincular_impresora(self, impresora):
        """Desvincula una impresora de esta computadora"""
        if impresora and impresora in self.impresoras_vinculadas.all():
            self.impresoras_vinculadas.remove(impresora)
            # Registrar en bitácora
            Bitacora.registrar_evento(
                tipo_dispositivo='computadora',
                dispositivo_obj=self,
                tipo_evento='cambio_estado',
                descripcion=f'Impresora {impresora.nombre} desvinculada de la computadora',
                observaciones=f'Impresora S/N: {impresora.numero_serie}'
            )
            return True
        return False
    
    def obtener_dispositivos_vinculados(self):
        """Retorna un diccionario con todos los dispositivos vinculados"""
        return {
            'monitores': list(self.monitores_vinculados.all()),
            'impresoras': list(self.impresoras_vinculadas.all()),
            'total_monitores': self.monitores_vinculados.count(),
            'total_impresoras': self.impresoras_vinculadas.count()
        }


class TipoMonitor(models.Model):
    """Tabla de tipos de monitor"""
    nombre = models.CharField(max_length=100, unique=True)
    comentarios = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Tipo de Monitor"
        verbose_name_plural = "Tipos de Monitor"
    
    def __str__(self):
        return self.nombre


class Monitor(models.Model):
    """Tabla de monitores"""
    nombre = models.CharField(max_length=200)
    estado = models.ForeignKey(
        Estado, 
        on_delete=models.PROTECT,
        verbose_name="Estado"
    )
    lugar = models.ForeignKey(
        Lugares, 
        on_delete=models.PROTECT,
        verbose_name="Lugar"
    )
    tipo_monitor = models.ForeignKey(
        TipoMonitor, 
        on_delete=models.PROTECT,
        verbose_name="Tipo de Monitor"
    )
    fabricante = models.ForeignKey(
        Fabricante, 
        on_delete=models.PROTECT,
        verbose_name="Fabricante"
    )
    modelo = models.ForeignKey(
        Modelo, 
        on_delete=models.PROTECT,
        verbose_name="Modelo"
    )
    numero_serie = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Número de Serie"
    )
    numero_inventario = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Número de Inventario"
    )
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Proveedor"
    )
    comentarios = models.TextField(blank=True, null=True)
    tipo_garantia = models.ForeignKey(
        TipoGarantia, 
        on_delete=models.PROTECT,
        verbose_name="Tipo de Garantía"
    )
    fecha_adquisicion = models.DateField(verbose_name="Fecha de Adquisición")
    anos_garantia = models.PositiveIntegerField(
        verbose_name="Años de Garantía",
        help_text="Número de años de garantía"
    )
    fecha_finalizacion_garantia = models.DateField(
        verbose_name="Fecha de Finalización de Garantía",
        editable=False
    )
    valor_adquisicion = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name="Valor de Adquisición"
    )
    moneda = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default='UYU',
        verbose_name="Moneda"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Monitor"
        verbose_name_plural = "Monitores"
        ordering = ['nombre']
    
    def clean(self):
        # Validar que el modelo pertenezca al fabricante seleccionado
        if self.modelo and self.fabricante:
            if self.modelo.fabricante != self.fabricante:
                raise ValidationError({
                    'modelo': f'El modelo {self.modelo} no pertenece al fabricante {self.fabricante}'
                })
    
    def save(self, *args, **kwargs):
        # Calcular fecha de finalización de garantía
        if self.fecha_adquisicion and self.anos_garantia:
            self.fecha_finalizacion_garantia = self.fecha_adquisicion + relativedelta(years=self.anos_garantia)
        
        if not self.numero_inventario:
            descriptor = None
            if self.modelo_id:
                descriptor = self.modelo.nombre
            elif self.tipo_monitor_id:
                descriptor = self.tipo_monitor.nombre
            elif self.fabricante_id:
                descriptor = self.fabricante.nombre
            generated = generar_numero_inventario(
                lugar=getattr(self, "lugar", None),
                descriptor=descriptor or self.nombre,
                referencia=self.numero_serie,
            )
            if generated:
                self.numero_inventario = generated

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nombre} - {self.numero_serie}"
    
    @property
    def garantia_vigente(self):
        """Verifica si la garantía está vigente"""
        return date.today() <= self.fecha_finalizacion_garantia
    
    @property
    def dias_restantes_garantia(self):
        """Calcula los días restantes de garantía"""
        if self.garantia_vigente:
            return (self.fecha_finalizacion_garantia - date.today()).days
        return 0


class TipoNetworking(models.Model):
    """Tabla de tipos para equipos de networking"""

    nombre = models.CharField(max_length=100, unique=True)
    comentarios = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Tipo de Equipo de Networking"
        verbose_name_plural = "Tipos de Equipos de Networking"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Networking(models.Model):
    """Tabla de equipos de red (switches, routers, etc.)"""

    nombre = models.CharField(max_length=200)
    estado = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        verbose_name="Estado"
    )
    lugar = models.ForeignKey(
        Lugares,
        on_delete=models.PROTECT,
        verbose_name="Lugar"
    )
    tipo_networking = models.ForeignKey(
        TipoNetworking,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Equipo"
    )
    fabricante = models.ForeignKey(
        Fabricante,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Fabricante"
    )
    modelo = models.ForeignKey(
        Modelo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Modelo"
    )
    numero_serie = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número de Serie"
    )
    numero_inventario = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número de Inventario"
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Proveedor"
    )
    tipo_garantia = models.ForeignKey(
        TipoGarantia,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Garantía"
    )
    fecha_adquisicion = models.DateField(
        verbose_name="Fecha de Adquisición"
    )
    anos_garantia = models.PositiveIntegerField(
        verbose_name="Años de Garantía",
        help_text="Número de años de garantía"
    )
    fecha_finalizacion_garantia = models.DateField(
        verbose_name="Fecha de Finalización de Garantía",
        editable=False,
        null=True,
        blank=True
    )
    valor_adquisicion = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Valor de Adquisición"
    )
    moneda = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default='UYU',
        verbose_name="Moneda"
    )
    direccion_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="Dirección IP"
    )
    direccion_mac = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        verbose_name="Dirección MAC",
        help_text="Formato: AA:BB:CC:DD:EE:FF"
    )
    firmware_version = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Versión de Firmware"
    )
    cantidad_puertos = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Puertos Disponibles"
    )
    soporte_poe = models.BooleanField(
        default=False,
        verbose_name="Soporte PoE"
    )
    comentarios = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Equipo de Networking"
        verbose_name_plural = "Equipos de Networking"
        ordering = ['nombre']

    def clean(self):
        if self.modelo and self.fabricante:
            if self.modelo.fabricante != self.fabricante:
                raise ValidationError({
                    'modelo': (
                        'El modelo seleccionado no corresponde al '
                        'fabricante indicado.'
                    )
                })

    def save(self, *args, **kwargs):
        if self.fecha_adquisicion and self.anos_garantia:
            self.fecha_finalizacion_garantia = (
                self.fecha_adquisicion
                + relativedelta(years=self.anos_garantia)
            )
        else:
            self.fecha_finalizacion_garantia = None

        if not self.numero_inventario:
            descriptor = None
            if self.modelo_id:
                descriptor = self.modelo.nombre
            elif self.tipo_networking_id:
                descriptor = self.tipo_networking.nombre
            elif self.fabricante_id:
                descriptor = self.fabricante.nombre
            generated = generar_numero_inventario(
                lugar=getattr(self, "lugar", None),
                descriptor=descriptor or self.nombre,
                referencia=self.numero_serie,
            )
            if generated:
                self.numero_inventario = generated

        is_new = self.pk is None
        previous_state = None
        previous_location = None

        if not is_new:
            try:
                old = Networking.objects.get(pk=self.pk)
                previous_state = old.estado.nombre if old.estado else None
                previous_location = old.lugar.nombre if old.lugar else None
            except Networking.DoesNotExist:
                pass

        self.full_clean()
        super().save(*args, **kwargs)

        if is_new:
            Bitacora.registrar_evento(
                tipo_dispositivo='networking',
                dispositivo_obj=self,
                tipo_evento='registro',
                descripcion=(
                    'Equipo de networking registrado en el sistema.'
                ),
                observaciones=(
                    f'S/N: {self.numero_serie or "N/A"}, '
                    f'Ubicación: {self.lugar.nombre}'
                )
            )
        else:
            if previous_state and previous_state != self.estado.nombre:
                Bitacora.registrar_evento(
                    tipo_dispositivo='networking',
                    dispositivo_obj=self,
                    tipo_evento='cambio_estado',
                    descripcion=(
                        f'Cambio de estado de {previous_state} '
                        f'a {self.estado.nombre}'
                    ),
                    valor_anterior=previous_state,
                    valor_nuevo=self.estado.nombre
                )

            if previous_location and previous_location != self.lugar.nombre:
                Bitacora.registrar_evento(
                    tipo_dispositivo='networking',
                    dispositivo_obj=self,
                    tipo_evento='cambio_ubicacion',
                    descripcion=(
                        f'Cambio de ubicación de {previous_location} '
                        f'a {self.lugar.nombre}'
                    ),
                    valor_anterior=previous_location,
                    valor_nuevo=self.lugar.nombre
                )

    def __str__(self):
        return self.nombre

    @property
    def garantia_vigente(self):
        if not self.fecha_finalizacion_garantia:
            return False
        return date.today() <= self.fecha_finalizacion_garantia

    @property
    def dias_restantes_garantia(self):
        if self.fecha_finalizacion_garantia and self.garantia_vigente:
            delta = self.fecha_finalizacion_garantia - date.today()
            return delta.days
        return 0


class TipoTelefonia(models.Model):
    """Tabla de tipos para dispositivos de telefonía"""

    nombre = models.CharField(max_length=100, unique=True)
    comentarios = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Tipo de Dispositivo de Telefonía"
        verbose_name_plural = "Tipos de Dispositivos de Telefonía"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Telefonia(models.Model):
    """Tabla de dispositivos de telefonía (IP, analógicos, etc.)"""

    nombre = models.CharField(max_length=200)
    estado = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        verbose_name="Estado"
    )
    lugar = models.ForeignKey(
        Lugares,
        on_delete=models.PROTECT,
        verbose_name="Lugar"
    )
    tipo_telefonia = models.ForeignKey(
        TipoTelefonia,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Telefonía"
    )
    fabricante = models.ForeignKey(
        Fabricante,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Fabricante"
    )
    modelo = models.ForeignKey(
        Modelo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Modelo"
    )
    numero_serie = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número de Serie"
    )
    numero_inventario = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número de Inventario"
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Proveedor"
    )
    tipo_garantia = models.ForeignKey(
        TipoGarantia,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Garantía"
    )
    fecha_adquisicion = models.DateField(
        verbose_name="Fecha de Adquisición"
    )
    anos_garantia = models.PositiveIntegerField(
        verbose_name="Años de Garantía",
        help_text="Número de años de garantía"
    )
    fecha_finalizacion_garantia = models.DateField(
        verbose_name="Fecha de Finalización de Garantía",
        editable=False,
        null=True,
        blank=True
    )
    valor_adquisicion = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Valor de Adquisición"
    )
    moneda = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default='UYU',
        verbose_name="Moneda"
    )
    extension_interna = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Extensión Interna"
    )
    numero_linea = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="Número de Línea"
    )
    direccion_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="Dirección IP"
    )
    direccion_mac = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        verbose_name="Dirección MAC"
    )
    tipo_conexion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Tipo de Conexión"
    )
    comentarios = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dispositivo de Telefonía"
        verbose_name_plural = "Dispositivos de Telefonía"
        ordering = ['nombre']

    def clean(self):
        if self.modelo and self.fabricante:
            if self.modelo.fabricante != self.fabricante:
                raise ValidationError({
                    'modelo': (
                        'El modelo seleccionado no corresponde al '
                        'fabricante indicado.'
                    )
                })

    def save(self, *args, **kwargs):
        if self.fecha_adquisicion and self.anos_garantia:
            self.fecha_finalizacion_garantia = (
                self.fecha_adquisicion
                + relativedelta(years=self.anos_garantia)
            )
        else:
            self.fecha_finalizacion_garantia = None

        if not self.numero_inventario:
            descriptor = None
            if self.modelo_id:
                descriptor = self.modelo.nombre
            elif self.tipo_telefonia_id:
                descriptor = self.tipo_telefonia.nombre
            elif self.fabricante_id:
                descriptor = self.fabricante.nombre
            generated = generar_numero_inventario(
                lugar=getattr(self, "lugar", None),
                descriptor=descriptor or self.nombre,
                referencia=self.numero_serie or self.numero_linea,
            )
            if generated:
                self.numero_inventario = generated

        is_new = self.pk is None
        previous_state = None
        previous_location = None

        if not is_new:
            try:
                old = Telefonia.objects.get(pk=self.pk)
                previous_state = old.estado.nombre if old.estado else None
                previous_location = old.lugar.nombre if old.lugar else None
            except Telefonia.DoesNotExist:
                pass

        self.full_clean()
        super().save(*args, **kwargs)

        if is_new:
            Bitacora.registrar_evento(
                tipo_dispositivo='telefonia',
                dispositivo_obj=self,
                tipo_evento='registro',
                descripcion='Dispositivo de telefonía registrado.',
                observaciones=(
                    f'Extensión: {self.extension_interna or "N/A"}, '
                    f'Ubicación: {self.lugar.nombre}'
                )
            )
        else:
            if previous_state and previous_state != self.estado.nombre:
                Bitacora.registrar_evento(
                    tipo_dispositivo='telefonia',
                    dispositivo_obj=self,
                    tipo_evento='cambio_estado',
                    descripcion=(
                        f'Cambio de estado de {previous_state} '
                        f'a {self.estado.nombre}'
                    ),
                    valor_anterior=previous_state,
                    valor_nuevo=self.estado.nombre
                )

            if previous_location and previous_location != self.lugar.nombre:
                Bitacora.registrar_evento(
                    tipo_dispositivo='telefonia',
                    dispositivo_obj=self,
                    tipo_evento='cambio_ubicacion',
                    descripcion=(
                        f'Cambio de ubicación de {previous_location} '
                        f'a {self.lugar.nombre}'
                    ),
                    valor_anterior=previous_location,
                    valor_nuevo=self.lugar.nombre
                )

    def __str__(self):
        return self.nombre

    @property
    def garantia_vigente(self):
        if not self.fecha_finalizacion_garantia:
            return False
        return date.today() <= self.fecha_finalizacion_garantia

    @property
    def dias_restantes_garantia(self):
        if self.fecha_finalizacion_garantia and self.garantia_vigente:
            delta = self.fecha_finalizacion_garantia - date.today()
            return delta.days
        return 0


class TipoPeriferico(models.Model):
    """Tabla de tipos para periféricos"""

    nombre = models.CharField(max_length=100, unique=True)
    comentarios = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Tipo de Periférico"
        verbose_name_plural = "Tipos de Periférico"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Periferico(models.Model):
    """Tabla de periféricos (teclados, ratones, etc.)"""

    nombre = models.CharField(max_length=200)
    estado = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        verbose_name="Estado"
    )
    lugar = models.ForeignKey(
        Lugares,
        on_delete=models.PROTECT,
        verbose_name="Lugar"
    )
    tipo_periferico = models.ForeignKey(
        TipoPeriferico,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Periférico"
    )
    fabricante = models.ForeignKey(
        Fabricante,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Fabricante"
    )
    modelo = models.ForeignKey(
        Modelo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Modelo"
    )
    numero_serie = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número de Serie"
    )
    numero_inventario = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número de Inventario"
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Proveedor"
    )
    tipo_garantia = models.ForeignKey(
        TipoGarantia,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Garantía"
    )
    fecha_adquisicion = models.DateField(
        verbose_name="Fecha de Adquisición"
    )
    anos_garantia = models.PositiveIntegerField(
        verbose_name="Años de Garantía",
        help_text="Número de años de garantía"
    )
    fecha_finalizacion_garantia = models.DateField(
        verbose_name="Fecha de Finalización de Garantía",
        editable=False,
        null=True,
        blank=True
    )
    valor_adquisicion = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Valor de Adquisición"
    )
    moneda = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default='UYU',
        verbose_name="Moneda"
    )
    tipo_conexion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Tipo de Conexión"
    )
    es_inalambrico = models.BooleanField(
        default=False,
        verbose_name="¿Es inalámbrico?"
    )
    comentarios = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Periférico"
        verbose_name_plural = "Periféricos"
        ordering = ['nombre']

    def clean(self):
        if self.modelo and self.fabricante:
            if self.modelo.fabricante != self.fabricante:
                raise ValidationError({
                    'modelo': (
                        'El modelo seleccionado no corresponde al '
                        'fabricante indicado.'
                    )
                })

    def save(self, *args, **kwargs):
        if self.fecha_adquisicion and self.anos_garantia:
            self.fecha_finalizacion_garantia = (
                self.fecha_adquisicion
                + relativedelta(years=self.anos_garantia)
            )
        else:
            self.fecha_finalizacion_garantia = None

        if not self.numero_inventario:
            descriptor = None
            if self.modelo_id:
                descriptor = self.modelo.nombre
            elif self.tipo_periferico_id:
                descriptor = self.tipo_periferico.nombre
            elif self.fabricante_id:
                descriptor = self.fabricante.nombre
            generated = generar_numero_inventario(
                lugar=getattr(self, "lugar", None),
                descriptor=descriptor or self.nombre,
                referencia=self.numero_serie,
            )
            if generated:
                self.numero_inventario = generated

        is_new = self.pk is None
        previous_state = None
        previous_location = None

        if not is_new:
            try:
                old = Periferico.objects.get(pk=self.pk)
                previous_state = old.estado.nombre if old.estado else None
                previous_location = old.lugar.nombre if old.lugar else None
            except Periferico.DoesNotExist:
                pass

        self.full_clean()
        super().save(*args, **kwargs)

        if is_new:
            Bitacora.registrar_evento(
                tipo_dispositivo='periferico',
                dispositivo_obj=self,
                tipo_evento='registro',
                descripcion='Periférico registrado en el sistema.',
                observaciones=(
                    f'S/N: {self.numero_serie or "N/A"}, '
                    f'Ubicación: {self.lugar.nombre}'
                )
            )
        else:
            if previous_state and previous_state != self.estado.nombre:
                Bitacora.registrar_evento(
                    tipo_dispositivo='periferico',
                    dispositivo_obj=self,
                    tipo_evento='cambio_estado',
                    descripcion=(
                        f'Cambio de estado de {previous_state} '
                        f'a {self.estado.nombre}'
                    ),
                    valor_anterior=previous_state,
                    valor_nuevo=self.estado.nombre
                )

            if previous_location and previous_location != self.lugar.nombre:
                Bitacora.registrar_evento(
                    tipo_dispositivo='periferico',
                    dispositivo_obj=self,
                    tipo_evento='cambio_ubicacion',
                    descripcion=(
                        f'Cambio de ubicación de {previous_location} '
                        f'a {self.lugar.nombre}'
                    ),
                    valor_anterior=previous_location,
                    valor_nuevo=self.lugar.nombre
                )

    def __str__(self):
        return self.nombre

    @property
    def garantia_vigente(self):
        if not self.fecha_finalizacion_garantia:
            return False
        return date.today() <= self.fecha_finalizacion_garantia

    @property
    def dias_restantes_garantia(self):
        if self.fecha_finalizacion_garantia and self.garantia_vigente:
            delta = self.fecha_finalizacion_garantia - date.today()
            return delta.days
        return 0


class TipoTecnologiaMedica(models.Model):
    """Tabla de tipos para tecnología médica"""

    nombre = models.CharField(max_length=100, unique=True)
    comentarios = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Tipo de Tecnología Médica"
        verbose_name_plural = "Tipos de Tecnología Médica"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class TecnologiaMedica(models.Model):
    """Tabla de equipos de tecnología médica"""

    nombre = models.CharField(max_length=200)
    estado = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        verbose_name="Estado"
    )
    lugar = models.ForeignKey(
        Lugares,
        on_delete=models.PROTECT,
        verbose_name="Lugar"
    )
    tipo_tecnologia_medica = models.ForeignKey(
        TipoTecnologiaMedica,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Equipo Médico"
    )
    fabricante = models.ForeignKey(
        Fabricante,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Fabricante"
    )
    modelo = models.ForeignKey(
        Modelo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Modelo"
    )
    numero_serie = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número de Serie"
    )
    numero_inventario = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número de Inventario"
    )
    numero_activo_fijo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número de Activo Fijo",
        help_text="Código de activo fijo contable"
    )
    registro_sanitario = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Registro Sanitario",
        help_text="Número de registro ante autoridad sanitaria"
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Proveedor"
    )
    tipo_garantia = models.ForeignKey(
        TipoGarantia,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Garantía"
    )
    fecha_adquisicion = models.DateField(
        verbose_name="Fecha de Adquisición"
    )
    anos_garantia = models.PositiveIntegerField(
        verbose_name="Años de Garantía",
        help_text="Número de años de garantía"
    )
    fecha_finalizacion_garantia = models.DateField(
        verbose_name="Fecha de Finalización de Garantía",
        editable=False,
        null=True,
        blank=True
    )
    valor_adquisicion = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Valor de Adquisición"
    )
    moneda = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default='UYU',
        verbose_name="Moneda"
    )
    
    # Campos específicos de equipos médicos
    requiere_calibracion = models.BooleanField(
        default=False,
        verbose_name="Requiere Calibración Periódica"
    )
    frecuencia_calibracion_meses = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Frecuencia de Calibración (meses)",
        help_text="Cada cuántos meses requiere calibración"
    )
    fecha_ultima_calibracion = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Última Calibración"
    )
    requiere_mantenimiento_preventivo = models.BooleanField(
        default=True,
        verbose_name="Requiere Mantenimiento Preventivo"
    )
    frecuencia_mantenimiento_meses = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Frecuencia de Mantenimiento (meses)"
    )
    fecha_ultimo_mantenimiento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Último Mantenimiento"
    )
    clasificacion_riesgo = models.CharField(
        max_length=20,
        choices=[
            ('clase_i', 'Clase I - Riesgo Bajo'),
            ('clase_iia', 'Clase IIa - Riesgo Medio'),
            ('clase_iib', 'Clase IIb - Riesgo Medio-Alto'),
            ('clase_iii', 'Clase III - Riesgo Alto'),
            ('clase_iv', 'Clase IV - Riesgo Muy Alto'),
        ],
        blank=True,
        null=True,
        verbose_name="Clasificación de Riesgo",
        help_text="Clasificación según normativa médica"
    )
    area_aplicacion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Área de Aplicación",
        help_text="Ej: UCI, Quirófano, Emergencia, etc."
    )
    requiere_personal_especializado = models.BooleanField(
        default=False,
        verbose_name="Requiere Personal Especializado"
    )
    voltaje_operacion = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Voltaje de Operación"
    )
    potencia = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Potencia"
    )
    
    comentarios = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tecnología Médica"
        verbose_name_plural = "Tecnología Médica"
        ordering = ['nombre']

    def clean(self):
        if self.modelo and self.fabricante:
            if self.modelo.fabricante != self.fabricante:
                raise ValidationError({
                    'modelo': (
                        'El modelo seleccionado no corresponde al '
                        'fabricante indicado.'
                    )
                })
        
        if self.requiere_calibracion and not self.frecuencia_calibracion_meses:
            raise ValidationError({
                'frecuencia_calibracion_meses': (
                    'Debe especificar la frecuencia de calibración.'
                )
            })
        
        if self.requiere_mantenimiento_preventivo and not self.frecuencia_mantenimiento_meses:
            raise ValidationError({
                'frecuencia_mantenimiento_meses': (
                    'Debe especificar la frecuencia de mantenimiento.'
                )
            })

    def save(self, *args, **kwargs):
        if self.fecha_adquisicion and self.anos_garantia:
            self.fecha_finalizacion_garantia = (
                self.fecha_adquisicion
                + relativedelta(years=self.anos_garantia)
            )
        else:
            self.fecha_finalizacion_garantia = None

        if not self.numero_inventario:
            descriptor = None
            if self.modelo_id:
                descriptor = self.modelo.nombre
            elif self.tipo_tecnologia_medica_id:
                descriptor = self.tipo_tecnologia_medica.nombre
            elif self.fabricante_id:
                descriptor = self.fabricante.nombre
            generated = generar_numero_inventario(
                lugar=getattr(self, "lugar", None),
                descriptor=descriptor or self.nombre,
                referencia=self.numero_serie or self.registro_sanitario,
            )
            if generated:
                self.numero_inventario = generated

        is_new = self.pk is None
        previous_state = None
        previous_location = None

        if not is_new:
            try:
                old = TecnologiaMedica.objects.get(pk=self.pk)
                previous_state = old.estado.nombre if old.estado else None
                previous_location = old.lugar.nombre if old.lugar else None
            except TecnologiaMedica.DoesNotExist:
                pass

        self.full_clean()
        super().save(*args, **kwargs)

        if is_new:
            Bitacora.registrar_evento(
                tipo_dispositivo='tecnologia_medica',
                dispositivo_obj=self,
                tipo_evento='registro',
                descripcion='Equipo de tecnología médica registrado.',
                observaciones=(
                    f'Tipo: {self.tipo_tecnologia_medica.nombre}, '
                    f'Ubicación: {self.lugar.nombre}'
                )
            )
        else:
            if previous_state and previous_state != self.estado.nombre:
                Bitacora.registrar_evento(
                    tipo_dispositivo='tecnologia_medica',
                    dispositivo_obj=self,
                    tipo_evento='cambio_estado',
                    descripcion=(
                        f'Cambio de estado de {previous_state} '
                        f'a {self.estado.nombre}'
                    ),
                    valor_anterior=previous_state,
                    valor_nuevo=self.estado.nombre
                )

            if previous_location and previous_location != self.lugar.nombre:
                Bitacora.registrar_evento(
                    tipo_dispositivo='tecnologia_medica',
                    dispositivo_obj=self,
                    tipo_evento='cambio_ubicacion',
                    descripcion=(
                        f'Cambio de ubicación de {previous_location} '
                        f'a {self.lugar.nombre}'
                    ),
                    valor_anterior=previous_location,
                    valor_nuevo=self.lugar.nombre
                )

    def __str__(self):
        return self.nombre

    @property
    def garantia_vigente(self):
        if not self.fecha_finalizacion_garantia:
            return False
        return date.today() <= self.fecha_finalizacion_garantia

    @property
    def dias_restantes_garantia(self):
        if self.fecha_finalizacion_garantia and self.garantia_vigente:
            delta = self.fecha_finalizacion_garantia - date.today()
            return delta.days
        return 0
    
    @property
    def requiere_calibracion_proxima(self):
        """Verifica si requiere calibración en los próximos 30 días"""
        if not self.requiere_calibracion or not self.fecha_ultima_calibracion or not self.frecuencia_calibracion_meses:
            return False
        
        fecha_proxima = self.fecha_ultima_calibracion + relativedelta(months=self.frecuencia_calibracion_meses)
        dias_restantes = (fecha_proxima - date.today()).days
        return 0 <= dias_restantes <= 30
    
    @property
    def requiere_mantenimiento_proximo(self):
        """Verifica si requiere mantenimiento en los próximos 30 días"""
        if not self.requiere_mantenimiento_preventivo or not self.fecha_ultimo_mantenimiento or not self.frecuencia_mantenimiento_meses:
            return False
        
        fecha_proxima = self.fecha_ultimo_mantenimiento + relativedelta(months=self.frecuencia_mantenimiento_meses)
        dias_restantes = (fecha_proxima - date.today()).days
        return 0 <= dias_restantes <= 30


class TipoInsumo(models.Model):
    """Tabla de tipos para insumos"""

    nombre = models.CharField(max_length=120, unique=True)
    unidad_medida_default = models.CharField(
        max_length=50,
        default='unidad',
        verbose_name="Unidad de Medida Predeterminada"
    )
    comentarios = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Tipo de Insumo"
        verbose_name_plural = "Tipos de Insumo"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Insumo(models.Model):
    """Tabla de insumos (consumibles)"""

    nombre = models.CharField(max_length=200)
    tipo_insumo = models.ForeignKey(
        TipoInsumo,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Insumo"
    )
    descripcion = models.TextField(blank=True, null=True)
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Proveedor"
    )
    cantidad_total = models.PositiveIntegerField(default=0)
    cantidad_disponible = models.PositiveIntegerField(default=0)
    punto_reorden = models.PositiveIntegerField(default=0)
    unidad_medida = models.CharField(max_length=50, default='unidad')
    valor_unitario_estandar = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor Unitario Estimado"
    )
    moneda = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default='UYU',
        verbose_name="Moneda"
    )
    activo = models.BooleanField(default=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
        ordering = ['nombre']

    def clean(self):
        if self.cantidad_disponible > self.cantidad_total:
            raise ValidationError({
                'cantidad_disponible': (
                    'La cantidad disponible no puede ser mayor que la '
                    'cantidad total.'
                )
            })

    def __str__(self):
        return self.nombre

    @property
    def necesita_reorden(self):
        return self.cantidad_disponible <= self.punto_reorden


class TipoSoftware(models.Model):
    """Tabla de tipos de software"""

    nombre = models.CharField(max_length=150, unique=True)
    comentarios = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Tipo de Software"
        verbose_name_plural = "Tipos de Software"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Software(models.Model):
    """Tabla de activos de software y licencias"""

    nombre = models.CharField(max_length=200)
    estado = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        verbose_name="Estado"
    )
    tipo_software = models.ForeignKey(
        TipoSoftware,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Software"
    )
    fabricante = models.ForeignKey(
        Fabricante,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Fabricante"
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Proveedor"
    )
    lugar = models.ForeignKey(
        Lugares,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Lugar asociado"
    )
    version = models.CharField(max_length=100, blank=True, null=True)
    numero_licencia = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Número de Licencia"
    )
    cantidad_licencias = models.PositiveIntegerField(default=1)
    licencias_en_uso = models.PositiveIntegerField(default=0)
    fecha_adquisicion = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Adquisición"
    )
    fecha_expiracion = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Expiración"
    )
    costo_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Costo Total"
    )
    moneda = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default='UYU',
        verbose_name="Moneda"
    )
    notas = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Software"
        verbose_name_plural = "Software"
        ordering = ['nombre']

    def clean(self):
        if self.licencias_en_uso > self.cantidad_licencias:
            raise ValidationError({
                'licencias_en_uso': (
                    'Las licencias en uso no pueden exceder la cantidad '
                    'total disponible.'
                )
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    @property
    def licencias_disponibles(self):
        return max(self.cantidad_licencias - self.licencias_en_uso, 0)

    @property
    def esta_vigente(self):
        if not self.fecha_expiracion:
            return True
        return date.today() <= self.fecha_expiracion


class TipoImpresora(models.Model):
    """Tabla de tipos de impresora"""
    nombre = models.CharField(max_length=100, unique=True)
    comentarios = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Tipo de Impresora"
        verbose_name_plural = "Tipos de Impresora"
    
    def __str__(self):
        return self.nombre


class Bitacora(models.Model):
    """Modelo para registrar eventos y cambios en los dispositivos"""
    
    TIPO_EVENTO_CHOICES = [
        ('registro', 'Registro Inicial'),
        ('servicio_garantia', 'Servicio por Garantía'),
        ('mantenimiento', 'Mantenimiento'),
        ('reparacion', 'Reparación'),
        ('cambio_estado', 'Cambio de Estado'),
        ('cambio_ubicacion', 'Cambio de Ubicación'),
        ('asignacion_personal', 'Asignación de Personal'),
        ('baja', 'Baja del Equipo'),
        ('actualizacion', 'Actualización de Datos'),
        ('otro', 'Otro')
    ]
    
    TIPO_DISPOSITIVO_CHOICES = [
        ('computadora', 'Computadora'),
        ('impresora', 'Impresora'),
        ('monitor', 'Monitor'),
        ('networking', 'Networking'),
        ('telefonia', 'Telefonía'),
        ('periferico', 'Periférico'),
        ('tecnologia_medica', 'Tecnología Médica'),
        ('insumo', 'Insumo'),
        ('software', 'Software'),
    ]
    
    # Información del evento
    tipo_evento = models.CharField(
        max_length=50,
        choices=TIPO_EVENTO_CHOICES,
        verbose_name="Tipo de Evento"
    )
    
    # Información del dispositivo
    tipo_dispositivo = models.CharField(
        max_length=20,
        choices=TIPO_DISPOSITIVO_CHOICES,
        verbose_name="Tipo de Dispositivo"
    )
    dispositivo_id = models.PositiveIntegerField(
        verbose_name="ID del Dispositivo"
    )
    dispositivo_nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del Dispositivo"
    )
    
    # Detalles del evento
    descripcion = models.TextField(verbose_name="Descripción del Evento")
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones Adicionales"
    )
    
    # Información de cambios (para eventos de cambio)
    valor_anterior = models.TextField(
        blank=True,
        null=True,
        verbose_name="Valor Anterior"
    )
    valor_nuevo = models.TextField(
        blank=True,
        null=True,
        verbose_name="Valor Nuevo"
    )
    
    # Personal responsable
    usuario_responsable = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Usuario Responsable"
    )
    
    # Fechas
    fecha_evento = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha del Evento"
    )
    
    class Meta:
        verbose_name = "Bitácora"
        verbose_name_plural = "Bitácoras"
        ordering = ['-fecha_evento']
        indexes = [
            models.Index(fields=['tipo_dispositivo', 'dispositivo_id']),
            models.Index(fields=['fecha_evento']),
            models.Index(fields=['tipo_evento']),
        ]
    
    def __str__(self):
        etiqueta = self.get_tipo_evento_display()
        fecha = self.fecha_evento.strftime('%d/%m/%Y %H:%M')
        return f"{etiqueta} - {self.dispositivo_nombre} ({fecha})"

    @classmethod
    def registrar_evento(
        cls,
        tipo_dispositivo,
        dispositivo_obj,
        tipo_evento,
        descripcion,
        observaciones=None,
        valor_anterior=None,
        valor_nuevo=None,
        usuario=None
    ):
        """Método para registrar un evento en la bitácora"""
        return cls.objects.create(
            tipo_dispositivo=tipo_dispositivo,
            dispositivo_id=dispositivo_obj.pk,
            dispositivo_nombre=dispositivo_obj.nombre,
            tipo_evento=tipo_evento,
            descripcion=descripcion,
            observaciones=observaciones,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            usuario_responsable=usuario
        )


class PlantillaDispositivo(models.Model):
    """Modelo para almacenar plantillas de dispositivos"""
    
    TIPO_DISPOSITIVO_CHOICES = [
        ('computadora', 'Computadora'),
        ('impresora', 'Impresora'),
        ('monitor', 'Monitor'),
        ('networking', 'Networking'),
        ('telefonia', 'Telefonía'),
        ('periferico', 'Periférico'),
        ('tecnologia_medica', 'Tecnología Médica'),
        ('insumo', 'Insumo'),
        ('software', 'Software'),
    ]
    
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre de la Plantilla",
        help_text="Nombre descriptivo para identificar la plantilla"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción",
        help_text="Descripción opcional de la plantilla"
    )
    tipo_dispositivo = models.CharField(
        max_length=20,
        choices=TIPO_DISPOSITIVO_CHOICES,
        verbose_name="Tipo de Dispositivo"
    )
    
    # Campos comunes para todos los dispositivos
    estado = models.ForeignKey(
        Estado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Estado"
    )
    lugar = models.ForeignKey(
        Lugares,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Lugar"
    )
    fabricante = models.ForeignKey(
        Fabricante,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Fabricante"
    )
    modelo = models.ForeignKey(
        Modelo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Modelo"
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Proveedor"
    )
    tipo_garantia = models.ForeignKey(
        TipoGarantia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de Garantía"
    )
    anos_garantia = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Años de Garantía"
    )
    valor_adquisicion = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor de Adquisición"
    )
    fecha_adquisicion = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Adquisición"
    )
    comentarios = models.TextField(
        blank=True,
        null=True,
        verbose_name="Comentarios"
    )
    
    # Campos específicos para computadoras
    tipo_computadora = models.ForeignKey(
        'TipoComputadora',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de Computadora"
    )
    direccion_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="Dirección IP"
    )
    direccion_mac = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        verbose_name="Dirección MAC"
    )
    
    # Campos específicos para impresoras
    tipo_impresora = models.ForeignKey(
        'TipoImpresora',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de Impresora"
    )
    
    # Campos específicos para monitores
    tipo_monitor = models.ForeignKey(
        'TipoMonitor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de Monitor"
    )
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    usuario_creacion = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Usuario que creó la plantilla"
    )
    
    class Meta:
        verbose_name = "Plantilla de Dispositivo"
        verbose_name_plural = "Plantillas de Dispositivos"
        ordering = ['tipo_dispositivo', 'nombre']
        unique_together = ['nombre', 'tipo_dispositivo']
    
    def __str__(self):
        return f"{self.get_tipo_dispositivo_display()} - {self.nombre}"
    
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Validar campos específicos según el tipo de dispositivo
        if (
            self.tipo_dispositivo == 'computadora'
            and not self.tipo_computadora
        ):
            raise ValidationError({
                'tipo_computadora': (
                    'Este campo es requerido para plantillas de '
                    'computadoras.'
                )
            })
        elif (
            self.tipo_dispositivo == 'impresora'
            and not self.tipo_impresora
        ):
            raise ValidationError({
                'tipo_impresora': (
                    'Este campo es requerido para plantillas de '
                    'impresoras.'
                )
            })
        elif (
            self.tipo_dispositivo == 'monitor'
            and not self.tipo_monitor
        ):
            raise ValidationError({
                'tipo_monitor': (
                    'Este campo es requerido para plantillas de '
                    'monitores.'
                )
            })
    
    def aplicar_a_dispositivo(self, dispositivo_form):
        """Aplica los valores de la plantilla a un formulario de dispositivo"""
        campos_comunes = [
            'estado',
            'lugar',
            'fabricante',
            'modelo',
            'proveedor',
            'tipo_garantia',
            'anos_garantia',
            'valor_adquisicion',
            'comentarios',
        ]
        
        # Aplicar campos comunes
        for campo in campos_comunes:
            valor = getattr(self, campo)
            if valor is not None and campo in dispositivo_form.fields:
                dispositivo_form.fields[campo].initial = valor
        
        # Aplicar campos específicos según el tipo de dispositivo
        if self.tipo_dispositivo == 'computadora':
            campos_especificos = [
                'tipo_computadora',
                'direccion_ip',
                'direccion_mac',
            ]
        elif self.tipo_dispositivo == 'impresora':
            campos_especificos = ['tipo_impresora']
        elif self.tipo_dispositivo == 'monitor':
            campos_especificos = ['tipo_monitor']
        else:
            campos_especificos = []
        
        for campo in campos_especificos:
            valor = getattr(self, campo)
            if valor is not None and campo in dispositivo_form.fields:
                dispositivo_form.fields[campo].initial = valor
        
        return dispositivo_form


class Impresora(models.Model):
    """Tabla de impresoras"""
    nombre = models.CharField(max_length=200)
    estado = models.ForeignKey(
        Estado,
        on_delete=models.PROTECT,
        verbose_name="Estado"
    )
    lugar = models.ForeignKey(
        Lugares,
        on_delete=models.PROTECT,
        verbose_name="Lugar"
    )
    tipo_impresora = models.ForeignKey(
        TipoImpresora,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Impresora"
    )
    fabricante = models.ForeignKey(
        Fabricante,
        on_delete=models.PROTECT,
        verbose_name="Fabricante"
    )
    modelo = models.ForeignKey(
        Modelo,
        on_delete=models.PROTECT,
        verbose_name="Modelo"
    )
    numero_serie = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Número de Serie"
    )
    numero_inventario = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número de Inventario"
    )
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Proveedor"
    )
    comentarios = models.TextField(blank=True, null=True)
    tipo_garantia = models.ForeignKey(
        TipoGarantia,
        on_delete=models.PROTECT,
        verbose_name="Tipo de Garantía"
    )
    fecha_adquisicion = models.DateField(verbose_name="Fecha de Adquisición")
    anos_garantia = models.PositiveIntegerField(
        verbose_name="Años de Garantía",
        help_text="Número de años de garantía"
    )
    fecha_finalizacion_garantia = models.DateField(
        verbose_name="Fecha de Finalización de Garantía",
        editable=False
    )
    valor_adquisicion = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Valor de Adquisición"
    )
    moneda = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default='UYU',
        verbose_name="Moneda"
    )
    requiere_toner_extra = models.BooleanField(
        default=False,
        verbose_name="Suministrar tóner extra",
        help_text="Indica si esta impresora debe enviarse con un cartucho de tóner adicional."
    )
    insumo_toner_extra = models.ForeignKey(
        'Insumo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tóner extra asociado",
        related_name='impresoras_con_toner_extra'
    )
    cantidad_toner_extra = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad de tóner extra",
        help_text="Unidades de tóner que se entregan junto a la impresora cuando se emite un remito."
    )
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Impresora"
        verbose_name_plural = "Impresoras"
        ordering = ['nombre']
    
    def clean(self):
        # Validar que el modelo pertenezca al fabricante seleccionado
        if self.modelo and self.fabricante:
            if self.modelo.fabricante != self.fabricante:
                raise ValidationError({
                    'modelo': f'El modelo {self.modelo.nombre} no pertenece al fabricante {self.fabricante.nombre}'
                })
        if self.requiere_toner_extra:
            errors = {}
            if not self.insumo_toner_extra:
                errors['insumo_toner_extra'] = 'Debe seleccionar un insumo de tóner para esta impresora.'
            if self.cantidad_toner_extra <= 0:
                errors['cantidad_toner_extra'] = 'La cantidad de tóner extra debe ser mayor a cero.'
            if errors:
                raise ValidationError(errors)
        else:
            # Si no requiere tóner extra, evitar información residual
            if self.insumo_toner_extra is not None or self.cantidad_toner_extra != 0:
                self.insumo_toner_extra = None
                self.cantidad_toner_extra = 0
    
    def save(self, *args, **kwargs):
        # Detectar si es una creación o actualización
        is_new = self.pk is None
        
        # Obtener valores anteriores para detectar cambios
        old_values = {}
        if not is_new:
            try:
                old_obj = Impresora.objects.get(pk=self.pk)
                old_values = {
                    'estado': old_obj.estado.nombre if old_obj.estado else None,
                    'lugar': old_obj.lugar.nombre if old_obj.lugar else None,
                    'valor_adquisicion': getattr(old_obj, 'valor_adquisicion', None),
                }
            except Impresora.DoesNotExist:
                pass
        
        # Calcular fecha de finalización de garantía automáticamente
        if self.fecha_adquisicion and self.anos_garantia:
            self.fecha_finalizacion_garantia = self.fecha_adquisicion + relativedelta(years=self.anos_garantia)
        
        if not self.numero_inventario:
            descriptor = None
            if self.modelo_id:
                descriptor = self.modelo.nombre
            elif self.tipo_impresora_id:
                descriptor = self.tipo_impresora.nombre
            elif self.fabricante_id:
                descriptor = self.fabricante.nombre
            generated = generar_numero_inventario(
                lugar=getattr(self, "lugar", None),
                descriptor=descriptor or self.nombre,
                referencia=self.numero_serie,
            )
            if generated:
                self.numero_inventario = generated

        # Validar antes de guardar
        self.full_clean()
        
        super().save(*args, **kwargs)
        
        # Registrar eventos en bitácora
        if is_new:
            # Registro inicial
            Bitacora.registrar_evento(
                tipo_dispositivo='impresora',
                dispositivo_obj=self,
                tipo_evento='registro',
                descripcion=f'Impresora registrada en el sistema. Modelo: {self.modelo.nombre}, Fabricante: {self.fabricante.nombre}',
                observaciones=f'Número de serie: {self.numero_serie}, Ubicación: {self.lugar.nombre}'
            )
        else:
            # Detectar cambios específicos
            if old_values.get('estado') != self.estado.nombre:
                Bitacora.registrar_evento(
                    tipo_dispositivo='impresora',
                    dispositivo_obj=self,
                    tipo_evento='cambio_estado',
                    descripcion=f'Cambio de estado de {old_values.get("estado")} a {self.estado.nombre}',
                    valor_anterior=old_values.get('estado'),
                    valor_nuevo=self.estado.nombre
                )
            
            if old_values.get('lugar') != self.lugar.nombre:
                Bitacora.registrar_evento(
                    tipo_dispositivo='impresora',
                    dispositivo_obj=self,
                    tipo_evento='cambio_ubicacion',
                    descripcion=f'Cambio de ubicación de {old_values.get("lugar")} a {self.lugar.nombre}',
                    valor_anterior=old_values.get('lugar'),
                    valor_nuevo=self.lugar.nombre
                )
            
            if old_values.get('valor_adquisicion') != getattr(self, 'valor_adquisicion', None):
                Bitacora.registrar_evento(
                    tipo_dispositivo='impresora',
                    dispositivo_obj=self,
                    tipo_evento='actualizacion',
                    descripcion=f'Actualización del valor de adquisición',
                    valor_anterior=str(old_values.get('valor_adquisicion')) if old_values.get('valor_adquisicion') else 'No definido',
                    valor_nuevo=str(getattr(self, 'valor_adquisicion', None)) if getattr(self, 'valor_adquisicion', None) else 'No definido'
                )
    
    def __str__(self):
        return f"{self.nombre} - {self.numero_serie}"
    
    @property
    def garantia_vigente(self):
        """Retorna True si la garantía está vigente"""
        return date.today() <= self.fecha_finalizacion_garantia
    
    @property
    def dias_restantes_garantia(self):
        """Retorna los días restantes de garantía"""
        if self.garantia_vigente:
            return (self.fecha_finalizacion_garantia - date.today()).days
        return 0


class Factura(models.Model):
    """Factura de movimiento de activos entre lugares."""

    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False)
    numero = models.CharField(max_length=60, unique=True)
    qr_token = models.UUIDField(default=uuid_lib.uuid4, editable=False)
    fecha_emision = models.DateTimeField(default=timezone.now)
    lugar_destino = models.ForeignKey(
        Lugares,
        on_delete=models.PROTECT,
        related_name='facturas_destino'
    )
    lugar_origen = models.ForeignKey(
        Lugares,
        on_delete=models.PROTECT,
        related_name='facturas_origen',
        null=True,
        blank=True
    )
    observaciones = models.TextField(blank=True)
    emitido_por = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name = 'Factura de Activos'
        verbose_name_plural = 'Facturas de Activos'
        ordering = ['-fecha_emision']

    def __str__(self) -> str:
        return f"Factura {self.numero}"

    def save(self, *args, **kwargs) -> None:
        if not self.numero:
            hoy = timezone.now()
            base = hoy.strftime('%Y%m%d')
            consecutivo = 1
            while True:
                posible = f"FAC-{base}-{consecutivo:03d}"
                if not Factura.objects.filter(numero=posible).exists():
                    self.numero = posible
                    break
                consecutivo += 1
        if not self.uuid:
            self.uuid = uuid_lib.uuid4()
        if not self.qr_token:
            self.qr_token = uuid_lib.uuid4()
        super().save(*args, **kwargs)


class FacturaActivo(models.Model):
    """Detalle de activos incluidos en una factura."""

    COMPUTADORA = 'computadora'
    IMPRESORA = 'impresora'
    MONITOR = 'monitor'
    TECNOLOGIA_MEDICA = 'tecnologia_medica'
    INSUMO = 'insumo'

    TIPO_ACTIVO_CHOICES = (
        (COMPUTADORA, 'Computadora'),
        (IMPRESORA, 'Impresora'),
        (MONITOR, 'Monitor'),
        (TECNOLOGIA_MEDICA, 'Tecnología Médica'),
        (INSUMO, 'Insumo'),
    )

    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='activos'
    )
    tipo_activo = models.CharField(max_length=20, choices=TIPO_ACTIVO_CHOICES)
    activo_id = models.PositiveIntegerField()
    numero_serie = models.CharField(max_length=200)
    nombre_activo = models.CharField(max_length=400)
    estado_previo = models.CharField(max_length=120, blank=True)
    lugar_previo = models.CharField(max_length=250, blank=True)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Activo facturado'
        verbose_name_plural = 'Activos facturados'
        ordering = ['factura', 'tipo_activo', 'numero_serie']
        unique_together = (
            ('factura', 'tipo_activo', 'activo_id'),
        )

    def __str__(self) -> str:
        if self.cantidad and self.cantidad != 1:
            return f"{self.factura.numero} - {self.nombre_activo} (x{self.cantidad})"
        return f"{self.factura.numero} - {self.nombre_activo}"


class EnvioServicioProveedor(models.Model):
    """Registro de envío de activos a servicio/reparación de proveedor externo."""

    uuid = models.UUIDField(default=uuid_lib.uuid4, editable=False, unique=True)
    numero = models.CharField(max_length=60, unique=True, verbose_name="Número de Envío")
    fecha_envio = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Envío")
    
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='envios_servicio',
        verbose_name="Proveedor de Servicio"
    )
    
    motivo_envio = models.TextField(verbose_name="Motivo del Envío")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    
    # Fechas de seguimiento
    fecha_estimada_retorno = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha Estimada de Retorno"
    )
    fecha_retorno_real = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha Real de Retorno"
    )
    
    # Estados
    ESTADO_CHOICES = [
        ('enviado', 'Enviado'),
        ('en_reparacion', 'En Reparación'),
        ('reparado', 'Reparado'),
        ('retornado', 'Retornado'),
        ('cancelado', 'Cancelado'),
    ]
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='enviado',
        verbose_name="Estado"
    )
    
    # Costos
    costo_servicio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Costo del Servicio"
    )
    moneda = models.CharField(
        max_length=3,
        default='UYU',
        choices=[('UYU', 'UYU'), ('USD', 'USD')],
        verbose_name="Moneda"
    )
    
    # Auditoría
    emitido_por = models.CharField(max_length=150, blank=True, verbose_name="Emitido Por")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Envío a Servicio de Proveedor'
        verbose_name_plural = 'Envíos a Servicio de Proveedores'
        ordering = ['-fecha_envio']

    def __str__(self) -> str:
        return f"Envío {self.numero} - {self.proveedor.nombre}"

    def save(self, *args, **kwargs) -> None:
        # Generate unique number if not set
        if not self.numero:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.numero = f"ENV-{timestamp}"
        super().save(*args, **kwargs)


class EnvioServicioActivo(models.Model):
    """Detalle de activos incluidos en un envío a servicio de proveedor."""

    TIPO_ACTIVO_CHOICES = [
        ('computadora', 'Computadora'),
        ('impresora', 'Impresora'),
        ('monitor', 'Monitor'),
        ('networking', 'Networking'),
        ('telefonia', 'Telefonía'),
        ('periferico', 'Periférico'),
        ('tecnologia_medica', 'Tecnología Médica'),
    ]

    envio = models.ForeignKey(
        EnvioServicioProveedor,
        on_delete=models.CASCADE,
        related_name='activos',
        verbose_name="Envío"
    )
    tipo_activo = models.CharField(
        max_length=20,
        choices=TIPO_ACTIVO_CHOICES,
        verbose_name="Tipo de Activo"
    )
    activo_id = models.PositiveIntegerField(verbose_name="ID del Activo")
    numero_serie = models.CharField(max_length=200, verbose_name="Número de Serie")
    nombre_activo = models.CharField(max_length=400, verbose_name="Nombre del Activo")
    
    # Estado previo
    estado_previo = models.CharField(max_length=120, blank=True, verbose_name="Estado Previo")
    lugar_previo = models.CharField(max_length=250, blank=True, verbose_name="Lugar Previo")
    
    # Detalles del servicio
    problema_reportado = models.TextField(blank=True, verbose_name="Problema Reportado")
    diagnostico_proveedor = models.TextField(blank=True, verbose_name="Diagnóstico del Proveedor")
    reparacion_realizada = models.TextField(blank=True, verbose_name="Reparación Realizada")
    
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Activo en Servicio'
        verbose_name_plural = 'Activos en Servicio'
        ordering = ['envio', 'tipo_activo', 'numero_serie']
        unique_together = (
            ('envio', 'tipo_activo', 'activo_id'),
        )

    def __str__(self) -> str:
        return f"{self.envio.numero} - {self.nombre_activo}"


class OrdenServicio(models.Model):
    """Modelo para gestionar órdenes de servicio, mantenimiento y reparación de dispositivos"""
    
    TIPO_SERVICIO_CHOICES = [
        ('mantenimiento_preventivo', 'Mantenimiento Preventivo'),
        ('mantenimiento_correctivo', 'Mantenimiento Correctivo'),
        ('reparacion', 'Reparación'),
        ('calibracion', 'Calibración'),
        ('instalacion', 'Instalación'),
        ('actualizacion', 'Actualización'),
        ('diagnostico', 'Diagnóstico'),
        ('limpieza', 'Limpieza'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('en_espera_repuesto', 'En Espera de Repuesto'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    TIPO_DISPOSITIVO_CHOICES = [
        ('computadora', 'Computadora'),
        ('impresora', 'Impresora'),
        ('monitor', 'Monitor'),
        ('networking', 'Networking'),
        ('telefonia', 'Telefonía'),
        ('periferico', 'Periférico'),
        ('tecnologia_medica', 'Tecnología Médica'),
        ('insumo', 'Insumo'),
        ('software', 'Software'),
    ]
    
    # Identificación de la orden
    numero_orden = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número de Orden",
        editable=False
    )
    
    # Tipo de servicio
    tipo_servicio = models.CharField(
        max_length=50,
        choices=TIPO_SERVICIO_CHOICES,
        verbose_name="Tipo de Servicio"
    )
    
    # Estado de la orden
    estado = models.CharField(
        max_length=30,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name="Estado"
    )
    
    # Prioridad
    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default='media',
        verbose_name="Prioridad"
    )
    
    # Dispositivo relacionado (Generic Foreign Key simulado)
    tipo_dispositivo = models.CharField(
        max_length=20,
        choices=TIPO_DISPOSITIVO_CHOICES,
        verbose_name="Tipo de Dispositivo"
    )
    dispositivo_id = models.PositiveIntegerField(
        verbose_name="ID del Dispositivo"
    )
    dispositivo_nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del Dispositivo",
        editable=False
    )
    dispositivo_numero_serie = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número de Serie",
        editable=False
    )
    
    # Descripción del problema/servicio
    descripcion_problema = models.TextField(
        verbose_name="Descripción del Problema/Necesidad"
    )
    
    # Diagnóstico y solución
    diagnostico = models.TextField(
        blank=True,
        null=True,
        verbose_name="Diagnóstico"
    )
    solucion_aplicada = models.TextField(
        blank=True,
        null=True,
        verbose_name="Solución Aplicada"
    )
    
    # Personal
    solicitante = models.CharField(
        max_length=200,
        verbose_name="Solicitante"
    )
    tecnico_asignado = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Técnico Asignado"
    )
    
    # Fechas
    fecha_solicitud = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Solicitud"
    )
    fecha_inicio = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fecha de Inicio"
    )
    fecha_finalizacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fecha de Finalización"
    )
    fecha_estimada = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha Estimada de Finalización"
    )
    
    # Costos
    costo_mano_obra = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Costo de Mano de Obra"
    )
    costo_repuestos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Costo de Repuestos"
    )
    costo_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Costo Total",
        editable=False
    )
    moneda = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default='UYU',
        verbose_name="Moneda"
    )
    
    # Repuestos utilizados
    repuestos_utilizados = models.TextField(
        blank=True,
        null=True,
        verbose_name="Repuestos Utilizados",
        help_text="Lista de repuestos utilizados en el servicio"
    )
    
    # Observaciones
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones"
    )
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Orden de Servicio"
        verbose_name_plural = "Órdenes de Servicio"
        ordering = ['-fecha_solicitud']
        indexes = [
            models.Index(fields=['tipo_dispositivo', 'dispositivo_id']),
            models.Index(fields=['estado']),
            models.Index(fields=['prioridad']),
            models.Index(fields=['tecnico_asignado']),
            models.Index(fields=['fecha_solicitud']),
        ]
    
    def clean(self):
        """Validaciones personalizadas"""
        # Validar que si está completada, tenga fecha de finalización
        if self.estado == 'completada' and not self.fecha_finalizacion:
            raise ValidationError({
                'fecha_finalizacion': 'Debe especificar la fecha de finalización para órdenes completadas.'
            })
        
        # Validar que si está en proceso, tenga fecha de inicio
        if self.estado == 'en_proceso' and not self.fecha_inicio:
            raise ValidationError({
                'fecha_inicio': 'Debe especificar la fecha de inicio para órdenes en proceso.'
            })
    
    def save(self, *args, **kwargs):
        # Generar número de orden automáticamente
        if not self.numero_orden:
            hoy = timezone.now()
            base = hoy.strftime('%Y%m%d')
            consecutivo = 1
            while True:
                posible = f"OS-{base}-{consecutivo:04d}"
                if not OrdenServicio.objects.filter(numero_orden=posible).exists():
                    self.numero_orden = posible
                    break
                consecutivo += 1
        
        # Calcular costo total
        mano_obra = self.costo_mano_obra or 0
        repuestos = self.costo_repuestos or 0
        self.costo_total = mano_obra + repuestos
        
        # Obtener información del dispositivo
        if not self.dispositivo_nombre:
            # Mapeo de tipos de dispositivo a modelos
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
            
            model_class = device_models.get(self.tipo_dispositivo)
            if model_class:
                try:
                    dispositivo = model_class.objects.get(pk=self.dispositivo_id)
                    self.dispositivo_nombre = dispositivo.nombre
                    if hasattr(dispositivo, 'numero_serie'):
                        self.dispositivo_numero_serie = dispositivo.numero_serie
                except model_class.DoesNotExist:
                    pass
        
        # Detectar cambios de estado
        is_new = self.pk is None
        old_estado = None
        
        if not is_new:
            try:
                old_obj = OrdenServicio.objects.get(pk=self.pk)
                old_estado = old_obj.estado
            except OrdenServicio.DoesNotExist:
                pass
        
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Registrar en bitácora cuando se crea o cambia estado
        if is_new:
            Bitacora.registrar_evento(
                tipo_dispositivo=self.tipo_dispositivo,
                dispositivo_obj=self if hasattr(self, 'nombre') else type('obj', (), {'pk': self.dispositivo_id, 'nombre': self.dispositivo_nombre})(),
                tipo_evento='mantenimiento',
                descripcion=f'Orden de servicio creada: {self.get_tipo_servicio_display()}',
                observaciones=f'Orden {self.numero_orden} - Prioridad: {self.get_prioridad_display()}'
            )
        elif old_estado and old_estado != self.estado:
            # Registrar cambio de estado
            if self.estado == 'completada':
                tipo_evento = 'mantenimiento'
            elif self.estado == 'en_proceso':
                tipo_evento = 'mantenimiento'
            else:
                tipo_evento = 'actualizacion'
            
            # Crear objeto temporal para registrar en bitácora
            temp_obj = type('TempObj', (), {
                'pk': self.dispositivo_id,
                'nombre': self.dispositivo_nombre
            })()
            
            Bitacora.registrar_evento(
                tipo_dispositivo=self.tipo_dispositivo,
                dispositivo_obj=temp_obj,
                tipo_evento=tipo_evento,
                descripcion=f'Orden {self.numero_orden} cambió de estado: {old_estado} → {self.estado}',
                observaciones=self.solucion_aplicada or ''
            )
    
    def __str__(self):
        return f"{self.numero_orden} - {self.dispositivo_nombre}"
    
    @property
    def tiempo_resolucion(self):
        """Calcula el tiempo de resolución en horas"""
        if self.fecha_inicio and self.fecha_finalizacion:
            delta = self.fecha_finalizacion - self.fecha_inicio
            return round(delta.total_seconds() / 3600, 2)  # Convertir a horas
        return None
    
    @property
    def esta_vencida(self):
        """Verifica si la orden está vencida según fecha estimada"""
        if self.fecha_estimada and self.estado not in ['completada', 'cancelada']:
            return date.today() > self.fecha_estimada
        return False
    
    @property
    def dias_pendiente(self):
        """Calcula cuántos días lleva pendiente"""
        if self.estado in ['pendiente', 'en_proceso', 'en_espera_repuesto']:
            delta = timezone.now() - self.fecha_solicitud
            return delta.days
        return 0
