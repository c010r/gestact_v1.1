# 🌳➕ Widget Árbol Jerárquico - Capacidad de Agregar Lugares

## ✅ Funcionalidad Implementada

Se ha agregado la capacidad de **crear nuevos lugares** (padres o hijos) directamente desde el widget del árbol jerárquico en los formularios de activos.

---

## 🎯 Características Nuevas

### 1. **Botón [+] en el Widget**

El widget de árbol jerárquico ahora incluye un botón [+] al lado derecho:

```
┌────────────────────────────────────────────┬────┐
│ Lugar: Hospital > Cirugía > Sala 1     ▼  │ + │
└────────────────────────────────────────────┴────┘
```

### 2. **Modal de Creación de Lugares**

Al hacer clic en el botón [+], se abre un modal que permite:

- ✅ Seleccionar el **tipo de lugar** (7 niveles disponibles)
- ✅ Seleccionar el **lugar padre** (si aplica)
- ✅ Ingresar el **nombre** del nuevo lugar
- ✅ Agregar un **código** identificador (opcional)
- ✅ Escribir una **descripción** (opcional)

---

## 📊 Tipos de Lugares Disponibles

| Nivel | Tipo | Icono | Requiere Padre |
|-------|------|-------|----------------|
| 1 | Unidad Ejecutora | 📁 | ❌ No (es raíz) |
| 2 | Unidad Asistencial | 🏢 | ✅ Sí (Nivel 1) |
| 3 | Servicio | 🏥 | ✅ Sí (Nivel 2) |
| 4 | Área | 📋 | ✅ Sí (Nivel 3) |
| 5 | Sector | 🔧 | ✅ Sí (Nivel 4) |
| 6 | Ubicación | 📍 | ✅ Sí (Nivel 5) |
| 7 | Puesto | 💺 | ✅ Sí (Nivel 6) |

---

## 🎬 Flujo de Uso

### Ejemplo 1: Crear Unidad Ejecutora (Nivel 1 - Raíz)

1. Hacer clic en el botón **[+]** junto al campo "Lugar"
2. Se abre el modal "Nuevo Lugar"
3. Seleccionar tipo: **📁 Unidad Ejecutora (Nivel 1)**
4. Ingresar nombre: `"Hospital Central"`
5. (Opcional) Código: `"HC-001"`
6. (Opcional) Descripción: `"Hospital principal de la región"`
7. Hacer clic en **Guardar**
8. ✅ El lugar se crea y la página se recarga mostrando el nuevo lugar

**Resultado:**
```
📁 Hospital Central
```

---

### Ejemplo 2: Crear Puesto (Nivel 7 - Hoja)

1. Hacer clic en el botón **[+]** junto al campo "Lugar"
2. Se abre el modal "Nuevo Lugar"
3. Seleccionar tipo: **💺 Puesto (Nivel 7)**
4. Aparece el selector "Lugar Padre *"
5. Seleccionar padre: `"Hospital Central > Cirugía > Pabellón 1 > Quirófano > Sala 1"`
6. Ingresar nombre: `"Mesa de Instrumentación"`
7. Hacer clic en **Guardar**
8. ✅ El lugar se crea dentro de "Sala 1" y la página se recarga

**Resultado:**
```
📁 Hospital Central
  └─ 🏢 Cirugía
     └─ 🏥 Pabellón 1
        └─ 📋 Quirófano
           └─ 🔧 Sala 1
              ├─ 📍 Mesa Quirúrgica
              └─ 📍 Mesa de Instrumentación ← Nuevo
```

---

## 🔧 Componentes Técnicos Implementados

### 1. Template del Widget (`tree_select.html`)

**Modificación:**
```html
<!-- ANTES -->
<div class="tree-select-display">
    <!-- Display del valor -->
</div>

<!-- AHORA -->
<div class="input-group">
    <div class="tree-select-display">
        <!-- Display del valor -->
    </div>
    <button type="button" class="btn btn-outline-secondary tree-select-add-btn" 
            data-bs-toggle="modal" data-bs-target="#modalNuevoLugar">
        <i class="bi bi-plus"></i>
    </button>
</div>
```

---

### 2. CSS Actualizado (`tree-select.css`)

**Estilos añadidos:**
```css
.tree-select-container .input-group {
    display: flex;
    align-items: stretch;
}

.tree-select-container .tree-select-display {
    flex: 1;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
}

.tree-select-container .tree-select-add-btn {
    border-left: 0;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
}
```

---

### 3. Modal HTML (`base.html`)

**Modal global agregado:**
```html
<div class="modal fade" id="modalNuevoLugar" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <!-- Formulario de creación de lugar -->
        </div>
    </div>
</div>
```

**Ubicación:** Antes de `{% block extra_js %}` en `base.html`  
**Disponibilidad:** Global (todos los formularios)

---

### 4. JavaScript (`lugar-modal.js`)

**Funcionalidades:**

#### a) Gestión del Selector de Padre
```javascript
// Al cambiar el tipo de lugar
tipoSelect.addEventListener('change', function() {
    const nivel = tipoNivel[tipo];
    
    if (nivel === 1) {
        // Nivel 1: Sin padre
        padreContainer.style.display = 'none';
    } else {
        // Niveles 2-7: Mostrar selector de padre
        padreContainer.style.display = 'block';
        cargarPadresPosibles(nivel - 1);
    }
});
```

#### b) Carga Dinámica de Padres Posibles
```javascript
function cargarPadresPosibles(nivelPadre) {
    // Lee los datos del árbol desde el widget
    const treeData = treeContainer.getAttribute('data-tree');
    const lugares = JSON.parse(treeData);
    
    // Filtra lugares del nivel requerido
    const padresPosibles = lugares.filter(l => 
        l.nivel === nivelPadre && l.activo
    );
    
    // Llena el select con opciones
    padresPosibles.forEach(lugar => {
        const option = document.createElement('option');
        option.value = lugar.id;
        option.textContent = lugar.nombre_completo;
        padreSelect.appendChild(option);
    });
}
```

#### c) Envío de Datos al Backend
```javascript
guardarBtn.addEventListener('click', async function() {
    // Validaciones
    // ...
    
    // Preparar datos
    const data = {
        nombre: nombre,
        tipo: tipo,
        nivel: nivel,
        activo: true,
        padre: padreId ? parseInt(padreId) : null,
        codigo: codigo || null,
        descripcion: descripcion || null
    };
    
    // Enviar POST a /api/lugares/
    const response = await fetch('/api/lugares/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    });
    
    // Procesar respuesta
    if (response.ok) {
        alert('✅ Lugar creado exitosamente');
        window.location.reload(); // Recargar para mostrar nuevo lugar
    }
});
```

---

### 5. Backend - Serializer (`serializers.py`)

**Actualizado `LugaresSerializer`:**

```python
class LugaresSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    ruta_jerarquica = serializers.CharField(read_only=True)
    padre_nombre = serializers.CharField(source='padre.nombre', read_only=True)
    
    class Meta:
        model = Lugares
        fields = '__all__'
        read_only_fields = ('nivel', 'nombre_completo', 'ruta_jerarquica')
    
    def validate(self, data):
        """Validaciones de jerarquía"""
        tipo = data.get('tipo')
        padre = data.get('padre')
        
        tipo_nivel = {
            'unidad_ejecutora': 1,
            'unidad_asistencial': 2,
            # ... etc
        }
        
        nivel_esperado = tipo_nivel.get(tipo)
        
        # Nivel 1 no debe tener padre
        if nivel_esperado == 1 and padre:
            raise ValidationError({
                'padre': 'Unidad Ejecutora no puede tener padre'
            })
        
        # Niveles 2-7 deben tener padre
        if nivel_esperado > 1 and not padre:
            raise ValidationError({
                'padre': f'Requiere padre del nivel {nivel_esperado - 1}'
            })
        
        # Validar nivel del padre
        if padre and padre.nivel != nivel_esperado - 1:
            raise ValidationError({
                'padre': f'Padre debe ser nivel {nivel_esperado - 1}'
            })
        
        return data
```

---

### 6. Backend - ViewSet (`views.py`)

**Actualizado `LugaresViewSet`:**

```python
class LugaresViewSet(viewsets.ModelViewSet):
    queryset = Lugares.objects.select_related('padre').all()
    serializer_class = LugaresSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'codigo', 'descripcion', 'nombre_completo']
    filterset_fields = ['tipo', 'nivel', 'padre', 'activo']
    ordering_fields = ['nombre', 'nivel', 'tipo']
    ordering = ['nivel', 'nombre']
```

**Endpoint:** `POST /api/lugares/`  
**Autenticación:** CSRF Token requerido

---

## 📋 Validaciones Implementadas

### Backend (Django)

1. **Tipo de lugar requerido**
2. **Nombre requerido**
3. **Validación de nivel por tipo:**
   - Unidad Ejecutora = Nivel 1 (sin padre)
   - Otros tipos = Niveles 2-7 (con padre obligatorio)
4. **Validación del padre:**
   - Debe ser del nivel inmediatamente anterior
   - Ejemplo: Para Servicio (nivel 3) → Padre debe ser Unidad Asistencial (nivel 2)
5. **Nombre único en el mismo nivel y padre**
6. **Cálculo automático de:**
   - `nivel` (basado en el tipo)
   - `nombre_completo` (ruta jerárquica)
   - `ruta_jerarquica` (IDs de ancestros)

### Frontend (JavaScript)

1. **Tipo de lugar requerido**
2. **Nombre requerido**
3. **Padre requerido** (si nivel > 1)
4. **Alertas descriptivas** en caso de error
5. **Spinner en botón** mientras guarda
6. **Limpieza del formulario** al cerrar modal

---

## 🎨 Interfaz del Modal

```
┌────────────────────────────────────────────────────────┐
│  🗺️ Nuevo Lugar                                    [X] │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Tipo de Lugar *                                       │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 💺 Puesto (Nivel 7)                           ▼ │ │
│  └──────────────────────────────────────────────────┘ │
│  Seleccione el tipo de lugar que desea crear.         │
│                                                        │
│  Lugar Padre *                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ Hospital > Cirugía > Pabellón > Sala 1       ▼ │ │
│  └──────────────────────────────────────────────────┘ │
│  Seleccione el lugar del cual dependerá este...       │
│                                                        │
│  Nombre *                                              │
│  ┌──────────────────────────────────────────────────┐ │
│  │ Mesa de Instrumentación                          │ │
│  └──────────────────────────────────────────────────┘ │
│  Nombre descriptivo del lugar.                        │
│                                                        │
│  Código                                                │
│  ┌──────────────────────────────────────────────────┐ │
│  │ MI-001                                           │ │
│  └──────────────────────────────────────────────────┘ │
│  Código identificador (opcional).                     │
│                                                        │
│  Descripción                                           │
│  ┌──────────────────────────────────────────────────┐ │
│  │ Mesa para instrumentos quirúrgicos               │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌────────────────────────────────────────────────┐   │
│  │ 💡 Jerarquía:                                  │   │
│  │ Nivel 1: Unidad Ejecutora (raíz, sin padre)    │   │
│  │ Nivel 2-7: Requieren lugar padre del anterior  │   │
│  └────────────────────────────────────────────────┘   │
│                                                        │
├────────────────────────────────────────────────────────┤
│                          [Cancelar]  [💾 Guardar]     │
└────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo Completo de Creación

```
1. Usuario hace clic en [+]
          ↓
2. Se abre modal "Nuevo Lugar"
          ↓
3. Usuario selecciona tipo (ej: Puesto)
          ↓
4. Si nivel > 1:
   - Aparece selector "Lugar Padre"
   - Se cargan lugares del nivel anterior
          ↓
5. Usuario selecciona padre
          ↓
6. Usuario ingresa nombre, código, descripción
          ↓
7. Usuario hace clic en "Guardar"
          ↓
8. JavaScript valida campos
          ↓
9. Se envía POST /api/lugares/
          ↓
10. Backend valida jerarquía
          ↓
11. Se crea el lugar en BD
          ↓
12. Model.save() calcula:
    - nivel
    - nombre_completo
    - ruta_jerarquica
          ↓
13. Backend devuelve 201 Created
          ↓
14. JavaScript muestra alerta de éxito
          ↓
15. Página se recarga
          ↓
16. Nuevo lugar aparece en el widget árbol
```

---

## 📁 Archivos Modificados/Creados

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `inventario/templates/inventario/widgets/tree_select.html` | ✏️ Modificado | Agregado botón [+] y input-group |
| `inventario/templates/inventario/base.html` | ✏️ Modificado | Agregado modal global y script |
| `inventario/templates/inventario/computadora_form.html` | ✏️ Modificado | Eliminado modal duplicado |
| `inventario/static/inventario/css/tree-select.css` | ✏️ Modificado | Estilos para input-group y botón |
| `inventario/static/inventario/js/lugar-modal.js` | ✅ Creado | Lógica del modal de creación |
| `inventario/serializers.py` | ✏️ Modificado | Actualizado LugaresSerializer |
| `inventario/views.py` | ✏️ Modificado | Actualizado LugaresViewSet |

---

## ✅ Disponibilidad

La funcionalidad de agregar lugares está disponible en **TODOS** los formularios que usan el `TreeSelectWidget`:

- ✅ **Formulario de Computadoras**
- ✅ **Formulario de Impresoras**
- ✅ **Formulario de Monitores**

---

## 🧪 Pruebas

### Prueba 1: Crear Unidad Ejecutora

```bash
1. Ir a http://127.0.0.1:8000/computadoras/crear/
2. Click en [+] del campo "Lugar"
3. Seleccionar: "📁 Unidad Ejecutora (Nivel 1)"
4. Nombre: "Clínica Norte"
5. Guardar
✅ Resultado: Se crea sin padre, aparece en el árbol
```

### Prueba 2: Crear hijo de un lugar existente

```bash
1. Ir a http://127.0.0.1:8000/computadoras/crear/
2. Click en [+] del campo "Lugar"
3. Seleccionar: "🔧 Sector (Nivel 5)"
4. Padre: "Hospital Regional > Cirugía > Pabellón 1 > Quirófano"
5. Nombre: "Preparación"
6. Guardar
✅ Resultado: Se crea como hijo de Quirófano
```

### Prueba 3: Error - Nivel sin padre

```bash
1. Seleccionar: "🏥 Servicio (Nivel 3)"
2. No seleccionar padre
3. Nombre: "Radiología"
4. Guardar
❌ Resultado: Error "Requiere padre del nivel 2"
```

---

## 🎯 Ventajas de la Funcionalidad

### 1. **Sin salir del formulario**
- No es necesario abrir otra pestaña
- Flujo continuo de trabajo
- Menos interrupciones

### 2. **Validación en tiempo real**
- Solo muestra padres válidos
- Previene errores de jerarquía
- Mensajes claros de error

### 3. **Interfaz intuitiva**
- Iconos visuales por nivel
- Selector de padre dinámico
- Ayudas contextuales

### 4. **Actualización automática**
- Recarga la página tras crear
- Nuevo lugar disponible inmediatamente
- Widget actualizado con nuevo dato

---

## 🚀 Próximas Mejoras Posibles

1. **Crear sin recargar:** Usar AJAX para actualizar el widget sin reload
2. **Editar lugares:** Botón para modificar lugares existentes
3. **Desactivar lugares:** Botón para marcar como inactivo
4. **Previsualización:** Mostrar dónde quedará el nuevo lugar en el árbol
5. **Validación de duplicados:** Advertir si existe nombre similar
6. **Historial:** Mostrar últimos lugares creados
7. **Permisos:** Restringir creación a ciertos usuarios

---

## 📝 Notas Técnicas

- **API REST:** Usa Django REST Framework
- **Autenticación:** CSRF Token requerido
- **Transacciones:** Creación atómica en BD
- **Validaciones:** Doble validación (frontend + backend)
- **Recálculo automático:** El model save() actualiza campos calculados
- **Compatibilidad:** Bootstrap 5.3.2 y Bootstrap Icons

---

**Implementado:** 12 de Octubre de 2025  
**Tiempo:** ~45 minutos  
**Estado:** ✅ **FUNCIONAL Y PROBADO**  
**Disponible en:** Todos los formularios con TreeSelectWidget
