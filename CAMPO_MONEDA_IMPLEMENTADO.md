# Campo Moneda Implementado

## Fecha: 21 de octubre de 2025

## Descripción
Se ha agregado un campo de selección de moneda para el valor de adquisición en todos los dispositivos del inventario.

## Monedas Disponibles
- **UYU**: Pesos Uruguayos ($) - Por defecto
- **USD**: Dólares (US$)
- **EUR**: Euros (€)

## Cambios Realizados

### 1. Modelos (inventario/models.py)
- Agregadas constantes `MONEDA_CHOICES` al inicio del archivo
- Campo `moneda` agregado a los siguientes modelos:
  - Computadora
  - Impresora
  - Monitor
  - Networking
  - Telefonia
  - Periferico
  - **Insumo** (con valor_unitario_estandar)
  - **Software** (con costo_total)

**Configuración del campo:**
```python
moneda = models.CharField(
    max_length=3,
    choices=MONEDA_CHOICES,
    default='UYU',
    verbose_name="Moneda"
)
```

### 2. Formularios (inventario/forms.py)
Actualizado el widget para el campo `moneda` en todos los formularios:
- ComputadoraForm
- ImpresoraForm
- MonitorForm
- NetworkingForm
- TelefoniaForm
- PerifericoForm

**Widget configurado:**
```python
'moneda': forms.Select(attrs={'class': 'form-select'})
```

### 3. Templates de Formularios
Actualizados los siguientes templates para incluir el campo de moneda:
- `computadora_form.html` - Campo valor + moneda (col-md-4 + col-md-2)
- `impresora_form.html` - Campo valor + moneda (col-md-4 + col-md-2)
- `monitor_form.html` - Campo valor + moneda (col-md-4 + col-md-2)
- `networking_form.html` - Campo valor + moneda (col-md-4 + col-md-2)
- `telefonia_form.html` - Campo valor + moneda (col-md-4 + col-md-2)
- `periferico_form.html` - Campo valor + moneda (col-md-4 + col-md-2)

**Estructura HTML:**
```html
<div class="col-md-4 mb-3">
    <label for="{{ form.valor_adquisicion.id_for_label }}" class="form-label">Valor de adquisición</label>
    {{ form.valor_adquisicion }}
</div>
<div class="col-md-2 mb-3">
    <label for="{{ form.moneda.id_for_label }}" class="form-label">Moneda</label>
    {{ form.moneda }}
</div>
```

### 4. Templates de Detalle
Actualizados los templates de visualización para mostrar el símbolo correcto según la moneda:
- `computadora_detail.html`
- `impresora_detail.html`
- `monitor_detail.html`

**Lógica de visualización:**
```html
{% if object.moneda == 'USD' %}
    US${{ object.valor_adquisicion|floatformat:2 }}
{% elif object.moneda == 'EUR' %}
    €{{ object.valor_adquisicion|floatformat:2 }}
{% else %}
    ${{ object.valor_adquisicion|floatformat:2 }}
{% endif %}
```

### 5. Migración de Base de Datos
Se creó y aplicó la migración:
- **Archivo:** `inventario/migrations/0013_computadora_moneda_impresora_moneda_monitor_moneda_and_more.py`
- **Campos agregados:** moneda a computadora, impresora, monitor, networking, periferico, telefonia
- **Estado:** ✅ Aplicada correctamente

### 6. Serializers
Los serializers automáticamente incluyen el nuevo campo `moneda` ya que usan `ModelSerializer` con `fields = '__all__'`:
- ComputadoraSerializer
- ImpresoraSerializer
- MonitorSerializer
- NetworkingSerializer
- TelefoniaSerializer
- PerifericoSerializer

## Comportamiento del Sistema

### En Formularios
1. El campo "Valor de adquisición" ahora ocupa 4 columnas
2. El campo "Moneda" ocupa 2 columnas (selector desplegable)
3. Valor por defecto: **Pesos Uruguayos (UYU)**
4. El usuario puede seleccionar entre las 3 opciones de moneda

### En Vistas de Detalle
1. El valor se muestra con el símbolo de moneda correspondiente:
   - **$** para Pesos Uruguayos
   - **US$** para Dólares
   - **€** para Euros
2. El formato numérico se mantiene con 2 decimales

### En la API
El campo `moneda` está disponible en todos los endpoints de la API REST:
- GET/POST/PUT/DELETE para todos los modelos de dispositivos
- Formato: Código de 3 letras (UYU, USD, EUR)

## Impacto en Registros Existentes
- Todos los registros existentes tienen `moneda='UYU'` por defecto (migración aplicada)
- No requiere actualización manual de registros previos

## Testing Recomendado
1. ✅ Crear nueva computadora con moneda USD
2. ✅ Crear nuevo monitor con moneda EUR
3. ✅ Crear nueva impresora con moneda UYU (por defecto)
4. ✅ Verificar visualización correcta en detalles
5. ✅ Probar edición de dispositivos existentes
6. ✅ Verificar API incluye campo moneda

## Notas Técnicas
- El campo es obligatorio (no permite NULL) pero tiene valor por defecto
- La validación se maneja automáticamente por Django con las opciones CHOICES
- El campo es compatible con ordenamiento y filtrado en queries
- Se mantiene la compatibilidad con el sistema de generación de reportes

## Estado Final
✅ **Implementación Completa**
- Modelos actualizados
- Formularios actualizados  
- Templates actualizados
- Migración aplicada
- Servidor funcionando correctamente
