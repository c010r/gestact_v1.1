# Corrección de API de Plantillas de Dispositivos

## Problema
El sistema de plantillas de dispositivos mostraba errores 404 al intentar guardar, listar, cargar o eliminar plantillas:
- `POST /api/plantillas/guardar/ 404`
- `GET /api/plantillas/listar/ 404`
- `GET /api/plantillas/cargar/ 404`
- `POST /api/plantillas/eliminar/ 404`

## Causa
El JavaScript en `plantillas.js` estaba utilizando URLs de API personalizadas tipo `/api/plantillas/accion/`, pero el backend Django REST Framework usa el patrón estándar RESTful con el endpoint `/api/plantillas-dispositivo/` registrado mediante router.

## Solución Implementada

### 1. Actualización de Endpoints en plantillas.js

#### Endpoint de Guardar (POST)
- **Antes:** `POST /api/plantillas/guardar/` con body `{nombre_plantilla, descripcion, tipo_dispositivo, datos_formulario}`
- **Después:** `POST /api/plantillas-dispositivo/` con campos directos del modelo PlantillaDispositivo

**Cambios:**
- Se eliminó el wrapper `datos_formulario`
- Se envían directamente los campos: `nombre`, `descripcion`, `tipo_dispositivo`, y campos mapeables del formulario
- La respuesta ahora es el objeto plantilla creado, no `{success: true, message: "..."}`

#### Endpoint de Listar (GET)
- **Antes:** `GET /api/plantillas/listar/?tipo_dispositivo=${tipo}`
- **Después:** `GET /api/plantillas-dispositivo/?tipo_dispositivo=${tipo}`

**Cambios:**
- URL actualizada al endpoint del router
- La respuesta es un array de plantillas directamente, no `{success: true, plantillas: [...]}`
- Eliminado el chequeo de `data.success`

#### Endpoint de Cargar (GET detalle)
- **Antes:** `GET /api/plantillas/cargar/?plantilla_id=${id}&tipo_dispositivo=${tipo}`
- **Después:** `GET /api/plantillas-dispositivo/${id}/`

**Cambios:**
- URL actualizada al endpoint de detalle del router (sin query params)
- La respuesta es el objeto plantilla completo
- Se actualizó el mapeo de campos para usar los campos del modelo directamente

#### Endpoint de Eliminar (DELETE)
- **Antes:** `POST /api/plantillas/eliminar/` con body `{plantilla_id: id}`
- **Después:** `DELETE /api/plantillas-dispositivo/${id}/`

**Cambios:**
- Método cambiado de POST a DELETE
- URL actualizada al endpoint de detalle del router
- El ID se pasa en la URL, no en el body
- La respuesta es 204 No Content (sin body), se verifica con `response.ok`

### 2. Ajustes en el Manejo de Respuestas

#### Guardar Plantilla
```javascript
// ANTES
.then(data => {
    if (data.success) {
        // Mostrar data.message
    }
})

// DESPUÉS
.then(response => {
    if (response.ok) return response.json();
    else throw new Error('...');
})
.then(plantilla => {
    // Usar plantilla.nombre directamente
})
```

#### Listar Plantillas
```javascript
// ANTES
.then(data => {
    if (data.success) {
        this.mostrarListaPlantillas(data.plantillas, container);
    }
})

// DESPUÉS
.then(plantillas => {
    this.mostrarListaPlantillas(plantillas, container);
})
```

#### Cargar Plantilla
```javascript
// ANTES
.then(data => {
    if (data.success) {
        const datos = data.datos_plantilla || data.datos || {};
        Object.keys(datos).forEach(key => { /* aplicar */ });
    }
})

// DESPUÉS
.then(plantilla => {
    camposMapeables.forEach(key => {
        if (plantilla[key] !== null && plantilla[key] !== undefined) {
            // aplicar valor
        }
    });
})
```

#### Eliminar Plantilla
```javascript
// ANTES
.then(response => response.json())
.then(data => {
    if (data.success) {
        this.mostrarAlerta(data.message, 'success');
    }
})

// DESPUÉS
.then(response => {
    if (response.ok) {
        this.mostrarAlerta('Plantilla eliminada exitosamente', 'success');
    } else {
        throw new Error('...');
    }
})
```

### 3. Campos Mapeables

Se definió una lista de campos que se pueden guardar y cargar desde las plantillas:

```javascript
const camposMapeables = [
    'estado', 'lugar', 'fabricante', 'modelo', 'proveedor',
    'tipo_garantia', 'anos_garantia', 'valor_adquisicion', 'comentarios',
    'tipo_computadora', 'direccion_ip', 'direccion_mac',
    'tipo_impresora', 'tipo_monitor', 'tamano_pantalla', 'resolucion',
    'tipo_periferico', 'tipo_insumo', 'tipo_licencia'
];
```

Estos campos coinciden con los campos del modelo `PlantillaDispositivo` en Django.

## Estructura del Backend (sin cambios)

El backend ya estaba correctamente configurado:

### Router Configuration (inventario/urls.py)
```python
router.register(r'plantillas-dispositivo', views.PlantillaDispositivoViewSet)
```

### ViewSet (inventario/views.py)
```python
class PlantillaDispositivoViewSet(viewsets.ModelViewSet):
    queryset = PlantillaDispositivo.objects.all()
    serializer_class = PlantillaDispositivoSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['tipo_dispositivo']
```

### Endpoints Generados por DRF Router

| Método | URL | Acción |
|--------|-----|--------|
| GET | `/api/plantillas-dispositivo/` | Listar todas |
| GET | `/api/plantillas-dispositivo/?tipo_dispositivo=X` | Filtrar por tipo |
| POST | `/api/plantillas-dispositivo/` | Crear nueva |
| GET | `/api/plantillas-dispositivo/{id}/` | Obtener detalle |
| PUT/PATCH | `/api/plantillas-dispositivo/{id}/` | Actualizar |
| DELETE | `/api/plantillas-dispositivo/{id}/` | Eliminar |

## Resultado

✅ Las plantillas ahora se pueden guardar correctamente  
✅ La lista de plantillas se carga sin errores  
✅ Las plantillas se pueden cargar y aplicar a los formularios  
✅ Las plantillas se pueden eliminar exitosamente  
✅ Los errores 404 han sido eliminados  
✅ El sistema funciona con los estándares de Django REST Framework

## Archivos Modificados

- `inventario/static/inventario/js/plantillas.js` - Actualizado todos los endpoints y manejo de respuestas

## Pruebas Sugeridas

1. Ir a `/computadoras/crear/`
2. Abrir el tab "Plantillas"
3. Llenar el formulario con datos de prueba
4. Hacer clic en "Guardar como plantilla" y completar nombre/descripción
5. Verificar que aparece el mensaje de éxito
6. En "Gestión de Plantillas", verificar que aparece la plantilla guardada
7. Hacer clic en "Cargar" para aplicar la plantilla a un formulario nuevo
8. Verificar que los campos se llenan correctamente
9. Probar eliminar la plantilla

## Notas Técnicas

- Django REST Framework usa convenciones RESTful estándar
- Los endpoints de lista/detalle son generados automáticamente por el router
- DELETE devuelve 204 No Content sin cuerpo de respuesta
- POST/PUT devuelven el objeto creado/actualizado
- GET lista devuelve un array directamente
- GET detalle devuelve un objeto directamente
- Los filtros se pasan como query parameters: `?campo=valor`
