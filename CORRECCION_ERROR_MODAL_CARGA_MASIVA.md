# Corrección de Error en Modal de Carga Masiva

## Error Original

```
Uncaught TypeError: can't access property "textContent", 
document.getElementById(...) is null
    mostrarCargaMasiva http://localhost:8000/static/inventario/js/plantillas.js:443
```

## Causa

La función `mostrarCargaMasiva()` intentaba acceder a elementos del DOM (como `nombrePlantillaCargaMasiva`) antes de verificar si existían. Esto causaba un error si:

1. El modal no se había cargado todavía
2. El navegador tenía JavaScript en caché
3. Hubo error al cargar el template

## Solución Implementada

### 1. Verificación de Existencia del Modal

**Antes:**
```javascript
mostrarCargaMasiva(plantillaId, nombrePlantilla) {
    const modal = new bootstrap.Modal(document.getElementById('modalCargaMasiva'));
    document.getElementById('nombrePlantillaCargaMasiva').textContent = nombrePlantilla;
    // ...
}
```

**Después:**
```javascript
mostrarCargaMasiva(plantillaId, nombrePlantilla) {
    // Verificar que el modal existe
    const modalElement = document.getElementById('modalCargaMasiva');
    if (!modalElement) {
        console.error('Modal modalCargaMasiva no encontrado en el DOM');
        alert('Error: No se pudo abrir el modal de carga masiva');
        return;
    }
    
    // Verificar cada elemento antes de usarlo
    const nombreSpan = document.getElementById('nombrePlantillaCargaMasiva');
    if (nombreSpan) nombreSpan.textContent = nombrePlantilla;
    // ...
}
```

### 2. Cerrar Modal Anterior

Se agregó código para cerrar el modal de "Cargar Plantilla" antes de abrir el de "Carga Masiva":

```javascript
// Cerrar el modal de cargar plantilla si está abierto
const modalCargar = document.getElementById('modalCargarPlantilla');
if (modalCargar) {
    const modalCargarInstance = bootstrap.Modal.getInstance(modalCargar);
    if (modalCargarInstance) {
        modalCargarInstance.hide();
    }
}
```

**Razón:** Evitar tener dos modales abiertos simultáneamente.

### 3. Verificaciones Defensivas

Se agregó verificación para cada elemento del DOM:

```javascript
const nombreSpan = document.getElementById('nombrePlantillaCargaMasiva');
const plantillaInput = document.getElementById('plantillaIdCargaMasiva');
const numerosSerie = document.getElementById('numerosSerieCargaMasiva');
const resultado = document.getElementById('resultadoCargaMasiva');

if (nombreSpan) nombreSpan.textContent = nombrePlantilla;
if (plantillaInput) plantillaInput.value = plantillaId;
if (numerosSerie) numerosSerie.value = '';
if (resultado) resultado.innerHTML = '';
```

**Ventaja:** Si algún elemento falta, el código continúa funcionando.

## Flujo de Datos en Carga Masiva

### Campos Generados Automáticamente (Backend)

Estos campos **NO** se envían desde el frontend, se generan en Django:

1. **`nombre`**: Generado como `Modelo/Número_serie`
   - Ejemplo: "HP ProDesk G6/ABC123"

2. **`numero_inventario`**: Generado como `UE/Modelo/Número_serie`
   - Ejemplo: "001/HP ProDesk G6/ABC123"

### Campos desde la Plantilla

Estos campos se copian de la plantilla seleccionada:

**Comunes:**
- `estado` - Estado del dispositivo
- `lugar` - Ubicación física
- `fabricante` - Marca del fabricante
- `modelo` - Modelo del dispositivo
- `proveedor` - Proveedor de compra
- `tipo_garantia` - Tipo de garantía
- `anos_garantia` - Duración de garantía
- `valor_adquisicion` - Precio de compra
- `moneda` - Moneda (UYU/USD/EUR)
- `comentarios` - Observaciones

**Específicos por Tipo:**

**Computadoras:**
- `tipo_computadora` - Desktop/Laptop/Server
- `direccion_ip` - IP de red (opcional)
- `direccion_mac` - MAC address (opcional)

**Impresoras:**
- `tipo_impresora` - Láser/Inyección/etc.

**Monitores:**
- `tipo_monitor` - LED/LCD/OLED
- `tamano_pantalla` - Pulgadas
- `resolucion` - 1920x1080, etc.

**Periféricos:**
- `tipo_periferico` - Teclado/Mouse/etc.

### Campo Ingresado por Usuario

- **`numero_serie`**: Único para cada dispositivo, ingresado uno por línea

### Ejemplo de Request

```json
{
  "numero_serie": "ABC123",
  "estado": 5,
  "lugar": 12,
  "fabricante": 3,
  "modelo": 45,
  "proveedor": 8,
  "tipo_garantia": 2,
  "anos_garantia": 3,
  "valor_adquisicion": "1500.00",
  "moneda": "USD",
  "comentarios": "Plantilla oficina estándar",
  "tipo_computadora": 1
}
```

**Nota:** No incluye `nombre` ni `numero_inventario`.

### Ejemplo de Response

```json
{
  "id": 157,
  "nombre": "HP ProDesk G6/ABC123",
  "numero_inventario": "001/HP ProDesk G6/ABC123",
  "numero_serie": "ABC123",
  "estado": 5,
  "lugar": 12,
  "fabricante": 3,
  "modelo": 45,
  ...
}
```

**Nota:** Incluye `nombre` y `numero_inventario` generados por Django.

## Validación de Campos Obligatorios

### En la Plantilla

Antes de poder usar una plantilla para carga masiva, debe tener configurados estos campos obligatorios:

✅ **Requeridos:**
- Estado
- Lugar
- Fabricante
- Modelo
- Tipo específico (tipo_computadora, tipo_impresora, etc.)

⚠️ **Opcionales:**
- Proveedor
- Tipo de garantía
- Años de garantía
- Valor de adquisición
- Moneda
- Comentarios
- Campos técnicos (IP, MAC, resolución, etc.)

### Durante la Carga

Si la plantilla está incompleta:

```javascript
// Django devuelve error 400
{
  "estado": ["Este campo es requerido."],
  "fabricante": ["Este campo es requerido."]
}

// JavaScript lo captura y muestra en la tabla
resultados.push({ 
  serie: "ABC123", 
  exito: false, 
  error: "estado: Este campo es requerido."
});
```

## Mejoras Implementadas

### 1. Manejo de Errores Robusto

```javascript
try {
    const response = await fetch(`/api/${tipoDispositivo}s/`, {...});
    
    if (response.ok) {
        const dispositivo = await response.json();
        resultados.push({ serie, exito: true, id: dispositivo.id, nombre: dispositivo.nombre });
    } else {
        const error = await response.json();
        resultados.push({ serie, exito: false, error: JSON.stringify(error) });
    }
} catch (error) {
    resultados.push({ serie, exito: false, error: error.message });
}
```

### 2. Feedback en Tiempo Real

```javascript
// Actualizar progreso
resultadoDiv.innerHTML = `
    <div class="alert alert-info">
        <i class="fas fa-spinner fa-spin me-2"></i>
        Procesando ${i + 1} de ${numerosSerie.length}: ${numeroSerie}
    </div>
`;
```

### 3. Tabla de Resultados Detallada

```javascript
// Resumen
<div class="alert alert-success">
    <i class="fas fa-check-circle"></i> 15 dispositivo(s) creado(s)
    <i class="fas fa-times-circle"></i> 2 error(es)
</div>

// Detalle por dispositivo
<table>
    <tr class="table-success">
        <td>ABC123</td>
        <td>✓ Creado</td>
        <td><a href="/computadoras/157/">HP ProDesk G6/ABC123</a></td>
    </tr>
    <tr class="table-danger">
        <td>DEF456</td>
        <td>✗ Error</td>
        <td>numero_serie: Ya existe un dispositivo con este número</td>
    </tr>
</table>
```

## Archivos Modificados

**inventario/static/inventario/js/plantillas.js**
- Función `mostrarCargaMasiva()`: Agregadas verificaciones de seguridad
- Función `crearDispositivosMasivos()`: Ya existente, sin cambios
- Manejo de errores mejorado

## Pruebas Recomendadas

### Test 1: Carga Exitosa

1. Crear plantilla con todos los campos obligatorios
2. Clic "Carga Masiva"
3. Ingresar 3 números de serie válidos
4. **Esperado:**
   - Modal se abre correctamente
   - Procesamiento exitoso
   - 3 dispositivos creados
   - Enlaces funcionan

### Test 2: Número de Serie Duplicado

1. Carga masiva con número de serie que ya existe
2. **Esperado:**
   - Error mostrado en tabla
   - Mensaje: "numero_serie: Ya existe..."
   - Otros dispositivos se crean correctamente

### Test 3: Plantilla Incompleta

1. Crear plantilla sin campos obligatorios (ej: sin estado)
2. Intentar carga masiva
3. **Esperado:**
   - Error mostrado en tabla
   - Mensaje: "estado: Este campo es requerido"
   - No se crea ningún dispositivo

### Test 4: Modal No Existe (Edge Case)

Si por alguna razón el modal no está en el DOM:
- **Esperado:**
  - Console log: "Modal modalCargaMasiva no encontrado"
  - Alert al usuario
  - No se crashea la aplicación

## Solución de Problemas

### Error: "Modal no encontrado"

**Solución:** Limpiar caché del navegador
```
Ctrl + Shift + R (Windows/Linux)
Cmd + Shift + R (Mac)
```

### Error: "Campo requerido"

**Solución:** Editar la plantilla y completar campos faltantes

### Error: "Número de serie ya existe"

**Solución:** Ese número ya está en la base de datos, usar otro

## Resumen

✅ **Verificaciones de seguridad** agregadas  
✅ **Manejo robusto de errores** implementado  
✅ **Cierre de modal anterior** para evitar conflictos  
✅ **Feedback detallado** en tabla de resultados  
✅ **Campos generados automáticamente** (nombre, número_inventario)  
✅ **Validación de plantillas** incompletas  

