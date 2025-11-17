# Sistema de Plantillas Reutilizables para Formularios de Dispositivos

## Descripción General

Este sistema de plantillas proporciona una estructura modular y reutilizable para los formularios de dispositivos en el sistema de inventario ASSE-GestACT. Permite mantener consistencia visual y funcional entre diferentes tipos de dispositivos (computadoras, impresoras, monitores) mientras facilita el mantenimiento del código.

## Estructura del Sistema

### 1. Plantilla Base
- **Archivo**: `base_device_form.html`
- **Propósito**: Plantilla principal que define la estructura común de todos los formularios de dispositivos
- **Características**:
  - Layout responsivo con columnas principal y lateral
  - Header con título dinámico y botón de retorno
  - Integración automática de secciones laterales
  - Scripts de validación básica

### 2. Plantillas Parciales (Partials)

#### Bitácora Lateral (`partials/bitacora_sidebar.html`)
- Muestra eventos recientes del dispositivo
- Enlaces para ver historial completo y registrar nuevos eventos
- Se muestra solo en modo edición

#### Acciones Rápidas (`partials/form_actions_sidebar.html`)
- Botones de acción contextuales (Guardar, Ver Detalle, Historial, etc.)
- Adaptación automática según el modo (creación/edición)
- Navegación hacia listado y detalle

#### Ayuda (`partials/help_sidebar.html`)
- Consejos y guías para el usuario
- Información sobre campos obligatorios
- Instrucciones de uso

### 3. Macros de Campos (`macros/form_fields.html`)

#### Macros Disponibles:
- `form_section(title, icon)`: Crea secciones con título e icono
- `text_field(field, label, required, help_text)`: Campo de texto con validación
- `select_field(field, label, required, help_text)`: Campo de selección
- `textarea_field(field, label, required, help_text)`: Área de texto
- `field_row(fields)`: Agrupa campos en una fila

### 4. Secciones Comunes (`sections/`)

#### Información Básica (`sections/basic_info_section.html`)
- Campos comunes: nombre, número de inventario, serie, estado, ubicación
- Campos opcionales: marca, modelo, usuario asignado, descripción
- Validaciones integradas

#### Compra y Garantía (`sections/purchase_warranty_section.html`)
- Información de adquisición: fecha, precio, proveedor, factura
- Datos de garantía: vencimiento, tipo, observaciones
- Campos condicionales según disponibilidad

## Uso del Sistema

### Para Crear un Nuevo Formulario

1. **Extender la plantilla base**:
```html
{% extends 'inventario/base_device_form.html' %}
```

2. **Definir las secciones del formulario**:
```html
{% block form_sections %}
    {% include 'inventario/sections/basic_info_section.html' %}
    <!-- Secciones específicas del dispositivo -->
    {% include 'inventario/sections/purchase_warranty_section.html' %}
{% endblock %}
```

3. **Agregar scripts específicos** (opcional):
```html
{% block extra_form_js %}
<script>
    // Validaciones específicas del dispositivo
</script>
{% endblock %}
```

### Variables de Contexto Requeridas

Las vistas deben proporcionar las siguientes variables:

```python
context.update({
    'device_type': 'computadora',  # Tipo de dispositivo
    'form_id': 'computadoraForm',  # ID único del formulario
    'list_url': reverse('inventario:computadora_list'),  # URL del listado
    'detail_url': reverse('inventario:computadora_detail', kwargs={'pk': object.pk}),  # URL del detalle (solo en edición)
})
```

### Ejemplo de Vista

```python
class ComputadoraCreateView(CreateView):
    model = Computadora
    form_class = ComputadoraForm
    template_name = 'inventario/computadora_form.html'
    
    def get_context_data(self, **kwargs):
        from django.urls import reverse
        context = super().get_context_data(**kwargs)
        context.update({
            'device_type': 'computadora',
            'form_id': 'computadoraForm',
            'list_url': reverse('inventario:computadora_list'),
            'detail_url': None,
        })
        return context
```

## Ventajas del Sistema

1. **Consistencia**: Todos los formularios mantienen la misma estructura y apariencia
2. **Mantenibilidad**: Cambios en una plantilla se reflejan en todos los formularios
3. **Reutilización**: Componentes comunes se definen una sola vez
4. **Escalabilidad**: Fácil agregar nuevos tipos de dispositivos
5. **Flexibilidad**: Permite personalización específica por dispositivo

## Archivos del Sistema

```
inventario/templates/inventario/
├── base_device_form.html           # Plantilla base principal
├── macros/
│   └── form_fields.html           # Macros reutilizables
├── partials/
│   ├── bitacora_sidebar.html      # Bitácora lateral
│   ├── form_actions_sidebar.html  # Acciones rápidas
│   └── help_sidebar.html          # Ayuda lateral
├── sections/
│   ├── basic_info_section.html    # Información básica
│   └── purchase_warranty_section.html # Compra y garantía
└── computadora_form.html          # Formulario específico (ejemplo)
```

## Mantenimiento

- **Agregar nuevos campos comunes**: Modificar las secciones correspondientes
- **Cambiar estilos globales**: Actualizar la plantilla base
- **Agregar nuevas validaciones**: Usar el bloque `extra_form_js`
- **Crear nuevos tipos de dispositivos**: Seguir el patrón establecido

## Notas Técnicas

- Compatible con Bootstrap 5
- Utiliza iconos de Font Awesome
- Validación JavaScript integrada
- Responsive design
- Accesibilidad mejorada con ARIA labels