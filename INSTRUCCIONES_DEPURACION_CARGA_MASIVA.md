# Instrucciones para Ver el Botón "Carga Masiva"

## Problema
No aparece el botón "Carga Masiva" al cargar plantillas.

## Solución: Limpiar Caché del Navegador

El navegador está usando una versión antigua del JavaScript. Necesitas forzar la recarga:

### Opción 1: Recarga Forzada (RECOMENDADO)

1. **En la página del formulario**, presiona:
   - **Windows/Linux:** `Ctrl + Shift + R`
   - **Mac:** `Cmd + Shift + R`

2. Esto limpiará la caché y recargará todos los archivos

### Opción 2: Limpiar Caché Completa

**Google Chrome / Edge:**
1. Presiona `Ctrl + Shift + Delete` (o `Cmd + Shift + Delete` en Mac)
2. Selecciona "Imágenes y archivos en caché"
3. Clic en "Borrar datos"
4. Recarga la página

**Firefox:**
1. Presiona `Ctrl + Shift + Delete`
2. Selecciona "Caché"
3. Clic en "Limpiar ahora"
4. Recarga la página

## Verificación

Después de limpiar caché:

1. Ve a http://127.0.0.1:8000/computadoras/crear/
2. En la barra lateral derecha, clic en "**Cargar Plantilla**"
3. Deberías ver **DOS botones** en cada plantilla:
   - `[Aplicar]` (azul)
   - `[Carga Masiva]` (verde) ← NUEVO

## Verificar con Consola del Navegador

Si sigues sin ver el botón:

1. **Abre la consola del navegador:**
   - Windows/Linux: `F12` o `Ctrl + Shift + I`
   - Mac: `Cmd + Option + I`

2. Ve a la pestaña "**Console**"

3. Haz clic en "**Cargar Plantilla**"

4. **Busca estos mensajes:**
   ```
   Respuesta del servidor (lista): [...]
   ```

5. **Verifica el HTML generado:**
   - Ve a la pestaña "**Elements**" (o "**Inspector**")
   - Busca: `btn-success` con texto "Carga Masiva"
   - Si no aparece, el JavaScript no se actualizó

## Si Aún No Funciona

### Verificar que el Archivo se Actualizó

1. Abre en el navegador:
   ```
   http://127.0.0.1:8000/static/inventario/js/plantillas.js
   ```

2. Busca (Ctrl+F) la palabra: `mostrarCargaMasiva`

3. **Deberías ver:**
   ```javascript
   mostrarCargaMasiva(plantillaId, nombrePlantilla) {
       console.log('mostrarCargaMasiva llamado:', plantillaId, nombrePlantilla);
       const modal = new bootstrap.Modal(document.getElementById('modalCargaMasiva'));
       ...
   }
   ```

4. **Si NO lo ves**, el problema es que el navegador no está cargando la última versión

### Solución Drástica: Modo Incógnito

1. **Abre una ventana de incógnito/privada:**
   - Chrome/Edge: `Ctrl + Shift + N`
   - Firefox: `Ctrl + Shift + P`

2. Ve a: http://127.0.0.1:8000/computadoras/crear/

3. En modo incógnito NO hay caché, por lo que cargará la versión actual

## Cómo Debería Verse

### Modal "Cargar Plantilla"

```
┌────────────────────────────────────────────────┐
│ Plantilla 1: Computadora HP Estándar          │
│ Configuración base para oficinas              │
│ [Aplicar] [Carga Masiva]                      │
└────────────────────────────────────────────────┘
```

### Modal "Carga Masiva" (al hacer clic)

```
┌──────────────────────────────────────────────────┐
│ Carga Masiva desde Plantilla                  × │
├──────────────────────────────────────────────────┤
│ ℹ️ Plantilla: Computadora HP Estándar           │
│                                                  │
│ Números de Serie                                 │
│ ┌────────────────────────────────────────────┐  │
│ │ Ingrese un número de serie por línea:      │  │
│ │ ABC123                                      │  │
│ │ DEF456                                      │  │
│ │ GHI789                                      │  │
│ │ ...                                         │  │
│ └────────────────────────────────────────────┘  │
│ 💡 Se creará un dispositivo por cada línea     │
│                                                  │
├──────────────────────────────────────────────────┤
│ [Cerrar]              [Procesar Carga Masiva]   │
└──────────────────────────────────────────────────┘
```

## Comandos de Depuración en Consola

Si quieres verificar manualmente:

```javascript
// Verificar que PlantillaManager existe
console.log(window.plantillaManager);

// Verificar que la función existe
console.log(typeof window.plantillaManager.mostrarCargaMasiva);
// Debería mostrar: "function"

// Probar manualmente (cambia 1 por ID de plantilla real)
window.plantillaManager.mostrarCargaMasiva(1, 'Plantilla de Prueba');
// Debería abrir el modal
```

## Resumen de Pasos

1. ✅ **Ctrl + Shift + R** para limpiar caché
2. ✅ Ir a `/computadoras/crear/`
3. ✅ Clic en "Cargar Plantilla"
4. ✅ Buscar botón verde "Carga Masiva"
5. ✅ Si no aparece: Modo incógnito
6. ✅ Si sigue sin aparecer: Revisar consola de errores

## Contacto de Errores

Si después de estos pasos sigue sin funcionar, revisa la consola del navegador y envía:
- Capturas de pantalla de la consola
- Mensajes de error (si los hay)
- Versión del navegador

