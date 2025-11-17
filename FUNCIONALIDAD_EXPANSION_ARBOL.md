# 🌳 Funcionalidad: Expansión Automática del Árbol al Editar

## 📋 Requerimiento

> "Si el lugar tiene seleccionado un lugar en el modal me debe cargar el árbol de ese lugar"

Cuando se edita un registro que ya tiene un lugar asignado, el widget de árbol jerárquico debe:
1. **Mostrar** el lugar seleccionado en el campo
2. **Expandir** automáticamente el árbol hasta ese nodo
3. **Resaltar** visualmente el nodo seleccionado
4. **Hacer scroll** para que el nodo sea visible

---

## 🎯 Casos de Uso

### Caso 1: Crear Nueva Computadora
**Escenario:** Usuario crea una computadora nueva
- Campo "Lugar" está **vacío**
- Al abrir el widget, el árbol se muestra **colapsado**
- Usuario navega y selecciona un lugar

### Caso 2: Editar Computadora Existente
**Escenario:** Usuario edita una computadora que ya tiene lugar asignado
- Campo "Lugar" muestra: **"Hospital Regional > Cirugía > Pabellón Quirúrgico > Pabellón 1 > Quirófano > Sala 1"**
- Al abrir el widget:
  - ✅ **Árbol expandido** hasta "Sala 1"
  - ✅ **Nodo "Sala 1" resaltado** en azul
  - ✅ **Scroll automático** para mostrar "Sala 1"
  - ✅ Todos los **nodos padres expandidos**:
    - Hospital Regional ▼
      - Cirugía ▼
        - Pabellón Quirúrgico ▼
          - Pabellón 1 ▼
            - Quirófano ▼
              - **Sala 1** ← Resaltado

---

## 🔧 Implementación

### 1. JavaScript - Expansión Automática

**Archivo:** `inventario/static/inventario/js/tree-select.js`

**Función agregada en `init()`:**

```javascript
init() {
    // Construir el árbol
    this.buildTree();
    
    // Event listeners
    this.display.addEventListener('click', () => this.toggle());
    // ... otros listeners ...
    
    // Actualizar display con valor inicial
    this.updateDisplay();
    
    // ✅ NUEVO: Si hay un valor preseleccionado, expandir el árbol hasta ese nodo
    if (this.selectedValue) {
        this.expandToSelected();
    }
}
```

**Nueva función `expandToSelected()`:**

```javascript
expandToSelected() {
    const selectedNode = this.treeList.querySelector(
        `[data-id="${this.selectedValue}"]`
    );
    
    if (selectedNode) {
        // 1. Marcar como seleccionado
        selectedNode.classList.add('selected');
        
        // 2. Expandir todos los padres hasta llegar a este nodo
        this.expandParents(selectedNode);
        
        // 3. Hacer scroll para que sea visible
        setTimeout(() => {
            selectedNode.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        }, 100);
    }
}
```

**Función existente `expandParents()` (ya existía para búsqueda):**

```javascript
expandParents(node) {
    let current = node.parentElement;
    
    while (current && current !== this.treeList) {
        if (current.classList.contains('tree-children')) {
            // Mostrar la lista de hijos
            current.style.display = 'block';
            
            // Cambiar el icono del toggle a expandido
            const parentNode = current.closest('.tree-node');
            if (parentNode) {
                const toggle = parentNode.querySelector('.tree-node-toggle');
                if (toggle) {
                    toggle.textContent = '▼';
                }
            }
        }
        current = current.parentElement;
    }
}
```

---

### 2. CSS - Estilos para Nodo Seleccionado

**Archivo:** `inventario/static/inventario/css/tree-select.css`

**Estilos mejorados:**

```css
.tree-node.selected {
    background-color: #007bff;  /* Fondo azul */
    color: white;               /* Texto blanco */
    font-weight: 500;           /* Texto semi-negrita */
}

/* Invertir color del icono en nodo seleccionado */
.tree-node.selected .tree-node-icon {
    filter: brightness(0) invert(1);
}

/* Toggle en blanco cuando está seleccionado */
.tree-node.selected .tree-node-toggle {
    color: white;
}
```

---

## 🎬 Flujo de Ejecución

### Al Cargar Formulario de Edición

```
1. Django renderiza el formulario
   └─> Campo hidden: <input id="id_lugar" value="19">
   └─> Display: "Hospital Regional > ... > Sala 1"

2. JavaScript inicializa TreeSelect
   └─> constructor() lee this.input.value = "19"
   └─> Almacena en this.selectedValue = "19"

3. init() se ejecuta
   └─> buildTree() construye el árbol HTML
   └─> updateDisplay() muestra el nombre completo
   └─> expandToSelected() se ejecuta porque selectedValue existe ✅

4. expandToSelected() actúa
   └─> Busca el nodo con data-id="19"
   └─> Agrega clase 'selected' al nodo
   └─> Llama expandParents(nodo)
   
5. expandParents() recorre hacia arriba
   └─> Nivel 7 (Sala 1) - es el nodo
   └─> Nivel 6 (Quirófano) - expande .tree-children, toggle ▼
   └─> Nivel 5 (Pabellón 1) - expande .tree-children, toggle ▼
   └─> Nivel 4 (Pabellón Quirúrgico) - expande .tree-children, toggle ▼
   └─> Nivel 3 (Cirugía) - expande .tree-children, toggle ▼
   └─> Nivel 2 (Hospital Regional) - expande .tree-children, toggle ▼
   └─> Nivel 1 - es raíz, termina

6. scrollIntoView() hace scroll
   └─> El nodo "Sala 1" se muestra en la vista
   └─> Smooth scroll con animación
```

---

## 📊 Ejemplo Visual

### ANTES (Sin Expansión Automática)

```
Al abrir widget en modo edición:

┌─────────────────────────────────────┐
│ Campo: Hospital Reg... > ... > Sala1│
│                                   ▼ │
└─────────────────────────────────────┘

┌─ Dropdown ──────────────────────────┐
│ 🔍 Buscar...                        │
├─────────────────────────────────────┤
│ ▶ 📁 Hospital Regional              │ ← Todo colapsado
│ ▶ 📁 Centro de Salud Norte          │
└─────────────────────────────────────┘
```
❌ Usuario debe expandir manualmente 5 niveles para ver "Sala 1"

---

### DESPUÉS (Con Expansión Automática)

```
Al abrir widget en modo edición:

┌─────────────────────────────────────┐
│ Campo: Hospital Reg... > ... > Sala1│
│                                   ▼ │
└─────────────────────────────────────┘

┌─ Dropdown ──────────────────────────┐
│ 🔍 Buscar...                        │
├─────────────────────────────────────┤
│ ▼ 📁 Hospital Regional              │ ← Expandido
│   ▼ 🏢 Cirugía                      │ ← Expandido
│     ▼ 🏥 Pabellón Quirúrgico        │ ← Expandido
│       ▼ 📋 Pabellón 1               │ ← Expandido
│         ▼ 🔧 Quirófano              │ ← Expandido
│           🎯 Sala 1   ◄─────────────┼─ SELECCIONADO (azul)
│           📍 Sala 2                 │
│ ▶ 📁 Centro de Salud Norte          │
└─────────────────────────────────────┘
```
✅ Árbol expandido automáticamente hasta el nodo seleccionado

---

## 🧪 Casos de Prueba

### Prueba 1: Crear Nueva Computadora
```
1. Ir a: http://127.0.0.1:8000/computadoras/crear/
2. Campo "Lugar" está vacío
3. Abrir widget
4. ✅ Árbol colapsado (comportamiento normal)
5. Seleccionar "Hospital Regional > Cirugía > Pabellón Quirúrgico > Pabellón 1"
6. ✅ Se guarda correctamente
```

### Prueba 2: Editar Computadora con Lugar Asignado
```
1. Crear una computadora con lugar "Sala 1" (nivel 7)
2. Guardar
3. Ir a editar la computadora
4. ✅ Campo muestra: "Hospital Regional > ... > Sala 1"
5. Abrir widget
6. ✅ Árbol expandido hasta "Sala 1"
7. ✅ "Sala 1" resaltado en azul
8. ✅ Scroll automático muestra "Sala 1"
```

### Prueba 3: Cambiar de Lugar
```
1. Editar computadora con "Sala 1" seleccionado
2. Abrir widget (árbol expandido a "Sala 1")
3. Navegar a otro lugar: "Centro de Salud Norte > Consulta Externa"
4. Seleccionar "Medicina General"
5. ✅ Widget se cierra
6. ✅ Campo actualizado a "Centro de Salud Norte > ... > Medicina General"
7. Reabrir widget
8. ✅ Ahora expandido hasta "Medicina General"
```

### Prueba 4: Lugar de Nivel 1 (Raíz)
```
1. Editar computadora con "Hospital Regional" (nivel 1)
2. Abrir widget
3. ✅ "Hospital Regional" resaltado en azul
4. ✅ Visible en la raíz del árbol
5. ✅ Sin nodos padres que expandir
```

---

## 🎨 Estilos Visuales

### Estado Normal
```css
background: white
color: #212529
font-weight: normal
```

### Al Hover
```css
background: #f8f9fa (gris claro)
color: #212529
```

### Seleccionado
```css
background: #007bff (azul Bootstrap)
color: white
font-weight: 500 (semi-negrita)
toggle: blanco (▼ en blanco)
icono: invertido (para que sea visible en fondo azul)
```

---

## 🔄 Reutilización del Código

La función `expandParents()` se reutiliza en **dos contextos**:

### 1. Búsqueda (uso previo)
```javascript
filterTree(searchTerm) {
    // ...
    if (term && nombre.includes(term)) {
        this.expandParents(node);  // ← Expandir al buscar
    }
}
```

### 2. Valor Preseleccionado (nuevo uso)
```javascript
expandToSelected() {
    if (selectedNode) {
        this.expandParents(selectedNode);  // ← Expandir al inicializar
    }
}
```

**Ventaja:** Un solo método para dos funcionalidades distintas.

---

## 📝 Consideraciones Técnicas

### 1. **Timing del Scroll**
```javascript
setTimeout(() => {
    selectedNode.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest'
    });
}, 100);
```
- Se usa `setTimeout(100ms)` para dar tiempo al DOM de renderizar las expansiones
- `behavior: 'smooth'` para animación suave
- `block: 'nearest'` para evitar scroll innecesario si ya es visible

### 2. **Búsqueda por data-id**
```javascript
const selectedNode = this.treeList.querySelector(
    `[data-id="${this.selectedValue}"]`
);
```
- Cada nodo tiene atributo `data-id` con el ID del lugar
- Búsqueda eficiente usando querySelector

### 3. **Persistencia del Estado**
- Al seleccionar un nuevo lugar, `this.selectedValue` se actualiza
- Al reabrir el widget, `expandToSelected()` usa el nuevo valor
- No requiere recarga de página

---

## 🚀 Beneficios

### Para el Usuario
✅ **Ahorro de tiempo:** No necesita expandir manualmente 5-7 niveles  
✅ **Contexto visual:** Ve inmediatamente dónde está ubicado el lugar  
✅ **Confirmación:** El resaltado confirma qué lugar está seleccionado  
✅ **Facilita cambios:** Puede ver lugares cercanos en la jerarquía

### Para el Sistema
✅ **UX mejorada:** Comportamiento esperado en formularios de edición  
✅ **Consistencia:** Mismo comportamiento que otros selectores jerárquicos  
✅ **Accesibilidad:** Scroll automático para usuarios con pantallas pequeñas  
✅ **Código limpio:** Reutiliza función existente `expandParents()`

---

## 🎯 Estado Final

✅ **Expansión automática en modo edición**  
✅ **Nodo seleccionado resaltado en azul**  
✅ **Scroll automático al nodo**  
✅ **Iconos de toggle expandidos (▼)**  
✅ **Funciona con todos los niveles (1-7)**  
✅ **Compatible con búsqueda en tiempo real**  
✅ **No afecta modo creación (nuevo registro)**

---

**Implementado:** 12 de Octubre de 2025  
**Archivos modificados:** 2  
- `tree-select.js` - Lógica de expansión  
- `tree-select.css` - Estilos de selección  
**Líneas agregadas:** ~25 líneas de código  
**Estado:** ✅ **IMPLEMENTADO Y PROBADO**
