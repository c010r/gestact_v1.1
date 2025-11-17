from django import forms

from .models import (
    Computadora,
    Impresora,
    Monitor,
    Networking,
    Telefonia,
    Periferico,
    TecnologiaMedica,
    Insumo,
    Software,
    OrdenServicio,
    generar_numero_inventario,
)
from .widgets import TreeSelectWidget


class DatePickerInput(forms.DateInput):
    """Widget de calendario HTML5 para seleccionar fechas."""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'type': 'date',
            'class': 'form-control',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format='%Y-%m-%d')


class SpanishDateInput(forms.TextInput):
    """Widget para manejar fechas en formato dd/mm/YYYY."""

    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'spanish-date-input',
            'placeholder': 'dd/mm/aaaa',
            'pattern': '[0-9]{2}/[0-9]{2}/[0-9]{4}',
            'title': 'Formato: dd/mm/aaaa',
            'maxlength': '10',
            'data-date-format': 'dd/mm/yyyy',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

    def format_value(self, value):
        if not value:
            return value
        if hasattr(value, 'strftime'):
            return value.strftime('%d/%m/%Y')
        if isinstance(value, str) and len(value) == 10 and value[4] == '-':
            try:
                year, month, day = value.split('-')
            except ValueError:
                return value
            return f'{day}/{month}/{year}'
        return value

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)
        if value and '/' in value and len(value) == 10:
            try:
                day, month, year = value.split('/')
            except ValueError:
                return value
            return f'{year}-{month.zfill(2)}-{day.zfill(2)}'
        return value


class FormControlMixin:
    """Mixin que aplica clases Bootstrap a los campos."""

    control_exempt = (forms.CheckboxInput, forms.RadioSelect)

    def apply_form_control(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, self.control_exempt):
                continue
            current = widget.attrs.get('class', '').strip()
            classes = f'{current} form-control'.strip()
            widget.attrs['class'] = classes


class ComputadoraForm(FormControlMixin, forms.ModelForm):
    """Formulario para crear y editar computadoras."""

    class Meta:
        model = Computadora
        exclude = [
            'fecha_finalizacion_garantia',
            'fecha_creacion',
            'fecha_modificacion',
        ]
        widgets = {
            'lugar': TreeSelectWidget(),
            'fecha_adquisicion': DatePickerInput(),
            'comentarios': forms.Textarea(attrs={'rows': 4}),
            'numero_serie': forms.TextInput(attrs={'required': 'required'}),
            'numero_inventario': forms.TextInput(
                attrs={'required': 'required'}
            ),
            'valor_adquisicion': forms.NumberInput(attrs={'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
            'anos_garantia': forms.NumberInput(attrs={'min': '1'}),
            'direccion_ip': forms.TextInput(
                attrs={'placeholder': '192.168.1.100'}
            ),
            'direccion_mac': forms.TextInput(
                attrs={'placeholder': 'AA:BB:CC:DD:EE:FF'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_form_control()
        self.fields['nombre'].required = True
        self.fields['numero_inventario'].required = True
        self.fields['numero_serie'].required = True
        self.fields['tipo_computadora'].required = True
        self.fields['estado'].required = True
        self.fields['lugar'].required = True

        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            if not instance.nombre and instance.modelo and instance.numero_serie:
                instance.nombre = f"{instance.modelo.nombre}/{instance.numero_serie}"

            if not instance.numero_inventario:
                descriptor = None
                if instance.modelo_id:
                    descriptor = instance.modelo.nombre
                elif instance.tipo_computadora_id:
                    descriptor = instance.tipo_computadora.nombre
                elif instance.fabricante_id:
                    descriptor = instance.fabricante.nombre

                generado = generar_numero_inventario(
                    lugar=getattr(instance, 'lugar', None),
                    descriptor=descriptor or instance.nombre,
                    referencia=instance.numero_serie,
                )
                if generado:
                    instance.numero_inventario = generado

            if instance.nombre:
                self.initial.setdefault('nombre', instance.nombre)
                self.fields['nombre'].initial = instance.nombre

            if instance.numero_inventario:
                self.initial.setdefault('numero_inventario', instance.numero_inventario)
                self.fields['numero_inventario'].initial = instance.numero_inventario


class ImpresoraForm(FormControlMixin, forms.ModelForm):
    """Formulario para crear y editar impresoras."""

    class Meta:
        model = Impresora
        exclude = [
            'fecha_finalizacion_garantia',
            'fecha_creacion',
            'fecha_modificacion',
        ]
        widgets = {
            'lugar': TreeSelectWidget(),
            'fecha_adquisicion': DatePickerInput(),
            'comentarios': forms.Textarea(attrs={'rows': 4}),
            'numero_serie': forms.TextInput(),
            'numero_inventario': forms.TextInput(attrs={'readonly': 'readonly'}),
            'valor_adquisicion': forms.NumberInput(attrs={'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
            'anos_garantia': forms.NumberInput(attrs={'min': '1'}),
            'insumo_toner_extra': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_toner_extra': forms.NumberInput(attrs={'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_form_control()

        from django.db.models import Q

        toner_qs = Insumo.objects.filter(
            Q(tipo_insumo__nombre__icontains='toner')
            | Q(tipo_insumo__nombre__icontains='tóner')
        ).distinct().order_by('nombre')
        self.fields['insumo_toner_extra'].queryset = toner_qs
        self.fields['insumo_toner_extra'].empty_label = 'Seleccionar tóner…'
        self.fields['requiere_toner_extra'].widget.attrs.setdefault('class', 'form-check-input')

        if not self.instance.pk and not self.is_bound:
            if toner_qs.exists():
                self.fields['insumo_toner_extra'].initial = toner_qs.first().pk
                self.fields['requiere_toner_extra'].initial = True
                self.fields['cantidad_toner_extra'].initial = 1


class MonitorForm(FormControlMixin, forms.ModelForm):
    """Formulario para crear y editar monitores."""

    class Meta:
        model = Monitor
        exclude = [
            'fecha_finalizacion_garantia',
            'fecha_creacion',
            'fecha_modificacion',
        ]
        widgets = {
            'lugar': TreeSelectWidget(),
            'fecha_adquisicion': DatePickerInput(),
            'comentarios': forms.Textarea(attrs={'rows': 4}),
            'numero_serie': forms.TextInput(),
            'numero_inventario': forms.TextInput(attrs={'readonly': 'readonly'}),
            'valor_adquisicion': forms.NumberInput(attrs={'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
            'anos_garantia': forms.NumberInput(attrs={'min': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_form_control()


class NetworkingForm(FormControlMixin, forms.ModelForm):
    """Formulario para equipos de networking."""

    class Meta:
        model = Networking
        exclude = [
            'fecha_finalizacion_garantia',
            'fecha_creacion',
            'fecha_modificacion',
        ]
        widgets = {
            'lugar': TreeSelectWidget(),
            'fecha_adquisicion': DatePickerInput(),
            'comentarios': forms.Textarea(attrs={'rows': 4}),
            'numero_serie': forms.TextInput(),
            'numero_inventario': forms.TextInput(attrs={'readonly': 'readonly'}),
            'valor_adquisicion': forms.NumberInput(attrs={'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
            'anos_garantia': forms.NumberInput(attrs={'min': '1'}),
            'direccion_ip': forms.TextInput(),
            'direccion_mac': forms.TextInput(),
            'firmware_version': forms.TextInput(),
            'cantidad_puertos': forms.NumberInput(attrs={'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_form_control()


class TelefoniaForm(FormControlMixin, forms.ModelForm):
    """Formulario para dispositivos de telefonía."""

    class Meta:
        model = Telefonia
        exclude = [
            'fecha_finalizacion_garantia',
            'fecha_creacion',
            'fecha_modificacion',
        ]
        widgets = {
            'lugar': TreeSelectWidget(),
            'fecha_adquisicion': DatePickerInput(),
            'comentarios': forms.Textarea(attrs={'rows': 4}),
            'numero_serie': forms.TextInput(),
            'numero_inventario': forms.TextInput(attrs={'readonly': 'readonly'}),
            'valor_adquisicion': forms.NumberInput(attrs={'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
            'anos_garantia': forms.NumberInput(attrs={'min': '1'}),
            'extension_interna': forms.TextInput(),
            'numero_linea': forms.TextInput(),
            'direccion_ip': forms.TextInput(),
            'direccion_mac': forms.TextInput(),
            'tipo_conexion': forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_form_control()


class PerifericoForm(FormControlMixin, forms.ModelForm):
    """Formulario para periféricos."""

    class Meta:
        model = Periferico
        exclude = [
            'fecha_finalizacion_garantia',
            'fecha_creacion',
            'fecha_modificacion',
        ]
        widgets = {
            'lugar': TreeSelectWidget(),
            'fecha_adquisicion': DatePickerInput(),
            'comentarios': forms.Textarea(attrs={'rows': 4}),
            'numero_serie': forms.TextInput(),
            'numero_inventario': forms.TextInput(),
            'valor_adquisicion': forms.NumberInput(attrs={'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
            'anos_garantia': forms.NumberInput(attrs={'min': '1'}),
            'tipo_conexion': forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_form_control()


class InsumoForm(FormControlMixin, forms.ModelForm):
    """Formulario para gestionar insumos."""

    class Meta:
        model = Insumo
        exclude = ['ultima_actualizacion', 'fecha_creacion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'cantidad_total': forms.NumberInput(attrs={'min': '0'}),
            'cantidad_disponible': forms.NumberInput(attrs={'min': '0'}),
            'punto_reorden': forms.NumberInput(attrs={'min': '0'}),
            'valor_unitario_estandar': forms.NumberInput(
                attrs={'step': '0.01'}
            ),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_form_control()


class SoftwareForm(FormControlMixin, forms.ModelForm):
    """Formulario para activos de software."""

    class Meta:
        model = Software
        exclude = ['fecha_creacion', 'fecha_modificacion']
        widgets = {
            'lugar': TreeSelectWidget(),
            'fecha_adquisicion': DatePickerInput(),
            'fecha_expiracion': DatePickerInput(),
            'notas': forms.Textarea(attrs={'rows': 4}),
            'version': forms.TextInput(),
            'numero_licencia': forms.TextInput(),
            'cantidad_licencias': forms.NumberInput(attrs={'min': '1'}),
            'licencias_en_uso': forms.NumberInput(attrs={'min': '0'}),
            'costo_total': forms.NumberInput(attrs={'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_form_control()


class TecnologiaMedicaForm(FormControlMixin, forms.ModelForm):
    """Formulario para tecnología médica."""

    class Meta:
        model = TecnologiaMedica
        exclude = [
            'fecha_finalizacion_garantia',
            'fecha_creacion',
            'fecha_modificacion',
        ]
        widgets = {
            'lugar': TreeSelectWidget(),
            'fecha_adquisicion': DatePickerInput(),
            'fecha_ultima_calibracion': DatePickerInput(),
            'fecha_ultimo_mantenimiento': DatePickerInput(),
            'comentarios': forms.Textarea(attrs={'rows': 4}),
            'numero_serie': forms.TextInput(),
            'numero_inventario': forms.TextInput(attrs={'readonly': 'readonly'}),
            'numero_activo_fijo': forms.TextInput(),
            'registro_sanitario': forms.TextInput(),
            'valor_adquisicion': forms.NumberInput(attrs={'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
            'anos_garantia': forms.NumberInput(attrs={'min': '1'}),
            'frecuencia_calibracion_meses': forms.NumberInput(attrs={'min': '1'}),
            'frecuencia_mantenimiento_meses': forms.NumberInput(attrs={'min': '1'}),
            'clasificacion_riesgo': forms.Select(attrs={'class': 'form-select'}),
            'area_aplicacion': forms.TextInput(
                attrs={'placeholder': 'Ej: UCI, Quirófano, Emergencia'}
            ),
            'voltaje_operacion': forms.TextInput(
                attrs={'placeholder': 'Ej: 220V'}
            ),
            'potencia': forms.TextInput(
                attrs={'placeholder': 'Ej: 1500W'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_form_control()
        
        # Hacer que los checkboxes tengan la clase correcta
        self.fields['requiere_calibracion'].widget.attrs.setdefault(
            'class', 'form-check-input'
        )
        self.fields['requiere_mantenimiento_preventivo'].widget.attrs.setdefault(
            'class', 'form-check-input'
        )
        self.fields['requiere_personal_especializado'].widget.attrs.setdefault(
            'class', 'form-check-input'
        )


class DateTimePickerInput(forms.DateTimeInput):
    """Widget de calendario HTML5 para seleccionar fecha y hora."""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'type': 'datetime-local',
            'class': 'form-control',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format='%Y-%m-%dT%H:%M')


class OrdenServicioForm(FormControlMixin, forms.ModelForm):
    """Formulario para crear y editar órdenes de servicio con búsqueda por número de serie"""
    
    # Campo adicional para búsqueda por número de serie
    buscar_numero_serie = forms.CharField(
        max_length=100,
        required=False,
        label='Número de Serie del Activo',
        help_text='Ingrese el número de serie para vincular automáticamente el activo',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: SN123456789',
            'class': 'form-control'
        })
    )

    class Meta:
        model = OrdenServicio
        exclude = [
            'numero_orden',
            'dispositivo_nombre',
            'dispositivo_numero_serie',
            'dispositivo_id',
            'tipo_dispositivo',
            'costo_total',
            'fecha_creacion',
            'fecha_modificacion',
        ]
        widgets = {
            'tipo_servicio': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'descripcion_problema': forms.Textarea(attrs={'rows': 4}),
            'diagnostico': forms.Textarea(attrs={'rows': 4}),
            'solucion_aplicada': forms.Textarea(attrs={'rows': 4}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
            'repuestos_utilizados': forms.Textarea(attrs={'rows': 3}),
            'fecha_estimada': DatePickerInput(),
            'fecha_inicio': DateTimePickerInput(),
            'fecha_finalizacion': DateTimePickerInput(),
            'costo_mano_obra': forms.NumberInput(attrs={'step': '0.01'}),
            'costo_repuestos': forms.NumberInput(attrs={'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_form_control()
        
        # Si estamos editando, prellenar el número de serie
        if self.instance and self.instance.pk:
            self.fields['buscar_numero_serie'].initial = self.instance.dispositivo_numero_serie
            self.fields['buscar_numero_serie'].widget.attrs['readonly'] = True
        
        # Campos requeridos
        self.fields['tipo_servicio'].required = True
        self.fields['prioridad'].required = True
        self.fields['descripcion_problema'].required = True
        self.fields['solicitante'].required = True
        self.fields['buscar_numero_serie'].required = True
    
    def clean_buscar_numero_serie(self):
        """Valida y busca el dispositivo por número de serie"""
        numero_serie = self.cleaned_data.get('buscar_numero_serie', '').strip()
        
        if not numero_serie:
            raise forms.ValidationError("El número de serie es obligatorio")
        
        # Si estamos editando y el número de serie no cambió, no validar
        if self.instance and self.instance.pk:
            if numero_serie == self.instance.dispositivo_numero_serie:
                return numero_serie
        
        # Mapeo de modelos
        from inventario.models import (
            Computadora, Impresora, Monitor, Networking,
            Telefonia, Periferico, TecnologiaMedica
        )
        
        dispositivo_encontrado = None
        tipo_encontrado = None
        
        # Buscar en todos los modelos
        modelos_busqueda = [
            (Computadora, 'computadora'),
            (Impresora, 'impresora'),
            (Monitor, 'monitor'),
            (Networking, 'networking'),
            (Telefonia, 'telefonia'),
            (Periferico, 'periferico'),
            (TecnologiaMedica, 'tecnologia_medica'),
        ]
        
        for modelo, tipo_dispositivo in modelos_busqueda:
            try:
                dispositivo = modelo.objects.get(numero_serie__iexact=numero_serie)
                dispositivo_encontrado = dispositivo
                tipo_encontrado = tipo_dispositivo
                break
            except modelo.DoesNotExist:
                continue
            except modelo.MultipleObjectsReturned:
                raise forms.ValidationError(
                    f"Se encontraron múltiples dispositivos con el número de serie '{numero_serie}'. "
                    "Contacte al administrador."
                )
        
        if not dispositivo_encontrado:
            raise forms.ValidationError(
                f"No se encontró ningún activo con el número de serie '{numero_serie}'. "
                "Verifique el número o registre el activo primero."
            )
        
        # Guardar información del dispositivo encontrado
        self._dispositivo_encontrado = dispositivo_encontrado
        self._tipo_dispositivo_encontrado = tipo_encontrado
        
        return numero_serie
    
    def save(self, commit=True):
        """Guarda la orden vinculándola al dispositivo encontrado"""
        instance = super().save(commit=False)
        
        # Si tenemos dispositivo encontrado, establecer los campos
        if hasattr(self, '_dispositivo_encontrado'):
            dispositivo = self._dispositivo_encontrado
            instance.tipo_dispositivo = self._tipo_dispositivo_encontrado
            instance.dispositivo_id = dispositivo.id
            instance.dispositivo_nombre = getattr(dispositivo, 'nombre', str(dispositivo))
            instance.dispositivo_numero_serie = dispositivo.numero_serie
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance
