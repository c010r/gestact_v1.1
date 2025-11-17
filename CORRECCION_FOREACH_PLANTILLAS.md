# Corrección de Error "plantillas.forEach is not a function"

## Problema

Al intentar gestionar plantillas, aparecía el siguiente error en la consola:

```
Error: TypeError: plantillas.forEach is not a function
    mostrarGestionPlantillas http://localhost:8000/static/inventario/js/plantillas.js:295
```

## Causa

Django REST Framework tenía configurada la paginación global en `settings.py`:

```python
'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
'PAGE_SIZE': 20
```

Esto hacía que el endpoint `/api/plantillas-dispositivo/` devolviera un objeto paginado:

```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [...]
}
```

Pero el JavaScript esperaba un array directo: `[...]`

## Solución Implementada

### 1. Desactivar Paginación en PlantillaDispositivoViewSet

**Archivo:** `inventario/views.py`

```python
class PlantillaDispositivoViewSet(viewsets.ModelViewSet):
    # ... campos existentes ...
    pagination_class = None  # Desactivar paginación para plantillas
```

**Justificación:** Las plantillas son pocas en cantidad (normalmente < 50) y no requieren paginación. Esto simplifica la respuesta de la API.

### 2. Manejo Defensivo en JavaScript

**Archivo:** `inventario/static/inventario/js/plantillas.js`

Se agregó manejo para ambos formatos (array directo o respuesta paginada) como medida de seguridad:

#### En cargarListaPlantillas():
```javascript
fetch(`/api/plantillas-dispositivo/?tipo_dispositivo=${this.deviceType}`)
.then(response => response.json())
.then(data => {
    console.log('Respuesta del servidor (lista):', data);
    // Manejar respuesta paginada o array directo
    const plantillas = Array.isArray(data) ? data : (data.results || []);
    this.mostrarListaPlantillas(plantillas, container);
})
```

#### En cargarGestionPlantillas():
```javascript
fetch(`/api/plantillas-dispositivo/?tipo_dispositivo=${this.deviceType}`)
.then(response => response.json())
.then(data => {
    console.log('Respuesta del servidor:', data);
    // Manejar respuesta paginada o array directo
    const plantillas = Array.isArray(data) ? data : (data.results || []);
    this.mostrarGestionPlantillas(plantillas, container);
})
```

#### En mostrarGestionPlantillas():
```javascript
mostrarGestionPlantillas(plantillas, container) {
    if (!Array.isArray(plantillas) || plantillas.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No hay plantillas disponibles</div>';
        return;
    }
    // ... resto del código ...
}
```

### 3. Logs de Depuración

Se agregaron logs en consola para facilitar la depuración:
- `console.log('Respuesta del servidor:', data)` en cargarGestionPlantillas()
- `console.log('Respuesta del servidor (lista):', data)` en cargarListaPlantillas()

Estos logs ayudan a verificar el formato de la respuesta durante el desarrollo.

## Resultado

✅ El endpoint ahora devuelve un array directo: `[{id: 1, nombre: "..."}, ...]`  
✅ `plantillas.forEach()` funciona correctamente  
✅ La lista de plantillas se carga sin errores  
✅ La gestión de plantillas funciona correctamente  
✅ El código es robusto y maneja ambos formatos por si se reactiva la paginación

## Archivos Modificados

1. `inventario/views.py` - Agregado `pagination_class = None` al ViewSet
2. `inventario/static/inventario/js/plantillas.js` - Manejo defensivo de respuestas en 2 funciones

## Prueba

1. Ve a http://127.0.0.1:8000/computadoras/crear/
2. Abre el tab "Plantillas"
3. Haz clic en "Gestionar Plantillas"
4. Verifica que no aparece el error `forEach is not a function`
5. Verifica en la consola del navegador que los logs muestran un array: `[...]`

## Notas Técnicas

- **Paginación en DRF:** Cuando está activa, envuelve los resultados en `{count, next, previous, results}`
- **Array.isArray():** Método seguro para verificar si una variable es un array
- **Operador ternario:** `Array.isArray(data) ? data : (data.results || [])` extrae el array del formato correcto
- **Validación defensiva:** `!Array.isArray(plantillas) || plantillas.length === 0` previene errores si el valor no es un array válido

## Alternativa Considerada (No Implementada)

Se consideró mantener la paginación y ajustar solo el JavaScript, pero se descartó porque:
1. Las plantillas son pocas en cantidad
2. La paginación agrega complejidad innecesaria
3. El usuario espera ver todas las plantillas disponibles de una vez
4. La respuesta sin paginar es más simple y directa
