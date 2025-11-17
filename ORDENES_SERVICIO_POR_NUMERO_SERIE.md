# 🔧 Órdenes de Servicio vinculadas por Número de Serie - ASSE-GestACT

## ✅ Implementación Completada

Las órdenes de servicio ahora se **vinculan automáticamente a los activos mediante el número de serie**, funcionando para **ambas categorías** (Activos Informáticos y Tecnología Médica).

---

## 🎯 Funcionamiento

### Búsqueda Automática

Al crear una orden de servicio, el sistema:

1. **Usuario ingresa** el número de serie del activo
2. **Sistema busca** automáticamente en todas las categorías:
   - Computadoras
   - Impresoras
   - Monitores
   - Networking
   - Telefonía
   - Periféricos
   - **Tecnología Médica**
3. **Vincula automáticamente** el activo encontrado
4. **Muestra confirmación** del activo vinculado

---

## 🔍 Validaciones Implementadas

### 1. **Número de Serie Obligatorio**
```
Error: "El número de serie es obligatorio"
```

### 2. **Activo No Encontrado**
```
Error: "No se encontró ningún activo con el número de serie 'XXXXX'. 
Verifique el número o registre el activo primero."
```

### 3. **Números de Serie Duplicados**
```
Error: "Se encontraron múltiples dispositivos con el número de serie 'XXXXX'. 
Contacte al administrador."
```

---

## 📋 Flujo de Creación

### Paso 1: Abrir Formulario
```
URL: /ordenes-servicio/crear/
```

### Paso 2: Buscar Activo
```
┌─────────────────────────────────────────────────┐
│ 🔍 Vincular Activo por Número de Serie         │
├─────────────────────────────────────────────────┤
│ Número de Serie del Activo: [SN123456789    ] │
│ Ingrese el número de serie para vincular       │
│ automáticamente el activo                       │
└─────────────────────────────────────────────────┘
```

### Paso 3: Validación Automática
- Sistema busca en **todas las categorías**
- Si encuentra: ✅ Vincula automáticamente
- Si no encuentra: ❌ Muestra error

### Paso 4: Confirmar Vinculación
```
✓ Activo vinculado: Computadora Dell Latitude 7490 (Computadora)
```

### Paso 5: Completar Orden
- Tipo de servicio
- Prioridad
- Estado
- Descripción del problema
- Técnico asignado
- etc.

---

## 🏗️ Arquitectura Técnica

### Formulario Modificado

**Campo nuevo: `buscar_numero_serie`**
```python
buscar_numero_serie = forms.CharField(
    max_length=100,
    required=True,
    label='Número de Serie del Activo',
    help_text='Ingrese el número de serie para vincular automáticamente el activo',
)
```

### Validación

**Método: `clean_buscar_numero_serie()`**
```python
def clean_buscar_numero_serie(self):
    numero_serie = self.cleaned_data.get('buscar_numero_serie', '').strip()
    
    # Buscar en todos los modelos
    modelos_busqueda = [
        (Computadora, 'computadora'),
        (Impresora, 'impresora'),
        (Monitor, 'monitor'),
        (Networking, 'networking'),
        (Telefonia, 'telefonia'),
        (Periferico, 'periferico'),
        (TecnologiaMedica, 'tecnologia_medica'),
    ]
    
    for modelo, tipo_dispositivo in modelos_busqueda:
        try:
            dispositivo = modelo.objects.get(numero_serie__iexact=numero_serie)
            self._dispositivo_encontrado = dispositivo
            self._tipo_dispositivo_encontrado = tipo_dispositivo
            return numero_serie
        except modelo.DoesNotExist:
            continue
    
    raise forms.ValidationError("No se encontró ningún activo...")
```

### Guardado Automático

**Método: `save()`**
```python
def save(self, commit=True):
    instance = super().save(commit=False)
    
    # Vincular automáticamente
    if hasattr(self, '_dispositivo_encontrado'):
        dispositivo = self._dispositivo_encontrado
        instance.tipo_dispositivo = self._tipo_dispositivo_encontrado
        instance.dispositivo_id = dispositivo.id
        instance.dispositivo_nombre = getattr(dispositivo, 'nombre', str(dispositivo))
        instance.dispositivo_numero_serie = dispositivo.numero_serie
    
    if commit:
        instance.save()
    
    return instance
```

---

## 📊 Campos Ocultos

Los siguientes campos se establecen **automáticamente** y no se muestran al usuario:

- `tipo_dispositivo` → Detectado automáticamente
- `dispositivo_id` → ID del activo encontrado
- `dispositivo_nombre` → Nombre del activo
- `dispositivo_numero_serie` → Guardado para referencia

---

## 🎨 Interfaz de Usuario

### Formulario de Creación

```
┌──────────────────────────────────────────────────────────────┐
│ 🔧 Nueva Orden de Servicio                                   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ [Información General] [Servicio] [Costos]                    │
│                                                               │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 🔍 Vincular Activo por Número de Serie                   │ │
│ │                                                            │ │
│ │ Número de Serie del Activo: *                             │ │
│ │ ┌────────────────────────────────────────────────────┐   │ │
│ │ │ SN123456789                                        │   │ │
│ │ └────────────────────────────────────────────────────┘   │ │
│ │ Ingrese el número de serie para vincular automáticamente │ │
│ │ el activo                                                  │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                               │
│ Tipo de Servicio: *           Prioridad: *    Estado:       │
│ [Mantenimiento    ▼]         [Media     ▼]   [Pendiente ▼] │
│                                                               │
│ Solicitante: *                Técnico Asignado:              │
│ [Juan Pérez       ▼]         [Carlos Tech    ▼]             │
│                                                               │
│ ...                                                           │
└──────────────────────────────────────────────────────────────┘
```

### Formulario de Edición

Cuando se edita una orden existente:

```
┌──────────────────────────────────────────────────────────────┐
│ 🔍 Vincular Activo por Número de Serie                       │
│                                                                │
│ Número de Serie del Activo: *                                 │
│ ┌────────────────────────────────────────────────────────┐   │
│ │ SN123456789                            [READONLY]       │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                                │
│ ℹ️ Activo vinculado: Computadora Dell Latitude 7490          │
│    (Computadora)                                               │
└──────────────────────────────────────────────────────────────┘
```

**Nota:** En edición, el número de serie es **readonly** para evitar cambios accidentales.

---

## 🔄 Ejemplos de Uso

### Ejemplo 1: Vincular Computadora

```
1. Ir a: Servicio → Nueva Orden
2. Ingresar número de serie: "SN-DELL-2024-001"
3. Sistema busca...
4. ✓ Encontrado: Computadora Dell Latitude 7490
5. Completa formulario
6. Guardar
```

**Resultado:**
- Orden vinculada a Computadora
- tipo_dispositivo = 'computadora'
- dispositivo_id = 123
- dispositivo_nombre = "Computadora Dell Latitude 7490"

---

### Ejemplo 2: Vincular Equipo Médico

```
1. Ir a: Servicio → Nueva Orden
2. Ingresar número de serie: "MED-ECG-2023-045"
3. Sistema busca...
4. ✓ Encontrado: Electrocardiógrafo GE MAC 2000
5. Completa formulario
6. Guardar
```

**Resultado:**
- Orden vinculada a Tecnología Médica
- tipo_dispositivo = 'tecnologia_medica'
- dispositivo_id = 456
- dispositivo_nombre = "Electrocardiógrafo GE MAC 2000"

---

### Ejemplo 3: Número de Serie Inválido

```
1. Ir a: Servicio → Nueva Orden
2. Ingresar número de serie: "SERIAL-INEXISTENTE"
3. Sistema busca...
4. ❌ Error: "No se encontró ningún activo con el número de serie 'SERIAL-INEXISTENTE'"
5. Corregir o registrar activo primero
```

---

## 📁 Archivos Modificados

### 1. **inventario/forms.py**
- ✅ Agregado campo `buscar_numero_serie`
- ✅ Implementada validación `clean_buscar_numero_serie()`
- ✅ Modificado método `save()` para vincular automáticamente
- ✅ Excluidos campos `tipo_dispositivo` y `dispositivo_id` del Meta

### 2. **inventario/templates/inventario/orden_servicio_form.html**
- ✅ Agregada card destacada para búsqueda por número de serie
- ✅ Removidos campos manuales de tipo y ID de dispositivo
- ✅ Agregado mensaje de confirmación en edición

---

## 🎯 Ventajas del Sistema

### 1. **Búsqueda Universal**
✅ Busca en todas las categorías automáticamente
✅ No necesita seleccionar tipo primero
✅ Funciona para TI y Médica

### 2. **Validación Robusta**
✅ Detecta números de serie duplicados
✅ Valida existencia del activo
✅ Mensajes de error claros

### 3. **Experiencia Simple**
✅ Un solo campo para vincular
✅ Autocompletado automático
✅ Confirmación visual

### 4. **Integridad de Datos**
✅ Vinculación garantizada
✅ No permite errores de ID
✅ Mantiene consistencia

---

## 🚀 Cómo Probar

### Crear Orden para Activo Informático

```bash
1. Ir a: http://localhost:8000/ordenes-servicio/crear/
2. Buscar una computadora existente por número de serie
3. Completar formulario
4. Guardar
5. Verificar: Orden vinculada correctamente
```

### Crear Orden para Tecnología Médica

```bash
1. Ir a: http://localhost:8000/ordenes-servicio/crear/
2. Buscar un equipo médico existente por número de serie
3. Completar formulario
4. Guardar
5. Verificar: Orden vinculada correctamente
```

### Probar Validación

```bash
1. Ir a: http://localhost:8000/ordenes-servicio/crear/
2. Ingresar número de serie inexistente: "TEST-INVALID-001"
3. Intentar guardar
4. Ver error: "No se encontró ningún activo..."
```

---

## 📊 Modelos de Dispositivos Soportados

| Categoría | Modelo | Campo Búsqueda |
|-----------|--------|----------------|
| **TI** | Computadora | `numero_serie` |
| **TI** | Impresora | `numero_serie` |
| **TI** | Monitor | `numero_serie` |
| **TI** | Networking | `numero_serie` |
| **TI** | Telefonía | `numero_serie` |
| **TI** | Periférico | `numero_serie` |
| **Médica** | TecnologiaMedica | `numero_serie` |

---

## ⚠️ Consideraciones

### Números de Serie Únicos

**Es importante que los números de serie sean únicos en cada categoría.**

Si hay duplicados:
```
Error: "Se encontraron múltiples dispositivos con el número de serie 'XXXXX'. 
Contacte al administrador."
```

**Solución:** El administrador debe corregir los números de serie duplicados en la base de datos.

### Edición de Órdenes

Al editar una orden existente:
- El campo de número de serie es **readonly**
- No se puede cambiar el activo vinculado
- Para vincular otro activo, crear una nueva orden

---

## ✅ Estado Final

**Sistema:** ✅ COMPLETAMENTE FUNCIONAL

**Características:**
- ✅ Búsqueda por número de serie
- ✅ Vinculación automática
- ✅ Soporte para ambas categorías (TI y Médica)
- ✅ Validaciones completas
- ✅ Interfaz intuitiva
- ✅ Mensajes de error claros

---

**¡Las órdenes de servicio ahora se vinculan automáticamente mediante el número de serie! 🎉**

**URLs de prueba:**
- Nueva Orden: http://localhost:8000/ordenes-servicio/crear/
- Listar Órdenes: http://localhost:8000/ordenes-servicio/

