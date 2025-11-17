# Sistema de Selección Jerárquica de Lugares

## Descripción General

Este documento describe el nuevo sistema de selección jerárquica de lugares implementado en los formularios de activos (Computadoras, Impresoras y Monitores).

## Características Implementadas

### 1. Widgets Personalizados

Se han creado dos widgets personalizados para la selección de lugares:

#### **HierarchicalSelectWidget**
- Widget simple basado en `<select>` HTML
- Muestra los lugares con indentación visual según su nivel
- Incluye iconos visuales (📁, ├─, └─) para indicar jerarquía
- Añade atributos `data-*` para uso posterior en JavaScript
- Clases CSS por nivel para estilos diferenciados

#### **TreeSelectWidget** (Recomendado)
- Widget interactivo con dropdown personalizado
- Búsqueda integrada en tiempo real
- Árbol expandible/contraíble
- Muestra ruta completa del lugar seleccionado
- Iconos diferenciados por nivel de jerarquía
- Responsive y accesible

### 2. Estilos CSS

Archivo: `inventario/static/inventario/css/tree-select.css`

Características:
- Estilos para el dropdown del árbol
- Indentación por niveles (12px base + 20px por nivel)
- Colores diferenciados por nivel
- Estados hover y selected
- Responsive design
- Transiciones suaves

### 3. JavaScript Interactivo

Archivo: `inventario/static/inventario/js/tree-select.js`

Funcionalidades:
- Construcción dinámica del árbol
- Búsqueda/filtrado de lugares
- Expandir/contraer nodos
- Selección de ubicación
- Auto-expansión de padres al buscar
- Cerrar al hacer clic fuera
- Eventos personalizados

### 4. Templates

**`hierarchical_select.html`**: Template simple para el select jerárquico básico

**`tree_select.html`**: Template avanzado con:
- Input oculto para el valor
- Display visual del valor seleccionado
- Dropdown con árbol interactivo
- Campo de búsqueda integrado

## Uso en Formularios

### Actualización de Modelos

Los formularios `ComputadoraForm`, `ImpresoraForm` y `MonitorForm` han sido actualizados para usar el widget jerárquico:

```python
from .widgets import TreeSelectWidget

class ComputadoraForm(forms.ModelForm):
    class Meta:
        model = Computadora
        widgets = {
            'lugar': TreeSelectWidget(),  # Widget jerárquico
            # ... otros widgets
        }
```

### Uso en Admin

Los ModelAdmin correspondientes ahora especifican el formulario personalizado:

```python
@admin.register(Computadora)
class ComputadoraAdmin(admin.ModelAdmin):
    form = ComputadoraForm  # Usar el formulario con widget jerárquico
    # ...
```

## Estructura de Niveles

El sistema soporta 7 niveles jerárquicos:

1. **Unidad Ejecutora** (📁) - Nivel raíz
2. **Unidad Asistencial** (🏢)
3. **Servicio** (🏥)
4. **Área** (📋)
5. **Sector** (🔧)
6. **Ubicación** (📍)
7. **Puesto** (💺) - Nivel hoja

Cada nivel tiene:
- Icono distintivo
- Color diferenciado
- Indentación específica
- Validaciones propias

## Flujo de Datos

### 1. Carga Inicial

```
Widget.get_context() 
    ↓
Consulta Lugares.objects.filter(activo=True)
    ↓
Convierte a estructura JSON
    ↓
Pasa al template como tree_data
    ↓
JavaScript construye el árbol visual
```

### 2. Selección de Lugar

```
Usuario hace clic en nodo
    ↓
JavaScript captura evento
    ↓
Actualiza input oculto con ID
    ↓
Actualiza display visual
    ↓
Cierra dropdown
    ↓
Dispara evento 'change' para validaciones
```

### 3. Búsqueda

```
Usuario escribe en campo de búsqueda
    ↓
JavaScript filtra nodos por nombre
    ↓
Oculta nodos no coincidentes
    ↓
Expande automáticamente padres de coincidencias
    ↓
Muestra solo resultados relevantes
```

## Personalización

### Cambiar el Widget

Para usar el widget simple en lugar del interactivo:

```python
widgets = {
    'lugar': HierarchicalSelectWidget(),  # Widget simple
}
```

### Personalizar Iconos

Edita la función `getIconForLevel()` en `tree-select.js`:

```javascript
getIconForLevel(nivel) {
    const icons = {
        1: '🏢',  // Tu icono personalizado
        2: '🏥',
        // ...
    };
    return icons[nivel] || '•';
}
```

### Personalizar Colores

Edita `tree-select.css`:

```css
.tree-node[data-nivel="1"] .tree-node-label {
    font-weight: bold;
    color: #tu-color;  /* Personalizar */
}
```

## Validaciones

El widget mantiene todas las validaciones del modelo Lugares:

- ✅ Solo lugares activos son seleccionables
- ✅ Respeta la jerarquía padre-hijo
- ✅ Valida niveles permitidos
- ✅ Verifica códigos únicos si aplica

## Compatibilidad

- ✅ **Navegadores**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- ✅ **Django**: 3.2+
- ✅ **Python**: 3.8+
- ✅ **Responsive**: Móvil y escritorio
- ✅ **Accesibilidad**: Teclado y lectores de pantalla

## Archivos Modificados

1. **inventario/widgets.py** - Nuevo archivo con widgets personalizados
2. **inventario/forms.py** - Actualizado con TreeSelectWidget
3. **inventario/admin.py** - Actualizado para usar formularios personalizados
4. **inventario/static/inventario/css/tree-select.css** - Nuevo archivo de estilos
5. **inventario/static/inventario/js/tree-select.js** - Nuevo archivo JavaScript
6. **inventario/templates/inventario/widgets/hierarchical_select.html** - Nuevo template
7. **inventario/templates/inventario/widgets/tree_select.html** - Nuevo template

## Ejemplos de Uso

### Crear una Computadora con Ubicación Jerárquica

1. Ir a Admin → Computadoras → Agregar
2. En el campo "Lugar", hacer clic en el dropdown
3. Buscar o navegar por el árbol
4. Expandir nodos si es necesario
5. Seleccionar el lugar específico
6. El campo mostrará la ruta completa: "UE Hospital / Cirugía / Pabellón 2"

### Buscar Ubicación

1. Hacer clic en el campo "Lugar"
2. Escribir parte del nombre en el buscador (ej: "pabellón")
3. El árbol se filtrará automáticamente
4. Los nodos padre se expandirán para mostrar coincidencias
5. Hacer clic en el resultado deseado

## Migraciones Necesarias

✅ Ya aplicadas:
- `0011_rebuild_lugares.py` - Reestructuración del modelo Lugares
- `init_tipos_nivel` - Inicialización de los 7 niveles

## Próximas Mejoras

- [ ] Agregar validación de nivel mínimo/máximo por tipo de activo
- [ ] Implementar drag & drop para reorganizar jerarquía
- [ ] Agregar vista de mapa de lugares
- [ ] Exportar/importar estructura jerárquica
- [ ] Historial de cambios de ubicación
- [ ] Alertas de sobrecarga por ubicación
- [ ] Dashboard de ocupación por nivel

## Soporte

Para problemas o consultas sobre el sistema jerárquico, consultar:
- **Documentación completa**: `JERARQUIA_LUGARES.md`
- **Modelos**: `inventario/models.py` - clase `Lugares` (líneas ~122-340)
- **Widgets**: `inventario/widgets.py`

## Notas Técnicas

### Rendimiento

- El árbol se construye una sola vez en el cliente
- Los datos se cachean en JavaScript
- Búsqueda optimizada con filtros locales
- Queries de base de datos optimizados con `select_related()`

### Seguridad

- Valores sanitizados con `mark_safe()` de Django
- JSON escapado correctamente
- Validación server-side de lugares válidos
- XSS protegido por templates de Django

### Accesibilidad

- ARIA labels implementados
- Navegación por teclado funcional
- Contraste de colores adecuado
- Screen reader compatible
