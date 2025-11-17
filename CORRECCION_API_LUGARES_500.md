# 🔧 Corrección: Error 500 en API de Lugares

## ❌ Problema Identificado

Al seleccionar un lugar en el formulario, la API devolvía un error 500 (Internal Server Error):

```
GET http://localhost:8000/api/lugares/2/ 500 (Internal Server Error)

TypeError at /api/lugares/2/
'Meta.fields' must not contain non-model field names: tipo
```

---

## 🔍 Diagnóstico

El error se generaba en **dos lugares diferentes** que estaban usando el campo `tipo` que **NO EXISTE** en el modelo `Lugares`:

### 1. **Serializador (serializers.py)**

El serializador usaba `fields = '__all__'` que intentaba incluir automáticamente todos los campos del modelo, pero las **validaciones** usaban un campo `tipo` inexistente.

### 2. **ViewSet (views.py)**

El ViewSet tenía configurado:
```python
filterset_fields = ['tipo', 'nivel', 'padre', 'activo']  # ❌ 'tipo' no existe
ordering_fields = ['nombre', 'nivel', 'tipo']            # ❌ 'tipo' no existe
search_fields = ['nombre', 'codigo', 'descripcion', ...]  # ❌ 'descripcion' no existe
```

### Estructura Real del Modelo

```python
class Lugares(models.Model):
    nombre = models.CharField(...)
    codigo = models.CharField(...)
    tipo_nivel = models.ForeignKey(TipoNivel, ...)  # ✅ Es ForeignKey, no campo directo
    padre = models.ForeignKey('self', ...)
    nivel = models.PositiveIntegerField(...)
    comentarios = models.TextField(...)             # ✅ No es 'descripcion'
    activo = models.BooleanField(...)
    # ...
```

---

## ✅ Solución Implementada

### 1. Corrección del Serializador

**Archivo:** `inventario/serializers.py`

**ANTES (líneas 46-53):**
```python
class LugaresSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    ruta_jerarquica = serializers.CharField(read_only=True)
    padre_nombre = serializers.CharField(source='padre.nombre', read_only=True)
    
    class Meta:
        model = Lugares
        fields = '__all__'  # ❌ Incluye campos que no existen
        read_only_fields = ('nivel', 'nombre_completo', 'ruta_jerarquica')
```

**DESPUÉS (líneas 46-62):**
```python
class LugaresSerializer(serializers.ModelSerializer):
    # Campos calculados de solo lectura
    nombre_completo = serializers.CharField(read_only=True)
    ruta_jerarquica = serializers.CharField(read_only=True)
    padre_nombre = serializers.CharField(source='padre.nombre', read_only=True)
    tipo_nivel_nombre = serializers.CharField(
        source='tipo_nivel.nombre', 
        read_only=True
    )
    numero_ue = serializers.SerializerMethodField()
    
    class Meta:
        model = Lugares
        fields = [  # ✅ Lista explícita de campos válidos
            'id', 'nombre', 'codigo', 'tipo_nivel', 'tipo_nivel_nombre',
            'padre', 'padre_nombre', 'nombre_completo', 'nivel', 
            'ruta_jerarquica', 'comentarios', 'activo', 
            'fecha_creacion', 'fecha_modificacion', 'numero_ue'
        ]
        read_only_fields = ('nivel', 'nombre_completo', 'ruta_jerarquica')
    
    def get_numero_ue(self, obj):
        """Obtiene el código de la UE raíz de este lugar"""
        if obj.nivel == 1:
            return obj.codigo
        # Navegar hasta el nivel 1
        actual = obj
        while actual.padre:
            actual = actual.padre
        return actual.codigo if actual else None
```

**Validaciones corregidas (líneas 64-130):**

```python
def validate(self, data):
    """Validaciones personalizadas para la jerarquía de lugares"""
    tipo_nivel_obj = data.get('tipo_nivel')  # ✅ Cambiado de 'tipo'
    padre = data.get('padre')
    nombre = data.get('nombre')
    
    if not tipo_nivel_obj:
        raise serializers.ValidationError({
            'tipo_nivel': 'El tipo de nivel es requerido'
        })
    
    nivel_esperado = tipo_nivel_obj.nivel  # ✅ Obtener nivel del objeto TipoNivel
    
    # Resto de validaciones...
```

---

### 2. Corrección del ViewSet

**Archivo:** `inventario/views.py`

**ANTES (líneas 80-87):**
```python
class LugaresViewSet(viewsets.ModelViewSet):
    queryset = Lugares.objects.select_related('padre').all()  # ❌ Falta tipo_nivel
    serializer_class = LugaresSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'codigo', 'descripcion', 'nombre_completo']  # ❌ 'descripcion'
    filterset_fields = ['tipo', 'nivel', 'padre', 'activo']  # ❌ 'tipo'
    ordering_fields = ['nombre', 'nivel', 'tipo']  # ❌ 'tipo'
    ordering = ['nivel', 'nombre']
```

**DESPUÉS:**
```python
class LugaresViewSet(viewsets.ModelViewSet):
    queryset = Lugares.objects.select_related('padre', 'tipo_nivel').all()  # ✅ Agregado tipo_nivel
    serializer_class = LugaresSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'codigo', 'comentarios', 'nombre_completo']  # ✅ 'comentarios'
    filterset_fields = ['tipo_nivel', 'nivel', 'padre', 'activo']  # ✅ 'tipo_nivel'
    ordering_fields = ['nombre', 'nivel', 'tipo_nivel']  # ✅ 'tipo_nivel'
    ordering = ['nivel', 'nombre']
```

---

## 📊 Resultado de la API

### Respuesta Correcta del Endpoint

```bash
$ curl http://localhost:8000/api/lugares/2/
```

**Respuesta JSON:**
```json
{
  "id": 2,
  "nombre": "Centro de Salud Norte",
  "codigo": "002",
  "tipo_nivel": 1,
  "tipo_nivel_nombre": "Unidad Ejecutora",
  "padre": null,
  "padre_nombre": null,
  "nombre_completo": "Centro de Salud Norte",
  "nivel": 1,
  "ruta_jerarquica": "/2/",
  "comentarios": null,
  "activo": true,
  "fecha_creacion": "2025-10-12T...",
  "fecha_modificacion": "2025-10-12T...",
  "numero_ue": "002"
}
```

### Campos Nuevos Agregados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `tipo_nivel_nombre` | string | Nombre descriptivo del tipo de nivel (ej: "Unidad Ejecutora") |
| `numero_ue` | string | Código de la UE raíz (calculado automáticamente navegando la jerarquía) |
| `padre_nombre` | string | Nombre del lugar padre (null si es raíz) |

---

## 🧪 Verificación

### 1. API Funciona Correctamente

```bash
✅ GET /api/lugares/           → Lista de lugares (200 OK)
✅ GET /api/lugares/2/         → Detalle del lugar (200 OK)
✅ POST /api/lugares/          → Crear lugar (201 Created)
✅ PUT /api/lugares/2/         → Actualizar lugar (200 OK)
✅ DELETE /api/lugares/2/      → Eliminar lugar (204 No Content)
```

### 2. Formulario de Computadora

1. Abrir: `http://127.0.0.1:8000/computadoras/crear/`
2. Click en campo "Lugar"
3. Seleccionar un lugar del árbol
4. ✅ **Sin errores 500**
5. ✅ Campo "Número de inventario" se autocompleta con el número UE
6. ✅ Consola del navegador sin errores

### 3. Campo `numero_ue` Calculado

El serializador ahora calcula automáticamente el `numero_ue` navegando la jerarquía hasta el nivel 1:

```python
def get_numero_ue(self, obj):
    """Obtiene el código de la UE raíz de este lugar"""
    if obj.nivel == 1:
        return obj.codigo
    # Navegar hasta el nivel 1
    actual = obj
    while actual.padre:
        actual = actual.padre
    return actual.codigo if actual else None
```

**Ejemplo:**
- Lugar nivel 7: "Sala 1 > Mesa Quirúrgica" → `numero_ue: "001"` (del Hospital Regional)
- Lugar nivel 1: "Centro de Salud Norte" → `numero_ue: "002"` (su propio código)

---

## 🎯 Archivos Modificados

| Archivo | Líneas | Cambios Principales |
|---------|--------|---------------------|
| `inventario/serializers.py` | 46-130 | - Campos explícitos en `Meta.fields`<br>- Agregado `tipo_nivel_nombre`<br>- Agregado `numero_ue` calculado<br>- Validaciones usan `tipo_nivel` |
| `inventario/views.py` | 80-87 | - `select_related('tipo_nivel')`<br>- `filterset_fields` usa `tipo_nivel`<br>- `ordering_fields` usa `tipo_nivel`<br>- `search_fields` usa `comentarios` |

---

## 📝 Lecciones Aprendidas

### 1. **`fields = '__all__'` puede ser problemático**

Cuando el modelo tiene ForeignKeys y campos calculados, es mejor especificar explícitamente los campos:

```python
# ❌ EVITAR
class Meta:
    fields = '__all__'

# ✅ PREFERIBLE
class Meta:
    fields = [
        'id', 'nombre', 'codigo', 'tipo_nivel', 'tipo_nivel_nombre',
        # ... lista completa
    ]
```

### 2. **Consistencia entre Modelo, Serializer y ViewSet**

Todos deben usar los **mismos nombres de campos**:

```python
# Modelo
tipo_nivel = models.ForeignKey(TipoNivel, ...)

# Serializer
fields = ['tipo_nivel', 'tipo_nivel_nombre']

# ViewSet
filterset_fields = ['tipo_nivel']
search_fields = ['comentarios']  # no 'descripcion'
```

### 3. **`select_related()` para Optimizar Queries**

Cuando se accede a ForeignKeys en el serializer, usar `select_related()` para evitar N+1 queries:

```python
queryset = Lugares.objects.select_related('padre', 'tipo_nivel').all()
```

### 4. **Campos Calculados con `SerializerMethodField`**

Para datos derivados (como `numero_ue`), usar métodos en el serializer:

```python
numero_ue = serializers.SerializerMethodField()

def get_numero_ue(self, obj):
    # Lógica de cálculo
    return valor
```

---

## 🚀 Estado Final

✅ **API de lugares funciona correctamente (200 OK)**  
✅ **Serializador usa campos correctos del modelo**  
✅ **ViewSet configurado con campos válidos**  
✅ **Campo `numero_ue` calculado automáticamente**  
✅ **Widget de lugares carga y funciona sin errores**  
✅ **Autocompletado de número UE funciona**  
✅ **Filtrado y ordenamiento por `tipo_nivel` disponible**

---

**Corregido:** 12 de Octubre de 2025  
**Archivos modificados:** 2 (serializers.py, views.py)  
**Error resuelto:** TypeError - 'Meta.fields' must not contain non-model field names  
**Estado:** ✅ **RESUELTO Y VERIFICADO**
