# 🛒 Carrito de Envío a Servicio de Proveedor - ASSE-GestACT

## ✅ Implementación Completada

Se ha implementado un **sistema de carrito** para enviar múltiples activos a servicio de proveedores externos, similar al carrito de envío a unidades ejecutoras.

---

## 🎯 Funcionalidad Principal

### Sistema Dual de Carritos

**ASSE-GestACT ahora tiene DOS carritos independientes:**

1. **🧾 Carrito de Envío a Unidades** (Azul)
   - Envía activos entre unidades ejecutoras
   - Estado: Stock → Asignado
   - Genera remito de transferencia

2. **🔧 Carrito de Envío a Servicio** (Naranja)
   - Envía activos a proveedores para reparación/mantenimiento
   - Estado: Cualquiera → En Servicio
   - Genera registro de envío a proveedor

---

## 🛠️ Carrito de Servicio a Proveedor

### Características

✅ **Selección múltiple** - Agregar varios activos al carrito
✅ **Ambas categorías** - Activos TI y Tecnología Médica
✅ **Proveedor obligatorio** - Seleccionar a quién se envía
✅ **Motivo detallado** - Especificar razón del envío
✅ **Fecha estimada** - Cuándo se espera el retorno
✅ **Cambio automático de estado** - Activos pasan a "En Servicio"
✅ **Trazabilidad** - Registro completo del envío
✅ **Observaciones** - Notas adicionales

---

## 🔄 Flujo de Uso

### Paso 1: Seleccionar Activos

```
1. Ir a listado de cualquier tipo de activo:
   - Computadoras
   - Impresoras
   - Monitores
   - Networking
   - Telefonía
   - Periféricos
   - Tecnología Médica

2. Click en botón 🔧 (Enviar a Servicio) en cada activo
   - Icono: Herramientas
   - Color: Naranja/Amarillo
   - Tooltip: "Enviar a Servicio"

3. Ver contador aumentar en navbar (badge naranja)
```

---

### Paso 2: Abrir Carrito

```
1. Click en botón 🔧 en navbar (esquina superior derecha)
2. Se abre modal: "Carrito de Envío a Servicio"
3. Ver activos agregados en tabla
```

---

### Paso 3: Completar Información

```
Datos obligatorios:
┌────────────────────────────────────────────┐
│ Proveedor de Servicio: *                   │
│ [Seleccione un proveedor...        ▼]     │
├────────────────────────────────────────────┤
│ Fecha Estimada de Retorno:                 │
│ [2024-12-31               📅]              │
├────────────────────────────────────────────┤
│ Motivo del Envío: *                        │
│ ┌──────────────────────────────────────┐  │
│ │ Ej: Reparación de placa madre,       │  │
│ │     Calibración anual, etc.          │  │
│ └──────────────────────────────────────┘  │
├────────────────────────────────────────────┤
│ Observaciones:                             │
│ ┌──────────────────────────────────────┐  │
│ │ Notas adicionales...                 │  │
│ └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘

Tabla de activos:
┌─────────────┬──────────────┬────────┬─────────┬────────┬──────────┐
│ N° Serie    │ Nombre       │ Tipo   │ Estado  │ Lugar  │ Acciones │
├─────────────┼──────────────┼────────┼─────────┼────────┼──────────┤
│ SN-001      │ Dell...      │ Comp.  │ Activo  │ Lab 1  │ [🗑️]     │
│ MED-ECG-01  │ ECG GE...    │ Tec.M. │ Activo  │ Sala 3 │ [🗑️]     │
└─────────────┴──────────────┴────────┴─────────┴────────┴──────────┘
```

---

### Paso 4: Emitir Envío

```
1. Click en "Emitir Envío"
2. Confirmación
3. Sistema crea registro de envío
4. Cambia estado de activos a "En Servicio"
5. Limpia carrito
6. Muestra mensaje de éxito
```

---

## 🏗️ Arquitectura Técnica

### Modelos Creados

#### 1. EnvioServicioProveedor

**Campos principales:**
- `uuid` - Identificador único
- `numero` - Número de envío (auto-generado: ENV-YYYYMMDDHHMMSS)
- `fecha_envio` - Cuándo se envió
- `proveedor` - A qué proveedor se envió
- `motivo_envio` - Por qué se envió
- `observaciones` - Notas adicionales
- `fecha_estimada_retorno` - Cuándo se espera de vuelta
- `fecha_retorno_real` - Cuándo volvió realmente
- `estado` - Enviado / En Reparación / Reparado / Retornado / Cancelado
- `costo_servicio` - Cuánto costó el servicio
- `moneda` - UYU / USD
- `emitido_por` - Quién lo emitió

**Estados posibles:**
- `enviado` - Recién enviado al proveedor
- `en_reparacion` - Proveedor está trabajando
- `reparado` - Proveedor terminó
- `retornado` - Ya regresó a ASSE
- `cancelado` - Envío cancelado

---

#### 2. EnvioServicioActivo

**Campos principales:**
- `envio` - Relación con EnvioServicioProveedor
- `tipo_activo` - Computadora, Impresora, etc.
- `activo_id` - ID del activo
- `numero_serie` - Número de serie
- `nombre_activo` - Nombre completo
- `estado_previo` - Estado antes del envío
- `lugar_previo` - Lugar antes del envío
- `problema_reportado` - Descripción del problema
- `diagnostico_proveedor` - Qué encontró el proveedor
- `reparacion_realizada` - Qué hizo el proveedor

---

### Backend (Python)

**Archivo:** `inventario/views_servicio_proveedor.py`

**Vistas implementadas:**
- `agregar_activo()` - Agregar activo al carrito
- `remover_activo()` - Quitar activo del carrito
- `obtener_carrito()` - Obtener contenido actual
- `actualizar_carrito()` - Actualizar proveedor/motivo/fechas
- `limpiar_carrito()` - Vaciar carrito
- `emitir_envio()` - Crear registro y cambiar estados

**Lógica de emisión:**
```python
1. Validar que hay activos en carrito
2. Validar que hay proveedor seleccionado
3. Validar que hay motivo de envío
4. Crear registro EnvioServicioProveedor
5. Para cada activo:
   - Crear EnvioServicioActivo
   - Cambiar estado a "En Servicio"
6. Limpiar carrito
7. Retornar éxito
```

---

### Frontend (JavaScript)

**Archivo:** `inventario/static/inventario/js/servicio-proveedor.js`

**Funciones públicas:**
- `ServicioProveedorCarrito.agregar(tipo, id)` - Agregar activo
- `ServicioProveedorCarrito.remover(tipo, id)` - Remover activo
- `ServicioProveedorCarrito.cargar()` - Cargar desde servidor
- `ServicioProveedorCarrito.limpiar()` - Limpiar carrito
- `ServicioProveedorCarrito.emitir()` - Emitir envío

**Estado en sesión:**
```javascript
{
    items: {
        'computadora': { '1': {...}, '2': {...} },
        'tecnologia_medica': { '3': {...} }
    },
    proveedor_id: 5,
    motivo_envio: "Reparación urgente",
    observaciones: "Revisar conectores",
    fecha_estimada_retorno: "2024-12-31"
}
```

---

### URLs Agregadas

**API Endpoints:**
```python
/api/servicio-proveedor/agregar/      # POST - Agregar activo
/api/servicio-proveedor/remover/      # POST - Remover activo
/api/servicio-proveedor/obtener/      # GET  - Obtener carrito
/api/servicio-proveedor/actualizar/   # POST - Actualizar metadata
/api/servicio-proveedor/limpiar/      # POST - Limpiar carrito
/api/servicio-proveedor/emitir/       # POST - Emitir envío
```

---

## 🎨 Interfaz de Usuario

### Botones en Listados

**Antes:**
```
[Ver 👁️] [Editar ✏️] [Eliminar 🗑️]
```

**Ahora:**
```
[Ver 👁️] [Editar ✏️] [Enviar Unidad 🧾] [Enviar Servicio 🔧] [Eliminar 🗑️]
```

**Colores:**
- 🧾 Enviar a Unidad - Azul (Info)
- 🔧 Enviar a Servicio - Naranja (Warning)

---

### Navbar - Dos Carritos

```
┌───────────────────────────────────────────────────────────┐
│ ASSE-GestACT    [🏠][...menú...]     [🌓] [🧾²] [🔧¹]     │
└───────────────────────────────────────────────────────────┘
                                             ↑    ↑
                                        Envío  Servicio
                                        Unidad Proveedor
                                        (Rojo) (Naranja)
```

---

### Modal del Carrito

```
┌─────────────────────────────────────────────────────────────┐
│ 🔧 Carrito de Envío a Servicio                          [X] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Proveedor de Servicio: *        Fecha Est. Retorno:        │
│ [TechService SA       ▼]       [2024-12-31      📅]        │
│                                                              │
│ Motivo del Envío: *                                         │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Reparación de placa madre                              │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                              │
│ Observaciones:                                               │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Urgente - equipo crítico                               │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ N° Serie │ Nombre │ Tipo │ Estado │ Lugar │ Acción │      │ │
│ ├──────────┼────────┼──────┼────────┼───────┼────────┤      │ │
│ │ SN-001   │ Dell   │ Comp │ Activo │ Lab1  │  [🗑️]  │      │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│                               [Limpiar] [Emitir Envío]      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Comparación de Sistemas

| Característica | Carrito de Envío | Carrito de Servicio |
|----------------|------------------|---------------------|
| **Icono** | 🧾 Recibo | 🔧 Herramientas |
| **Color badge** | Rojo (#dc2626) | Naranja (#f59e0b) |
| **Destino** | Unidad Ejecutora | Proveedor |
| **Estado requiere** | Stock/Almacén | Cualquiera |
| **Estado final** | Asignado | En Servicio |
| **Documento** | Remito PDF | Registro de envío |
| **Retorno** | No aplica | Con fecha estimada |
| **Costo** | No | Sí |

---

## 🔄 Flujo Completo

### Enviar Activos a Servicio

```
1. Usuario navega listados
   ↓
2. Click en botón 🔧 en activos que necesitan servicio
   ↓
3. Contador naranja aumenta en navbar
   ↓
4. Click en carrito 🔧 en navbar
   ↓
5. Modal se abre con activos seleccionados
   ↓
6. Seleccionar proveedor
   ↓
7. Escribir motivo del envío
   ↓
8. Opcional: fecha estimada, observaciones
   ↓
9. Click "Emitir Envío"
   ↓
10. Sistema crea registro
    ↓
11. Activos cambian a estado "En Servicio"
    ↓
12. Carrito se limpia
    ↓
13. Mensaje de confirmación
```

---

### Recibir Activos de Servicio

```
(Flujo futuro - por implementar)

1. Usuario busca envío por número
2. Marca como "Retornado"
3. Activos vuelven a estado anterior o nuevo estado
4. Se registra fecha de retorno real
5. Se registra costo del servicio
```

---

## 📁 Archivos Creados/Modificados

### Backend

**1. inventario/models.py**
- ✅ Creado modelo `EnvioServicioProveedor`
- ✅ Creado modelo `EnvioServicioActivo`

**2. inventario/views_servicio_proveedor.py** (NUEVO)
- ✅ Vista `agregar_activo()`
- ✅ Vista `remover_activo()`
- ✅ Vista `obtener_carrito()`
- ✅ Vista `actualizar_carrito()`
- ✅ Vista `limpiar_carrito()`
- ✅ Vista `emitir_envio()`

**3. inventario/templatetags/inventario_tags.py** (NUEVO)
- ✅ Template tag `get_proveedores`

**4. inventario/urls.py**
- ✅ Importado `views_servicio_proveedor`
- ✅ Agregadas 6 URLs de API

**5. inventario/migrations/0021_envioservicioproveedor_envioservicioactivo.py**
- ✅ Migración creada y aplicada

---

### Frontend

**6. inventario/static/inventario/js/servicio-proveedor.js** (NUEVO)
- ✅ Sistema completo de carrito en JavaScript
- ✅ Gestión de estado
- ✅ Comunicación con API
- ✅ Renderizado dinámico

**7. inventario/static/inventario/css/custom.css**
- ✅ Estilos para `.btn-servicio-proveedor`
- ✅ Estilos para `.servicio-proveedor-counter`

**8. inventario/templates/inventario/base.html**
- ✅ Agregado botón de carrito de servicio en navbar
- ✅ Agregado contador naranja
- ✅ Agregado script servicio-proveedor.js
- ✅ Agregado modal completo

**9. Templates de listados actualizados:**
- ✅ `computadora_list.html`
- ✅ `impresora_list.html`
- ✅ `monitor_list.html`
- ✅ `networking_list.html`
- ✅ `telefonia_list.html`
- ✅ `periferico_list.html`
- ✅ `tecnologia_medica_list.html`

---

## 🎯 Casos de Uso

### Caso 1: Enviar Computadora a Reparación

```
1. Usuario en: /inventario/computadoras/
2. Click en 🔧 en "Computadora Dell Latitude" (ID: 5)
3. Confirmación: "Activo agregado al carrito de servicio"
4. Contador 🔧¹ aparece en navbar
5. Click en carrito 🔧
6. Modal abre
7. Seleccionar proveedor: "TechService SA"
8. Motivo: "Reparación de placa madre dañada"
9. Fecha estimada: 2024-12-15
10. Click "Emitir Envío"
11. Envío ENV-20241103120000 creado
12. Computadora cambia a estado "En Servicio"
```

---

### Caso 2: Enviar Múltiples Equipos Médicos

```
1. Usuario en: /inventario/tecnologia-medica/
2. Click en 🔧 en "Electrocardiógrafo GE" (ID: 2)
3. Click en 🔧 en "Monitor Signos Vitales" (ID: 7)
4. Contador 🔧² aparece
5. Click en carrito 🔧
6. Ver 2 equipos en tabla
7. Proveedor: "MedEquip Service"
8. Motivo: "Calibración anual"
9. Fecha: 2024-12-20
10. Observaciones: "Incluir certificados de calibración"
11. Click "Emitir Envío"
12. Ambos equipos cambian a "En Servicio"
```

---

### Caso 3: Remover Activo del Carrito

```
1. Usuario tiene 3 activos en carrito
2. Abre modal 🔧
3. Ve tabla con 3 activos
4. Click en 🗑️ en activo que no quiere enviar
5. Activo se remueve de la tabla
6. Contador baja a 🔧²
```

---

## 🔒 Validaciones

### Al Agregar Activo
✅ Activo existe
✅ Tipo de activo válido
❌ Activo ya en carrito → Error

### Al Emitir Envío
✅ Carrito no vacío
✅ Proveedor seleccionado
✅ Motivo especificado
✅ Estado "En Servicio" existe
❌ Falta información → Error

---

## 📊 Datos Registrados

### Información del Envío
- Número único (ENV-timestamp)
- Proveedor destino
- Motivo completo
- Fechas (envío, estimada, real)
- Estado del envío
- Costos (opcional)
- Quién lo emitió

### Información de cada Activo
- Tipo y ID del activo
- Número de serie y nombre
- Estado y lugar previos
- Problema reportado
- Diagnóstico (cuando retorne)
- Reparación realizada (cuando retorne)

---

## 🚀 Cómo Usar

### Enviar Activos a Servicio

**Paso a paso:**
```bash
1. Ir a cualquier listado de activos
2. Click en botón 🔧 en activos a enviar
3. Ver contador naranja aumentar
4. Click en carrito 🔧 (navbar)
5. Seleccionar proveedor
6. Escribir motivo
7. (Opcional) Fecha estimada
8. Click "Emitir Envío"
9. ✓ Confirmación
```

---

### Gestionar Proveedores

Los proveedores se gestionan en el sistema de base de datos.

**Crear proveedor** (por script o shell):
```python
from inventario.models import Proveedor

Proveedor.objects.create(
    nombre="TechService SA",
    telefono="+598 2XXX XXXX",
    email="contacto@techservice.com",
    direccion="Av. Principal 1234"
)
```

---

## ⚙️ Configuración Requerida

### Estado "En Servicio"

**El sistema requiere un estado llamado "En Servicio" en la base de datos.**

Si no existe, crear:
```python
from inventario.models import Estado

Estado.objects.create(
    nombre="En Servicio",
    # otros campos según tu configuración
)
```

---

## 🎨 Estilos Visuales

### Botón en Navbar

```css
/* Botón circular naranja con icono de herramientas */
.btn-servicio-proveedor {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: transparent;
    color: white;
}

/* Contador naranja */
.servicio-proveedor-counter {
    background: #f59e0b;  /* Naranja */
    color: white;
    font-size: 0.7rem;
}
```

---

## 🔄 Integración con Sistema Existente

### Compatibilidad

✅ **No interfiere con carrito de envío a unidades**
✅ **Usa mismos activos** (TI y Médica)
✅ **Sesión independiente** (claves diferentes)
✅ **Estilos consistentes** con el sistema

### Diferencias Clave

| Aspecto | Carrito Unidades | Carrito Servicio |
|---------|------------------|------------------|
| Sesión | `facturacion_carrito` | `servicio_proveedor_carrito` |
| Endpoints | `/api/facturacion/*` | `/api/servicio-proveedor/*` |
| Estado origen | Stock/Almacén | Cualquiera |
| Estado final | Según destino | En Servicio |
| Documento | PDF remito | Registro DB |

---

## ✅ Estado de Activos

### Flujo de Estados

```
[Activo en uso]
    ↓
[Click 🔧 Enviar a Servicio]
    ↓
[Agregado al carrito]
    ↓
[Emitir envío]
    ↓
[Estado: "En Servicio"]
    ↓
[Proveedor repara]
    ↓
[Marcar como "Retornado"]
    ↓
[Estado: vuelve a anterior o nuevo]
```

---

## 📋 Archivos del Sistema

### Nuevos Archivos Creados

1. ✅ `inventario/views_servicio_proveedor.py` (263 líneas)
2. ✅ `inventario/static/inventario/js/servicio-proveedor.js` (383 líneas)
3. ✅ `inventario/templatetags/inventario_tags.py` (10 líneas)
4. ✅ `inventario/migrations/0021_*.py` (auto-generado)

### Archivos Modificados

5. ✅ `inventario/models.py` (+132 líneas)
6. ✅ `inventario/urls.py` (+32 líneas)
7. ✅ `inventario/templates/inventario/base.html` (+47 líneas)
8. ✅ `inventario/static/inventario/css/custom.css` (+25 líneas)
9-15. ✅ 7 templates de listados (+7-10 líneas c/u)

**Total:**
- ~600 líneas de código nuevo
- 15 archivos modificados/creados
- 2 modelos nuevos
- 6 endpoints API
- Sistema completamente funcional

---

## 🔍 Próximas Mejoras (Opcional)

### Funcionalidades Sugeridas

1. **Vista de Envíos**
   - Listado de todos los envíos
   - Filtros por proveedor/estado
   - Ver detalle de cada envío

2. **Gestión de Retornos**
   - Marcar envíos como retornados
   - Restaurar estados de activos
   - Registrar costos finales

3. **Reportes**
   - Activos en servicio por proveedor
   - Costos de servicio por período
   - Tiempo promedio de servicio

4. **Notificaciones**
   - Alertas de fechas estimadas vencidas
   - Recordatorios de seguimiento

---

## ✅ Estado Final

**Sistema:** ✅ COMPLETAMENTE FUNCIONAL

**Carritos implementados:**
- ✅ Carrito de Envío a Unidades (Existente)
- ✅ Carrito de Envío a Servicio (NUEVO)

**Características:**
- ✅ Selección múltiple
- ✅ Validaciones completas
- ✅ Cambio automático de estados
- ✅ Trazabilidad total
- ✅ Interfaz intuitiva
- ✅ Integración perfecta

---

## 🚀 Cómo Probar

### 1. Verificar Estado "En Servicio"

**Ir a base de datos y verificar:**
```sql
SELECT * FROM inventario_estado WHERE nombre LIKE '%servicio%';
```

Si no existe, crear desde Django shell:
```bash
cd /home/usuario/Escritorio/ASSE-GestIT
source venv/bin/activate
python manage.py shell
```

```python
from inventario.models import Estado
Estado.objects.create(nombre="En Servicio")
```

---

### 2. Crear Proveedores de Prueba

```python
from inventario.models import Proveedor

Proveedor.objects.create(
    nombre="TechService Uruguay",
    telefono="+598 2XXX XXXX",
    email="contacto@techservice.uy",
    direccion="18 de Julio 1234"
)

Proveedor.objects.create(
    nombre="MedEquip Service",
    telefono="+598 2YYY YYYY",
    email="servicio@medequip.com",
    direccion="Bulevar Artigas 5678"
)
```

---

### 3. Probar Carrito

**Test básico:**
```
1. Ir a: http://localhost:8000/inventario/computadoras/
2. Click en 🔧 en una computadora
3. Ver contador naranja: 🔧¹
4. Click en carrito 🔧 (navbar)
5. Ver modal con computadora
6. Seleccionar proveedor: "TechService Uruguay"
7. Motivo: "Prueba de sistema"
8. Click "Emitir Envío"
9. Ver confirmación
10. Verificar que computadora cambió a "En Servicio"
```

**Test múltiple:**
```
1. Agregar 3 activos diferentes al carrito
2. Ver contador: 🔧³
3. Abrir modal
4. Ver 3 activos en tabla
5. Remover 1 activo
6. Ver contador: 🔧²
7. Completar y emitir
8. Verificar 2 activos en "En Servicio"
```

---

## ⚠️ Importante

### Requisito: Estado "En Servicio"

**El sistema REQUIERE que exista un estado llamado "En Servicio".**

Si al emitir un envío aparece el error:
```
"No se encontró el estado 'En Servicio'. Créelo en el sistema."
```

**Solución:** Crear el estado como se indica arriba.

---

### Diferencia con Órdenes de Servicio

**Carrito de Servicio a Proveedor:**
- Envío masivo de activos a proveedor externo
- Activos salen de ASSE temporalmente
- Estado: "En Servicio"
- Retornan después de reparación

**Órdenes de Servicio:**
- Trabajo interno en ASSE
- Activos permanecen en ASSE
- Estados diversos
- Técnicos internos

**Ambos sistemas son complementarios.**

---

## 📊 Resumen Visual

### Navbar con Dos Carritos

```
┌──────────────────────────────────────────────────┐
│ ASSE-GestACT  [Menú...] [🌓][🧾²][🔧¹] [User▼] │
└──────────────────────────────────────────────────┘
                             ↑   ↑
                          Envío  Servicio
                          Unidad Proveedor
```

### Listado con Botones

```
┌─────────────────────────────────────────────────────────────┐
│ Activos Informáticos                                        │
├─────────────────────────────────────────────────────────────┤
│ N° Serie │ Nombre │ Estado │ Lugar │ Acciones               │
├──────────┼────────┼────────┼───────┼────────────────────────┤
│ SN-001   │ Dell   │ Activo │ Lab 1 │ [👁️][✏️][🧾][🔧][🗑️]  │
└─────────────────────────────────────────────────────────────┘
                                     ↑    ↑
                                 Enviar  Enviar
                                 Unidad  Servicio
```

---

**¡Sistema de Carrito de Servicio a Proveedor completamente implementado! 🎉**

**Pruébalo ahora:**
1. Recarga la página (Ctrl + Shift + R)
2. Verás el botón 🔧 en la navbar
3. Ve a cualquier listado de activos
4. Verás botones 🔧 en cada activo
5. Agregar al carrito y probar!

---

**URLs importantes:**
- Computadoras: http://localhost:8000/inventario/computadoras/
- Tecnología Médica: http://localhost:8000/inventario/tecnologia-medica/

