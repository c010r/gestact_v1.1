# Historial de Remitos - Vistas Tarjetas/Lista con Ordenamiento

## Descripción
Se ha mejorado el historial de remitos para incluir dos vistas diferentes (Tarjetas y Lista) con un toggle para cambiar entre ellas, y se ha implementado ordenamiento por fecha descendente (más recientes primero).

## Cambios Realizados

### 1. Ordenamiento por Fecha Descendente (`inventario/frontend_views.py`)

```python
# ANTES
facturas_list = Factura.objects.select_related(
    'lugar_destino', 'lugar_origen'
).prefetch_related('activos').all()

# DESPUÉS
facturas_list = Factura.objects.select_related(
    'lugar_destino', 'lugar_origen'
).prefetch_related('activos').order_by('-fecha_emision')
```

**Resultado:** Los remitos más recientes aparecen primero en el listado.

### 2. Toggle de Vistas (`inventario/frontend_views.py`)

Se agregó soporte para cambiar entre vista de tarjetas y lista:

```python
# Obtener modo de vista (tarjetas o lista)
vista = request.GET.get('vista', 'tarjetas')  # Por defecto tarjetas

context = {
    ...
    'vista': vista,
}
```

### 3. Botones de Cambio de Vista (Template)

Se agregó un grupo de botones en el encabezado para alternar entre vistas:

```html
<div class="btn-group" role="group" aria-label="Cambiar vista">
    <a href="?vista=tarjetas..." class="btn btn-outline-primary {% if vista == 'tarjetas' %}active{% endif %}">
        <i class="bi bi-grid-3x3-gap-fill"></i> Tarjetas
    </a>
    <a href="?vista=lista..." class="btn btn-outline-primary {% if vista == 'lista' %}active{% endif %}">
        <i class="bi bi-list-ul"></i> Lista
    </a>
</div>
```

### 4. Dos Vistas Completamente Funcionales

#### 📋 **Vista de Lista** (Tabla tradicional)
- Tabla responsive con todas las columnas
- Número de remito con ícono
- Fecha de emisión
- Lugar de destino con ícono
- Badge con cantidad de activos
- Observaciones (truncadas)
- Botones de acción (Ver detalles, Descargar PDF)
- Hover effects

#### 🎴 **Vista de Tarjetas** (Grid de cards)
- Grid responsive (1, 2 o 3 columnas según pantalla)
- Tarjetas con animación hover (elevación)
- Header con número y badge de activos
- Body con fecha, destino y observaciones
- Footer con botones de acción
- Diseño compacto y visual

### 5. Persistencia de Vista en Filtros y Paginación

Todas las acciones mantienen la vista seleccionada:

- **Filtros:** Input hidden `<input type="hidden" name="vista" value="{{ vista }}">`
- **Limpiar filtros:** `?vista={{ vista }}`
- **Paginación:** Todos los links incluyen `&vista={{ vista }}`

## Características de Cada Vista

### 🎴 Vista de Tarjetas (Por defecto)

**Ventajas:**
- ✅ Diseño moderno y visual
- ✅ Mejor aprovechamiento del espacio vertical
- ✅ Información jerarquizada
- ✅ Efectos visuales atractivos (hover, elevación)
- ✅ Responsive por naturaleza (grid adaptativo)
- ✅ Ideal para exploración rápida

**Layout:**
```
┌─────────────┬─────────────┬─────────────┐
│  FAC-001    │  FAC-002    │  FAC-003    │
│  [2 activos]│  [5 activos]│  [1 activo] │
│  22/10 16:57│  22/10 16:56│  23/10 14:07│
│  Informática│  Test Dept  │  Depósito   │
│  [Ver] [PDF]│  [Ver] [PDF]│  [Ver] [PDF]│
└─────────────┴─────────────┴─────────────┘
```

### 📋 Vista de Lista (Tabla)

**Ventajas:**
- ✅ Vista compacta de muchos remitos
- ✅ Fácil comparación entre filas
- ✅ Diseño tradicional y familiar
- ✅ Mejor para datos tabulares
- ✅ Ideal para búsquedas específicas

**Layout:**
```
┌──────────┬──────────┬─────────┬────────┬──────────┬─────────┐
│ Número   │ Fecha    │ Destino │ Activos│ Observ.  │ Acciones│
├──────────┼──────────┼─────────┼────────┼──────────┼─────────┤
│ FAC-001  │ 22/10/25 │ Info    │   2    │ Se envían│ [👁][📥]│
│ FAC-002  │ 22/10/25 │ Test    │   5    │ Urgente  │ [👁][📥]│
└──────────┴──────────┴─────────┴────────┴──────────┴─────────┘
```

## Ordenamiento Implementado

### 🔽 Orden Descendente por Fecha

Los remitos se ordenan con el criterio: **más reciente primero**

```python
.order_by('-fecha_emision')
```

**Ejemplo de orden:**
1. FAC-20251023-001 → 23/10/2025 14:07
2. FAC-20251022-002 → 22/10/2025 16:57
3. FAC-20251022-001 → 22/10/2025 16:56

Esto garantiza que:
- ✅ Los últimos remitos emitidos aparecen primero
- ✅ Facilita el acceso a información reciente
- ✅ Orden lógico para seguimiento de operaciones

## Integración con Filtros

El sistema de vistas funciona perfectamente con los filtros existentes:

- **Fecha desde/hasta:** Se mantiene al cambiar de vista
- **Lugar destino:** Se conserva en ambas vistas
- **Limpiar filtros:** Mantiene la vista seleccionada
- **Paginación:** Preserva vista y filtros activos

## Modo Oscuro

Ambas vistas están completamente integradas con el modo oscuro:

### Vista de Tarjetas (Dark Mode)
- Cards con fondo `#2d3238`
- Headers con fondo `#1a1d20`
- Texto con color `#e9ecef`
- Hover con sombra blanca sutil

### Vista de Lista (Dark Mode)
- Tabla con texto `#e9ecef`
- Filas alternadas con transparencia
- Hover con background sutil
- Headers con color `#f8f9fa`
- Bordes con color `#404448`

## Testing

Para probar la funcionalidad:

1. **Acceder al historial:**
   - Navegar a Reportes → Historial de Remitos
   - Por defecto aparece en vista de tarjetas

2. **Cambiar entre vistas:**
   - Hacer clic en "Tarjetas" o "Lista"
   - Verificar que el botón activo cambia
   - Confirmar que la vista se actualiza

3. **Verificar ordenamiento:**
   - Los remitos más nuevos deben estar primero
   - Comprobar fechas en orden descendente

4. **Probar filtros con vistas:**
   - Aplicar filtro de fecha
   - Cambiar de vista
   - Verificar que el filtro se mantiene

5. **Paginación:**
   - Cambiar de página
   - Verificar que la vista se mantiene
   - Comprobar que los filtros persisten

6. **Modo oscuro:**
   - Alternar entre modo claro/oscuro
   - Verificar contraste en ambas vistas
   - Comprobar efectos hover

## Beneficios del Sistema de Vistas

### 🎯 Flexibilidad
- Usuarios pueden elegir su vista preferida
- Cambio instantáneo sin recargar filtros

### 📱 Adaptabilidad
- Vista de tarjetas: Mejor en móviles y tablets
- Vista de lista: Mejor en pantallas grandes

### 🎨 Experiencia de Usuario
- Opción visual moderna (tarjetas)
- Opción tradicional eficiente (lista)

### 🔄 Persistencia
- La vista elegida se mantiene en toda la sesión
- No se pierde al filtrar o paginar

### ⚡ Performance
- Misma consulta para ambas vistas
- Solo cambia el template rendering
- No hay sobrecarga adicional

## Archivos Modificados

- ✅ `inventario/frontend_views.py` - Ordenamiento y soporte de vistas
- ✅ `inventario/templates/inventario/historico_remitos.html` - Toggle y ambas vistas
- ✅ Estilos CSS integrados para modo oscuro en ambas vistas

---

*Fecha de implementación: 23 de octubre de 2025*
*Versión del sistema: Django 5.2.6*
*Funcionalidad: Historial de Remitos con Toggle Tarjetas/Lista*
