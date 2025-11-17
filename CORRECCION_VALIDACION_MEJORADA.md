# Corrección Mejorada de Validación de Formularios

## Problema Actualizado

Después de la primera corrección, seguían apareciendo errores:

```
The invalid form control with name='fecha_adquisicion' is not focusable.
An invalid form control is not focusable.
```

## Causa

La solución anterior intentaba detectar campos inválidos DESPUÉS de que HTML5 intentara validarlos. El problema es que HTML5 intenta validar campos ocultos antes de que nuestro código pueda intervenir.

## Nueva Solución: Validación Manual Completa

Se desactivó completamente la validación HTML5 nativa y se implementó validación manual en JavaScript.

### Cambios Implementados

**Archivo:** `inventario/templates/inventario/base_device_form.html`

#### 1. Deshabilitar Validación HTML5

```javascript
form.setAttribute('novalidate', 'novalidate');
```

Esto previene que el navegador intente validar campos ocultos.

#### 2. Validación Manual en Submit

Al enviar el formulario:

1. **Recorre todos los campos `[required]`**
2. **Valida según tipo de campo:**
   - Text/Date/Select: Verifica que no esté vacío
   - Checkbox: Verifica que esté marcado
   - Radio: Verifica que al menos uno del grupo esté seleccionado

3. **Marca campos inválidos:**
   - Agrega clase `is-invalid` (estilo Bootstrap de error)
   - Guarda el primer campo inválido encontrado

4. **Si hay errores:**
   - Previene el envío del formulario
   - Si el campo está en un tab oculto, activa ese tab
   - Enfoca el primer campo con error
   - Muestra alerta con nombre del campo

#### 3. Feedback Visual Inmediato

```javascript
// Cuando el usuario corrige un campo
form.addEventListener('input', function(e) {
    if (e.target.classList.contains('is-invalid') && e.target.value.trim() !== '') {
        e.target.classList.remove('is-invalid');
    }
});
```

La clase `is-invalid` se quita automáticamente cuando el usuario corrige el error.

## Flujo de Validación

### Escenario 1: Todos los Campos Válidos

```
Usuario → [Guardar] → Validación manual → ✓ OK → Enviar formulario → Django
```

### Escenario 2: Campo Requerido Vacío en Tab Activo

```
Usuario → [Guardar] → Validación manual → ✗ Error
                   → Campo marcado en rojo (is-invalid)
                   → Enfoca campo
                   → Alert: "Por favor complete el campo: Número de serie"
                   → No envía formulario
```

### Escenario 3: Campo Requerido Vacío en Tab Oculto

```
Usuario en tab "Plantillas" → [Guardar]
                           → Validación manual → ✗ Error en "Datos básicos"
                           → Cambia a tab "Datos básicos"
                           → Campo marcado en rojo
                           → Enfoca campo
                           → Alert: "Por favor complete el campo: Número de serie"
                           → No envía formulario
```

## Ventajas de Esta Solución

✅ **Sin errores "is not focusable"**: HTML5 nunca intenta validar campos ocultos  
✅ **Feedback visual**: Campos con error se marcan en rojo (Bootstrap `is-invalid`)  
✅ **Navegación automática**: Lleva al usuario al tab con error  
✅ **Mensajes claros**: Alerta muestra el nombre del campo faltante  
✅ **Corrección inmediata**: El error visual desaparece al corregir el campo  
✅ **Compatible con todos los tipos**: Text, Date, Select, Checkbox, Radio  

## Código Implementado

### Estructura de Validación

```javascript
// 1. Deshabilitar HTML5
form.setAttribute('novalidate', 'novalidate');

// 2. Evento submit
form.addEventListener('submit', function(e) {
    let isValid = true;
    let firstInvalidField = null;
    let firstInvalidTabPane = null;
    
    // 3. Validar cada campo required
    form.querySelectorAll('[required]').forEach(field => {
        let fieldValid = validateField(field);
        
        if (!fieldValid) {
            field.classList.add('is-invalid');
            if (!firstInvalidField) {
                firstInvalidField = field;
                firstInvalidTabPane = field.closest('.tab-pane');
            }
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    // 4. Si hay errores
    if (!isValid) {
        e.preventDefault();
        e.stopPropagation();
        
        // Cambiar de tab si es necesario
        if (firstInvalidTabPane && !firstInvalidTabPane.classList.contains('show')) {
            activateTab(firstInvalidTabPane);
        }
        
        // Enfocar y mostrar alerta
        firstInvalidField.focus();
        showAlert(firstInvalidField);
        
        return false;
    }
});
```

### Validación por Tipo de Campo

```javascript
function validateField(field) {
    if (field.type === 'checkbox') {
        return field.checked;
    } else if (field.type === 'radio') {
        const radioGroup = form.querySelectorAll(`[name="${field.name}"]`);
        return Array.from(radioGroup).some(radio => radio.checked);
    } else {
        return field.value.trim() !== '';
    }
}
```

## Estilo Visual de Errores

Bootstrap proporciona la clase `is-invalid` que:

- Pone borde rojo al campo
- Si existe `.invalid-feedback`, lo muestra en rojo debajo del campo

Ejemplo en HTML:

```html
<input type="text" class="form-control is-invalid" required>
<div class="invalid-feedback">Este campo es requerido</div>
```

## Comparación: Antes vs. Después

### Antes (HTML5 Nativo)

```
❌ HTML5 intenta validar campos ocultos
❌ Error: "is not focusable"
❌ Formulario no se envía pero usuario no sabe por qué
❌ No hay indicador visual del error
```

### Después (Validación Manual)

```
✅ JavaScript valida solo campos visibles y ocultos correctamente
✅ No hay errores "is not focusable"
✅ Usuario ve exactamente qué campo tiene error
✅ Campo marcado en rojo con clase is-invalid
✅ Navegación automática al tab correcto
✅ Alerta descriptiva con nombre del campo
```

## Casos de Prueba

### Caso 1: Campo de Texto Vacío

1. Crear computadora
2. Dejar "Número de serie" vacío
3. Clic en "Guardar"
4. **Resultado esperado:**
   - Campo se marca en rojo
   - Aparece alerta: "Por favor complete el campo: Número de serie"
   - Formulario no se envía

### Caso 2: Fecha Vacía en Tab "Compra y garantía"

1. Crear computadora
2. Ir a tab "Plantillas"
3. Dejar "Fecha de adquisición" vacía en tab "Compra y garantía"
4. Clic en "Guardar" desde tab "Plantillas"
5. **Resultado esperado:**
   - Cambia automáticamente a tab "Compra y garantía"
   - Campo "Fecha de adquisición" marcado en rojo
   - Alerta: "Por favor complete el campo: Fecha de adquisición"
   - Formulario no se envía

### Caso 3: Corrección de Error

1. Campo marcado en rojo (is-invalid)
2. Usuario ingresa datos
3. **Resultado esperado:**
   - Al escribir, el rojo desaparece inmediatamente
   - Campo vuelve a estado normal

## Archivos Modificados

- `inventario/templates/inventario/base_device_form.html`
  - Agregado: `form.setAttribute('novalidate', 'novalidate')`
  - Reemplazado: Validación con `:invalid` por validación manual completa
  - Agregado: Event listeners para `input` y `change` que quitan `is-invalid`

## Notas Técnicas

### `novalidate` Attribute

- Atributo HTML5 que deshabilita validación del navegador
- Permite implementar validación personalizada en JavaScript
- No afecta la validación del lado del servidor (Django)

### `is-invalid` Class (Bootstrap)

- Clase de utilidad de Bootstrap 5
- Estilo CSS: borde rojo, texto rojo de feedback
- Compatible con todos los controles de formulario

### `e.preventDefault()` + `e.stopPropagation()`

- `preventDefault()`: Previene el envío del formulario
- `stopPropagation()`: Previene que el evento se propague a otros handlers
- Ambos necesarios para control completo

### `setTimeout(200)`

- 200ms da tiempo a Bootstrap para completar la animación del tab
- Sin esto, el `focus()` puede fallar si el campo aún no es visible
- Mayor que los 150ms anteriores para mayor compatibilidad

## Resultado Final

✅ **Cero errores "is not focusable"** en la consola  
✅ **Validación funcional** en todos los tabs  
✅ **Feedback visual inmediato** con clase Bootstrap  
✅ **Navegación inteligente** entre tabs  
✅ **Experiencia de usuario mejorada**  

## Prueba Ahora

1. Ve a http://127.0.0.1:8000/computadoras/crear/
2. Deja campos requeridos vacíos
3. Cambia a un tab diferente (ej: "Plantillas")
4. Clic en "Guardar"
5. **Verifica:**
   - No aparecen errores en consola
   - Se activa el tab con el error
   - Campo se marca en rojo
   - Aparece alerta descriptiva
