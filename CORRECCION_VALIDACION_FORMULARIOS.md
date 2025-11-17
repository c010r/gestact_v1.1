# Corrección de Validación de Formularios en Tabs

## Problemas Detectados

### 1. Error de Validación HTML5
```
The invalid form control with name='nombre' is not focusable.
The invalid form control with name='numero_serie' is not focusable.
An invalid form control is not focusable.
```

### 2. Error de Favicon
```
GET http://localhost:8000/favicon.ico [HTTP/1.1 404 Not Found 16ms]
```

## Causa del Problema de Validación

Los formularios de dispositivos usan tabs (pestañas) de Bootstrap para organizar los campos. Cuando un usuario intenta enviar el formulario:

1. El navegador ejecuta la validación HTML5 nativa
2. Encuentra campos `required` (obligatorios) vacíos
3. Intenta enfocar el primer campo inválido para mostrar el mensaje de error
4. **PROBLEMA:** El campo está dentro de un tab inactivo (oculto con `display: none`)
5. HTML5 no puede enfocar elementos ocultos → Error "is not focusable"

### Escenario Típico

Usuario en el tab "Plantillas" → Hace clic en "Guardar" → Campos required en tab "Datos básicos" están ocultos → Error de validación

## Solución Implementada

### Script de Validación Inteligente

**Archivo:** `inventario/templates/inventario/base_device_form.html`

Se agregó un event listener que intercepta el submit del formulario:

```javascript
form.addEventListener('submit', function(e) {
    // Encontrar campos requeridos inválidos
    const invalidFields = form.querySelectorAll(':invalid');
    
    if (invalidFields.length > 0) {
        // Tomar el primer campo inválido
        const firstInvalid = invalidFields[0];
        
        // Encontrar el tab-pane que lo contiene
        let tabPane = firstInvalid.closest('.tab-pane');
        
        // Si el tab está oculto
        if (tabPane && !tabPane.classList.contains('show')) {
            e.preventDefault(); // Prevenir submit
            
            // Encontrar y activar el tab correcto
            const tabId = tabPane.getAttribute('id');
            const tabButton = document.querySelector(`[data-bs-target="#${tabId}"]`);
            
            if (tabButton) {
                const tab = new bootstrap.Tab(tabButton);
                tab.show(); // Mostrar tab
                
                // Enfocar el campo después del cambio
                setTimeout(() => {
                    firstInvalid.focus();
                    firstInvalid.reportValidity(); // Mostrar mensaje
                }, 150);
            }
        }
    }
});
```

### Funcionamiento

1. **Interceptar submit:** Cuando el usuario hace submit
2. **Detectar campos inválidos:** Usa selector CSS `:invalid` para encontrar campos con errores
3. **Localizar tab:** Busca el `.tab-pane` que contiene el campo inválido
4. **Verificar visibilidad:** Chequea si el tab está oculto (no tiene clase `show`)
5. **Cambiar de tab:** Usa Bootstrap Tab API para activar el tab correcto
6. **Enfocar campo:** Después de 150ms, enfoca el campo y muestra el mensaje de validación nativo
7. **Permitir validación:** El navegador puede ahora mostrar el mensaje correctamente

### Ventajas de Esta Solución

✅ **No desactiva validación HTML5:** Mantiene la validación nativa del navegador  
✅ **UX mejorada:** Lleva automáticamente al usuario al campo con error  
✅ **Sin dependencias:** Solo usa Bootstrap (ya presente) y JavaScript nativo  
✅ **Funciona con cualquier tab:** Detecta automáticamente el tab correcto  
✅ **Mensajes nativos:** Usa `reportValidity()` para mostrar mensajes estándar del navegador  

## Solución del Favicon

### Favicon SVG con Emoji

**Archivo:** `inventario/templates/inventario/base.html`

Se agregó un favicon inline usando SVG con emoji:

```html
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='0.9em' font-size='90'>💻</text></svg>">
```

### Ventajas

✅ **Sin archivos:** No requiere archivo físico favicon.ico  
✅ **Sin 404:** Elimina el error en consola  
✅ **Escalable:** SVG se adapta a cualquier tamaño  
✅ **Temático:** Emoji 💻 representa el sistema de inventario  
✅ **Compatible:** Funciona en todos los navegadores modernos  

### Alternativa (no implementada)

Si en el futuro se desea usar un favicon personalizado:

1. Crear archivo `favicon.ico` o `favicon.png`
2. Colocarlo en `sgai/static/` o `inventario/static/inventario/`
3. Actualizar la línea a:
   ```html
   <link rel="icon" href="{% static 'favicon.ico' %}">
   ```

## Resultado

### Antes
❌ Submit desde tab inactivo → Error "not focusable" → Formulario no se envía  
❌ Console muestra error 404 de favicon.ico  
❌ Usuario confundido sin saber qué campo tiene error  

### Después
✅ Submit desde tab inactivo → Cambia automáticamente al tab con error  
✅ Campo inválido se enfoca y muestra mensaje de validación  
✅ No hay errores 404 en consola  
✅ Mejor experiencia de usuario  

## Archivos Modificados

1. `inventario/templates/inventario/base_device_form.html` - Agregado script de validación
2. `inventario/templates/inventario/base.html` - Agregado favicon SVG

## Pruebas Recomendadas

### Validación de Formulario

1. Ve a `/computadoras/crear/`
2. Cambia al tab "Plantillas" o "Notas"
3. Haz clic en "Guardar" sin llenar campos obligatorios
4. **Esperado:** El formulario cambia automáticamente al tab "Datos básicos"
5. **Esperado:** El campo "Número de serie" se enfoca y muestra mensaje de validación
6. **Esperado:** No aparece error "is not focusable" en consola

### Favicon

1. Abre cualquier página del sistema
2. Revisa la pestaña del navegador
3. **Esperado:** Aparece emoji 💻 en la pestaña
4. **Esperado:** No hay error 404 en consola

## Notas Técnicas

### Selector `:invalid`
- Pseudo-clase CSS que selecciona elementos de formulario con validación fallida
- Solo funciona con validación HTML5 (required, pattern, type, etc.)
- No incluye validación personalizada de JavaScript

### `reportValidity()`
- Método DOM que dispara la validación de un campo
- Muestra el mensaje de error nativo del navegador
- Retorna `true` si el campo es válido, `false` si no

### `setTimeout(150)`
- Necesario para dar tiempo a Bootstrap de completar la animación del tab
- 150ms es suficiente para la transición `fade` de Bootstrap
- Sin esto, el `focus()` puede fallar si el elemento aún está oculto

### Bootstrap Tab API
- `new bootstrap.Tab(element)` - Crea instancia de tab
- `.show()` - Activa el tab (equivalente a hacer clic)
- Dispara eventos: `show.bs.tab`, `shown.bs.tab`

### Data URI con SVG
- Formato: `data:image/svg+xml,<svg>...</svg>`
- Permite incluir imágenes inline sin archivos externos
- Ideal para iconos simples como favicons
- Los emojis se renderizan como texto dentro del SVG
