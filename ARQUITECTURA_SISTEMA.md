# 🏗️ Arquitectura del Sistema ASSE-GestACT

## 📋 Índice

1. [Visión General](#visión-general)
2. [Arquitectura General](#arquitectura-general)
3. [Capas del Sistema](#capas-del-sistema)
4. [Módulos del Sistema](#módulos-del-sistema)
5. [Modelos de Datos](#modelos-de-datos)
6. [APIs REST](#apis-rest)
7. [Sistema de Autenticación](#sistema-de-autenticación)
8. [Flujo de Datos](#flujo-de-datos)
9. [Tecnologías Utilizadas](#tecnologías-utilizadas)
10. [Estructura de Directorios](#estructura-de-directorios)

---

## 🎯 Visión General

**ASSE-GestACT** es un sistema web de gestión integral de activos para instituciones de salud, diseñado específicamente para administrar tanto **activos informáticos** como **tecnología médica** con sus particularidades específicas.

### Objetivo Principal
Proporcionar una plataforma unificada para:
- Gestionar inventario de activos tecnológicos
- Controlar mantenimientos y servicios
- Monitorear garantías y calibraciones
- Generar reportes y trazabilidad
- Gestionar facturación y remitos

---

## 🏛️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTACIÓN (Frontend)                   │
├─────────────────────────────────────────────────────────────┤
│  • Templates HTML (Django Templates)                        │
│  • JavaScript (Vanilla + Bootstrap)                         │
│  • CSS (Bootstrap 5 + Custom)                               │
│  • Chart.js (Gráficos)                                      │
└─────────────────────────────────────────────────────────────┘
                              ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE APLICACIÓN                        │
├─────────────────────────────────────────────────────────────┤
│  • Views (Class-Based Views)                                │
│  • Frontend Views (ListView, DetailView, CreateView, etc.)  │
│  • Forms (Django Forms con validaciones)                    │
│  • ViewSets (Django REST Framework)                         │
│  • Serializers (REST API)                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE NEGOCIO                          │
├─────────────────────────────────────────────────────────────┤
│  • Models (Lógica de negocio)                               │
│  • Validaciones personalizadas                              │
│  • Cálculos automáticos                                     │
│  • Signals y Triggers                                       │
│  • Bitácora automática                                      │
└─────────────────────────────────────────────────────────────┘
                              ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE DATOS                            │
├─────────────────────────────────────────────────────────────┤
│  • Django ORM                                               │
│  • SQLite (Desarrollo)                                      │
│  • PostgreSQL / MySQL / Oracle (Producción - configurable)  │
│  • Migraciones (Django Migrations)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📚 Capas del Sistema

### 1. Capa de Presentación

#### A. Templates (Django Template Engine)
- **Base Templates:**
  - `base.html` - Plantilla base con menú de navegación
  - `base_device_form.html` - Plantilla base para formularios de dispositivos

- **Dashboards:**
  - `dashboard.html` - Dashboard de Activos Informáticos
  - `dashboard_tecnologia_medica.html` - Dashboard de Tecnología Médica

- **Templates por Módulo:**
  - `{modulo}_list.html` - Listados con filtros y paginación
  - `{modulo}_form.html` - Formularios de creación/edición
  - `{modulo}_detail.html` - Vistas de detalle

- **Partials (Componentes Reutilizables):**
  - `partials/estado_badge.html` - Badge de estado
  - `partials/delete_modal.html` - Modal de confirmación
  - `partials/bitacora_sidebar.html` - Sidebar de bitácora
  - `partials/plantillas_sidebar.html` - Sidebar de plantillas

#### B. Assets Estáticos
- **CSS:** Bootstrap 5 + estilos personalizados
- **JavaScript:** 
  - Bootstrap 5 JS
  - Chart.js (gráficos)
  - Scripts personalizados (validaciones, widgets)
- **Iconos:** Bootstrap Icons

### 2. Capa de Aplicación

#### A. Views (Class-Based Views)
```python
ListView → Listados con filtros y paginación
DetailView → Detalles de un registro
CreateView → Creación de nuevos registros
UpdateView → Edición de registros existentes
DeleteView → Eliminación de registros
```

#### B. ViewSets (REST API)
```python
ModelViewSet → CRUD completo vía API
@action → Endpoints personalizados
Filters → django-filter, SearchFilter, OrderingFilter
Serializers → Transformación de datos
```

#### C. Forms
```python
ModelForm → Formularios basados en modelos
Widgets → TreeSelectWidget (selección jerárquica)
          DatePickerInput (calendario HTML5)
          DateTimePickerInput (fecha/hora)
Mixins → FormControlMixin (aplicar clases Bootstrap)
```

### 3. Capa de Negocio

#### A. Models (Modelos de Django)
- **Modelos Base:** ModulosVisibles, Estado, TipoGarantia, Proveedor, Fabricante, Modelo
- **Jerarquía:** TipoNivel, Lugares (hasta 7 niveles)
- **Activos Informáticos:** Computadora, Monitor, Impresora, Networking, Telefonia, Periferico
- **Tecnología Médica:** TecnologiaMedica, TipoTecnologiaMedica
- **Recursos:** Insumo, Software
- **Gestión:** OrdenServicio, Bitacora, Factura, FacturaActivo, PlantillaDispositivo

#### B. Lógica de Negocio
```python
# Validaciones personalizadas
def clean(self):
    # Validar coherencia de datos
    # Validar rangos y formatos
    # Validar relaciones entre modelos

# Cálculos automáticos
def save(self, *args, **kwargs):
    # Generar números automáticos
    # Calcular fechas de garantía/calibración
    # Actualizar campos calculados
    # Registrar en bitácora

# Propiedades computadas
@property
def garantia_vigente(self):
    # Verificar si la garantía está vigente

@property
def requiere_calibracion_proxima(self):
    # Detectar si requiere calibración en 30 días
```

### 4. Capa de Datos

#### A. ORM (Object-Relational Mapping)
- Django ORM con soporte para múltiples bases de datos
- Consultas optimizadas con `select_related` y `prefetch_related`
- Índices en campos clave para rendimiento

#### B. Migraciones
- 20 migraciones aplicadas
- Versionado de esquema
- Rollback disponible

---

## 🧩 Módulos del Sistema

### Módulo 1: Activos Informáticos 💻

**Componentes:**
```
├── Computadoras
│   ├── Tipos de Computadora
│   ├── Vinculación con Monitores
│   └── Vinculación con Impresoras
├── Monitores
│   └── Tipos de Monitor
├── Impresoras
│   ├── Tipos de Impresora
│   └── Gestión de tóner extra
├── Networking
│   ├── Switches, Routers
│   └── Configuración de red (IP, MAC, puertos, PoE)
├── Telefonía
│   ├── IP, Analógicos
│   └── Extensiones y líneas
└── Periféricos
    └── Teclados, ratones, escáneres
```

**Características:**
- Direcciones IP y MAC
- Vinculación de dispositivos
- Gestión de garantías
- Números de inventario automáticos

### Módulo 2: Tecnología Médica 🏥

**Componentes:**
```
├── Equipos Médicos
│   ├── Ventiladores Mecánicos
│   ├── Monitores de Paciente
│   ├── Desfibriladores
│   ├── Bombas de Infusión
│   ├── Electrocardiógrafos
│   ├── Oxímetros
│   ├── Incubadoras
│   ├── Equipos de Rayos X
│   ├── Ecógrafos
│   └── Autoclaves
└── Gestión Especializada
    ├── Clasificación de Riesgo (I-IV)
    ├── Registro Sanitario
    ├── Calibración Periódica
    ├── Mantenimiento Preventivo
    └── Área de Aplicación
```

**Características Específicas:**
- Alertas de calibración (30 días)
- Alertas de mantenimiento (30 días)
- Clasificación de riesgo visual
- Requisitos de personal especializado
- Especificaciones técnicas médicas

### Módulo 3: Servicio y Mantenimiento 🔧

**Órdenes de Servicio:**
```
├── Tipos de Servicio
│   ├── Mantenimiento Preventivo
│   ├── Mantenimiento Correctivo
│   ├── Reparación
│   ├── Calibración
│   ├── Instalación
│   ├── Actualización
│   ├── Diagnóstico
│   └── Limpieza
├── Estados
│   ├── Pendiente
│   ├── En Proceso
│   ├── En Espera de Repuesto
│   ├── Completada
│   └── Cancelada
└── Gestión
    ├── Asignación de técnicos
    ├── Prioridades (Baja, Media, Alta, Crítica)
    ├── Costos (Mano de obra + Repuestos)
    ├── Tiempos de resolución
    └── Observaciones y diagnósticos
```

**Aplicable a:**
- ✅ TODOS los tipos de dispositivos (TI + Médica)

### Módulo 4: Recursos 📦

**Componentes:**
```
├── Software
│   ├── Licencias
│   ├── Versiones
│   └── Fechas de expiración
└── Insumos
    ├── Stock
    ├── Punto de reorden
    └── Gestión de inventario
```

### Módulo 5: Gestión 📋

**Componentes:**
```
├── Lugares (Jerarquía de 7 niveles)
│   ├── TipoNivel
│   └── Lugares (auto-referencial)
├── Facturación
│   ├── Facturas
│   └── FacturaActivo (remitos)
├── Bitácora
│   └── Registro automático de eventos
└── Plantillas
    └── Plantillas de dispositivos
```

### Módulo 6: Configuración ⚙️

**Componentes:**
```
├── Estados
├── Tipos de Garantía
├── Proveedores
├── Fabricantes
├── Modelos
└── Configuración de Lugares
```

---

## 🗄️ Modelos de Datos

### Jerarquía de Modelos

#### Modelos Base (Compartidos)
```
Estado ──┐
         ├──→ Computadora
Lugares ─┤     Impresora
         │     Monitor
         │     Networking
         │     Telefonia
         │     Periferico
         │     TecnologiaMedica
         │     Software
         └──→ Insumo

Fabricante ──→ Modelo ──→ Dispositivos
Proveedor ──────────────→ Dispositivos
TipoGarantia ────────────→ Dispositivos
```

#### Estructura Jerárquica de Lugares
```
Nivel 1: Unidad Ejecutora (requiere código)
   ├── Nivel 2: Unidad Asistencial
   │   ├── Nivel 3: Servicio
   │   │   ├── Nivel 4: Área
   │   │   │   ├── Nivel 5: Sector
   │   │   │   │   ├── Nivel 6: Ubicación
   │   │   │   │   │   └── Nivel 7: Puesto

Campos calculados automáticamente:
- nivel (1-7)
- nombre_completo ("UE > UA > Servicio > ...")
- ruta_jerarquica ("/1/5/12/23/")
```

#### Modelos de Dispositivos

**Campos Comunes (Todos los Dispositivos):**
```python
nombre: CharField
estado: ForeignKey(Estado)
lugar: ForeignKey(Lugares)
fabricante: ForeignKey(Fabricante)
modelo: ForeignKey(Modelo)
numero_serie: CharField (unique para hw físico)
numero_inventario: CharField (generado automáticamente)
proveedor: ForeignKey(Proveedor)
tipo_garantia: ForeignKey(TipoGarantia)
fecha_adquisicion: DateField
anos_garantia: PositiveIntegerField
fecha_finalizacion_garantia: DateField (calculado automáticamente)
valor_adquisicion: DecimalField
moneda: CharField (UYU, USD, EUR)
comentarios: TextField
fecha_creacion: DateTimeField (auto)
fecha_modificacion: DateTimeField (auto)
```

**Campos Específicos por Tipo:**

**Computadora:**
```python
tipo_computadora: ForeignKey
direccion_ip: GenericIPAddressField
direccion_mac: CharField
monitores_vinculados: ManyToManyField(Monitor)
impresoras_vinculadas: ManyToManyField(Impresora)
```

**TecnologiaMedica:**
```python
tipo_tecnologia_medica: ForeignKey
numero_activo_fijo: CharField
registro_sanitario: CharField
clasificacion_riesgo: CharField (clase_i, clase_iia, clase_iib, clase_iii, clase_iv)
area_aplicacion: CharField
requiere_calibracion: BooleanField
frecuencia_calibracion_meses: PositiveIntegerField
fecha_ultima_calibracion: DateField
requiere_mantenimiento_preventivo: BooleanField
frecuencia_mantenimiento_meses: PositiveIntegerField
fecha_ultimo_mantenimiento: DateField
requiere_personal_especializado: BooleanField
voltaje_operacion: CharField
potencia: CharField
```

**Networking:**
```python
tipo_networking: ForeignKey
direccion_ip: GenericIPAddressField
direccion_mac: CharField
firmware_version: CharField
cantidad_puertos: PositiveIntegerField
soporte_poe: BooleanField
```

**Telefonia:**
```python
tipo_telefonia: ForeignKey
extension_interna: CharField
numero_linea: CharField
direccion_ip: GenericIPAddressField
direccion_mac: CharField
tipo_conexion: CharField
```

**Impresora:**
```python
tipo_impresora: ForeignKey
requiere_toner_extra: BooleanField
insumo_toner_extra: ForeignKey(Insumo)
cantidad_toner_extra: PositiveIntegerField
```

**Software:**
```python
tipo_software: ForeignKey
version: CharField
numero_licencia: CharField
cantidad_licencias: PositiveIntegerField
licencias_en_uso: PositiveIntegerField
fecha_expiracion: DateField
costo_total: DecimalField
```

**Insumo:**
```python
tipo_insumo: ForeignKey
cantidad_total: PositiveIntegerField
cantidad_disponible: PositiveIntegerField
punto_reorden: PositiveIntegerField
unidad_medida: CharField
activo: BooleanField
```

#### Modelo de Órdenes de Servicio

**OrdenServicio:**
```python
# Identificación
numero_orden: CharField (auto: OS-YYYYMMDD-####)
tipo_servicio: CharField (CHOICES)
estado: CharField (CHOICES)
prioridad: CharField (CHOICES)

# Dispositivo (Generic Foreign Key simulado)
tipo_dispositivo: CharField
dispositivo_id: PositiveIntegerField
dispositivo_nombre: CharField (calculado)
dispositivo_numero_serie: CharField (calculado)

# Descripción
descripcion_problema: TextField
diagnostico: TextField
solucion_aplicada: TextField

# Personal
solicitante: CharField
tecnico_asignado: CharField

# Fechas
fecha_solicitud: DateTimeField (auto)
fecha_inicio: DateTimeField
fecha_finalizacion: DateTimeField
fecha_estimada: DateField

# Costos
costo_mano_obra: DecimalField
costo_repuestos: DecimalField
costo_total: DecimalField (calculado)
moneda: CharField

# Otros
repuestos_utilizados: TextField
observaciones: TextField

# Propiedades computadas
@property tiempo_resolucion → Horas entre inicio y fin
@property esta_vencida → Si superó fecha estimada
@property dias_pendiente → Días desde solicitud
```

#### Modelo de Bitácora

**Bitacora:**
```python
# Evento
tipo_evento: CharField (registro, mantenimiento, cambio_estado, etc.)

# Dispositivo
tipo_dispositivo: CharField
dispositivo_id: PositiveIntegerField
dispositivo_nombre: CharField

# Detalles
descripcion: TextField
observaciones: TextField
valor_anterior: TextField
valor_nuevo: TextField

# Auditoría
usuario_responsable: CharField
fecha_evento: DateTimeField (auto)

# Método estático
@classmethod registrar_evento(...) → Registro centralizado
```

### 3. Capa de Lógica de Negocio

#### Generación Automática

**Número de Inventario:**
```python
def generar_numero_inventario(lugar, descriptor, referencia):
    """
    Formato: {CODIGO_UE}/{DESCRIPTOR}/{REFERENCIA}
    Ejemplo: 001/HP-Pavilion/ABC123
    """
    - Obtiene código de unidad ejecutora desde lugar
    - Sanitiza segmentos (reemplaza / por -)
    - Construye número único
```

**Número de Orden de Servicio:**
```python
Formato: OS-{YYYYMMDD}-{####}
Ejemplo: OS-20251031-0001
Auto-incrementa diariamente
```

**Número de Factura:**
```python
Formato: FAC-{YYYYMMDD}-{###}
Ejemplo: FAC-20251031-001
Auto-incrementa diariamente
```

#### Cálculos Automáticos

**Fecha de Finalización de Garantía:**
```python
fecha_finalizacion = fecha_adquisicion + relativedelta(years=anos_garantia)
```

**Próxima Calibración:**
```python
fecha_proxima = fecha_ultima_calibracion + relativedelta(months=frecuencia_calibracion_meses)
requiere_calibracion_proxima = 0 <= (fecha_proxima - today).days <= 30
```

**Costo Total de Orden:**
```python
costo_total = costo_mano_obra + costo_repuestos
```

#### Validaciones

**A nivel de Modelo:**
```python
# Validar coherencia fabricante-modelo
if modelo.fabricante != fabricante:
    raise ValidationError(...)

# Validar frecuencia si requiere calibración
if requiere_calibracion and not frecuencia_calibracion_meses:
    raise ValidationError(...)

# Validar unicidad de nombre en mismo padre
queryset = Lugares.objects.filter(nombre=nombre, padre=padre)
if queryset.exists():
    raise ValidationError(...)
```

### 4. Capa de Persistencia

#### Base de Datos

**Desarrollo:** SQLite
**Producción (configurable):** PostgreSQL, MySQL, Oracle

**Esquema:**
- 60+ tablas
- Relaciones: ForeignKey, ManyToManyField
- Índices en campos frecuentemente consultados
- Constraints: unique, unique_together

**Optimizaciones:**
```python
# Eager loading para reducir queries
.select_related('estado', 'lugar', 'fabricante', 'modelo')
.prefetch_related('monitores_vinculados', 'impresoras_vinculadas')

# Índices
indexes = [
    models.Index(fields=['tipo_dispositivo', 'dispositivo_id']),
    models.Index(fields=['estado']),
    models.Index(fields=['prioridad']),
]
```

---

## 🌐 APIs REST

### Endpoints Principales

#### Activos
```
GET    /api/computadoras/           → Lista computadoras
POST   /api/computadoras/           → Crea computadora
GET    /api/computadoras/{id}/      → Detalle
PUT    /api/computadoras/{id}/      → Actualiza
DELETE /api/computadoras/{id}/      → Elimina

(Similar para: impresoras, monitores, networking, telefonia, 
perifericos, tecnologia-medica, insumos, software)
```

#### Tecnología Médica
```
GET /api/tecnologia-medica/                    → Lista
GET /api/tecnologia-medica/requieren_calibracion/  → Alertas
GET /api/tecnologia-medica/requieren_mantenimiento/ → Alertas
```

#### Órdenes de Servicio
```
GET  /api/ordenes-servicio/                → Lista
POST /api/ordenes-servicio/                → Crea
GET  /api/ordenes-servicio/{id}/           → Detalle
PUT  /api/ordenes-servicio/{id}/           → Actualiza
GET  /api/ordenes-servicio/pendientes/     → Pendientes
GET  /api/ordenes-servicio/en_proceso/     → En proceso
GET  /api/ordenes-servicio/vencidas/       → Vencidas
GET  /api/ordenes-servicio/por_dispositivo/?tipo_dispositivo=X&dispositivo_id=Y
POST /api/ordenes-servicio/{id}/iniciar/   → Iniciar orden
POST /api/ordenes-servicio/{id}/completar/ → Completar orden
```

#### Catálogos
```
/api/estados/
/api/fabricantes/
/api/modelos/
/api/proveedores/
/api/lugares/
/api/tipos-garantia/
/api/tipos-computadora/
/api/tipos-monitor/
/api/tipos-impresora/
/api/tipos-networking/
/api/tipos-telefonia/
/api/tipos-periferico/
/api/tipos-tecnologia-medica/
/api/tipos-insumo/
/api/tipos-software/
```

#### Facturación
```
POST /api/facturacion/agregar/     → Agregar activo al carrito
POST /api/facturacion/remover/     → Remover del carrito
GET  /api/facturacion/obtener/     → Obtener carrito
POST /api/facturacion/actualizar/  → Actualizar carrito
POST /api/facturacion/limpiar/     → Limpiar carrito
POST /api/facturacion/emitir/      → Emitir factura
GET  /api/facturacion/descargar/{id}/ → PDF de factura
```

### Características de la API

**Paginación:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/computadoras/?page=2",
  "previous": null,
  "results": [...]
}
```

**Filtros:**
```
?search=texto           → Búsqueda en múltiples campos
?estado=1               → Filtrar por estado
?lugar=5                → Filtrar por lugar
?fabricante=3           → Filtrar por fabricante
?ordering=nombre        → Ordenar por campo
?ordering=-fecha_creacion → Orden descendente
```

**Formato de Respuesta:**
```json
{
  "id": 1,
  "nombre": "Computadora HP",
  "estado": 1,
  "estado_nombre": "Activo",
  "lugar": 5,
  "lugar_nombre": "Hospital Central > Piso 2 > Sala A",
  "fabricante": 2,
  "fabricante_nombre": "HP",
  "modelo": 10,
  "modelo_nombre": "Pavilion",
  "numero_serie": "ABC123",
  "numero_inventario": "001/HP-Pavilion/ABC123",
  "garantia_vigente": true,
  "dias_restantes_garantia": 180,
  ...
}
```

---

## 🔐 Sistema de Autenticación y Autorización

### Autenticación

**Basada en Django Auth:**
```python
User (django.contrib.auth.models.User)
├── username
├── password (hashed)
├── email
├── first_name
├── last_name
├── is_active
├── is_staff
├── is_superuser
└── groups (ManyToMany con Group)
```

### Grupos y Roles

**Grupos Implementados:**
```
1. Activos Informáticos
   └── Dashboard: Activos TI
   
2. Tecnología Médica
   └── Dashboard: Tecnología Médica
```

**Lógica de Dashboard:**
```python
def dashboard(request):
    if user.groups.contains('Tecnología Médica'):
        return dashboard_tecnologia_medica(request)
    elif user.groups.contains('Activos Informáticos'):
        return dashboard_activos_informaticos(request)
    else:
        return dashboard_activos_informaticos(request)  # Default
```

### Permisos

**Actual:** Sin restricciones (todos acceden a todo)
**Futuro:** Se pueden agregar permisos granulares por grupo

---

## 🔄 Flujo de Datos

### Flujo de Creación de Dispositivo

```
Usuario → Formulario HTML
    ↓
Validación Frontend (HTML5 + JS)
    ↓
POST a Django View (CreateView)
    ↓
Form.is_valid() - Validaciones de Django
    ↓
Model.clean() - Validaciones personalizadas
    ↓
Model.save()
    ├─→ Generar número_inventario
    ├─→ Calcular fecha_finalizacion_garantia
    ├─→ Validar coherencia fabricante-modelo
    └─→ Registrar en Bitacora
    ↓
Guardar en Base de Datos
    ↓
Redirect a lista o detalle
    ↓
Mensaje de éxito al usuario
```

### Flujo de Orden de Servicio

```
1. Creación
   Usuario → OrdenServicioCreateView
       ↓
   Selecciona tipo de dispositivo y ID
       ↓
   Describe problema
       ↓
   Sistema genera número automático
       ↓
   Registra en Bitacora

2. Procesamiento
   Técnico → OrdenServicioUpdateView
       ↓
   Cambia estado a "En Proceso"
       ↓
   Registra fecha_inicio automáticamente
       ↓
   Agrega diagnóstico
       ↓
   Sistema registra en Bitacora

3. Finalización
   Técnico → Completa orden
       ↓
   Agrega solución_aplicada
       ↓
   Registra costos
       ↓
   Sistema calcula costo_total
       ↓
   Registra fecha_finalizacion
       ↓
   Actualiza Bitacora
       ↓
   Notifica finalización
```

### Flujo de Alertas

```
Sistema (Cron/Scheduler o consulta on-demand)
    ↓
Consulta dispositivos TecnologiaMedica
    ↓
Para cada equipo:
    ├─→ Si requiere_calibracion == True
    │   └─→ Calcular fecha_proxima_calibracion
    │       └─→ Si días_restantes <= 30:
    │           └─→ Marcar en Dashboard como alerta
    │
    └─→ Si requiere_mantenimiento_preventivo == True
        └─→ Calcular fecha_proximo_mantenimiento
            └─→ Si días_restantes <= 30:
                └─→ Marcar en Dashboard como alerta
```

---

## 💻 Tecnologías Utilizadas

### Backend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.10+ | Lenguaje principal |
| **Django** | 5.1.4 | Framework web |
| **Django REST Framework** | 3.15+ | API REST |
| **django-filter** | 24.3+ | Filtros avanzados |
| **django-cors-headers** | 4.5+ | CORS para API |
| **python-dateutil** | 2.9+ | Manejo de fechas |

### Frontend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Bootstrap** | 5.3 | Framework CSS |
| **Bootstrap Icons** | 1.11 | Iconografía |
| **Chart.js** | 4.4.0 | Gráficos interactivos |
| **JavaScript** | ES6+ | Interactividad |

### Base de Datos

| Motor | Soporte | Estado |
|-------|---------|--------|
| **SQLite** | ✅ | Desarrollo (actual) |
| **PostgreSQL** | ✅ | Producción (configurable) |
| **MySQL** | ✅ | Producción (configurable) |
| **Oracle** | ✅ | Producción (configurable) |

---

## 📁 Estructura de Directorios

```
ASSE-GestACT/
├── sgai/                           # Proyecto Django principal
│   ├── __init__.py
│   ├── settings.py                 # Configuración general
│   ├── urls.py                     # URLs principales
│   ├── wsgi.py                     # WSGI para producción
│   └── asgi.py                     # ASGI para async
│
├── inventario/                     # App principal de inventario
│   ├── migrations/                 # Migraciones de BD (20 archivos)
│   │   ├── 0001_initial.py
│   │   ├── ...
│   │   └── 0020_ordenservicio.py
│   │
│   ├── static/inventario/          # Assets estáticos
│   │   ├── css/                    # Estilos personalizados
│   │   ├── js/                     # JavaScript
│   │   └── fonts/                  # Fuentes
│   │
│   ├── templates/inventario/       # Templates HTML
│   │   ├── base.html               # Template base
│   │   ├── base_device_form.html   # Base para formularios
│   │   ├── dashboard.html          # Dashboard TI
│   │   ├── dashboard_tecnologia_medica.html  # Dashboard Médica
│   │   │
│   │   ├── computadora_*.html      # Templates de computadoras
│   │   ├── impresora_*.html        # Templates de impresoras
│   │   ├── monitor_*.html          # Templates de monitores
│   │   ├── networking_*.html       # Templates de networking
│   │   ├── telefonia_*.html        # Templates de telefonía
│   │   ├── periferico_*.html       # Templates de periféricos
│   │   ├── tecnologia_medica_*.html # Templates de tec. médica
│   │   ├── insumo_*.html           # Templates de insumos
│   │   ├── software_*.html         # Templates de software
│   │   ├── orden_servicio_*.html   # Templates de órdenes
│   │   │
│   │   ├── partials/               # Componentes reutilizables
│   │   │   ├── estado_badge.html
│   │   │   ├── delete_modal.html
│   │   │   ├── bitacora_sidebar.html
│   │   │   └── plantillas_sidebar.html
│   │   │
│   │   ├── sections/               # Secciones de formularios
│   │   │   ├── basic_info_section.html
│   │   │   └── purchase_warranty_section.html
│   │   │
│   │   ├── widgets/                # Widgets personalizados
│   │   │   ├── tree_select.html
│   │   │   └── hierarchical_select.html
│   │   │
│   │   └── reports/                # Templates de reportes
│   │       ├── menu.html
│   │       └── enterprise_report.html
│   │
│   ├── templatetags/               # Template tags personalizados
│   │   ├── __init__.py
│   │   ├── date_filters.py         # Filtros de fechas
│   │   └── form_extras.py          # Helpers de formularios
│   │
│   ├── management/commands/        # Comandos personalizados
│   │   └── ...
│   │
│   ├── models.py                   # Modelos de datos (3135 líneas)
│   ├── serializers.py              # Serializers API (959 líneas)
│   ├── views.py                    # ViewSets API (888 líneas)
│   ├── frontend_views.py           # Vistas frontend (3270 líneas)
│   ├── forms.py                    # Formularios (469 líneas)
│   ├── urls.py                     # Rutas (369 líneas)
│   ├── widgets.py                  # Widgets personalizados
│   ├── views_facturacion.py        # Vistas de facturación
│   ├── utils_reports.py            # Utilidades de reportes
│   ├── utils_facturacion.py        # Utilidades de facturación
│   └── admin.py                    # Admin de Django (deshabilitado)
│
├── seteo/                          # App de configuración
│   └── views.py                    # Vistas de configuración
│
├── venv/                           # Entorno virtual Python
│
├── db.sqlite3                      # Base de datos (desarrollo)
│
├── manage.py                       # CLI de Django
├── requirements.txt                # Dependencias Python
│
├── scripts de utilidad/
│   ├── crear_bd_automatico.py      # Crear BD automáticamente
│   ├── crear_datos_maestros.py     # Poblar datos iniciales
│   ├── generar_carga_masiva.py     # Generar archivos de carga masiva
│   ├── gestionar_usuarios.py       # Gestión de usuarios (NUEVO)
│   └── verificar_lugares.py        # Verificar jerarquía de lugares
│
└── Documentación/
    ├── README.md                   # Documentación general
    ├── ARQUITECTURA_SISTEMA.md     # Este archivo
    ├── SISTEMA_DASHBOARDS_POR_ROL.md
    ├── GUIA_DASHBOARDS_ROL.md
    ├── MODULO_TECNOLOGIA_MEDICA_Y_SERVICIO.md
    ├── JERARQUIA_LUGARES.md
    ├── WIDGET_JERARQUICO_IMPLEMENTADO.md
    └── ... (20+ archivos de documentación)
```

---

## 🎨 Patrones de Diseño Implementados

### 1. MTV (Model-Template-View)
Patrón arquitectónico de Django:
```
Model → Capa de datos y lógica de negocio
Template → Presentación (HTML)
View → Controlador (lógica de aplicación)
```

### 2. Class-Based Views (CBV)
Reutilización mediante herencia:
```python
ListView → Listados
DetailView → Detalles
CreateView → Creación
UpdateView → Edición
DeleteView → Eliminación
```

### 3. Mixins
Composición de funcionalidad:
```python
FormControlMixin → Aplicar clases Bootstrap
RedirectToListMixin → Manejo de redirecciones
LugarFilterMixin → Filtrado por lugares jerárquicos
```

### 4. Generic Foreign Key (Simulado)
Para relaciones polimórficas:
```python
# En OrdenServicio y Bitacora
tipo_dispositivo: CharField
dispositivo_id: PositiveIntegerField
```

### 5. Repository Pattern (Implícito)
A través de Django ORM:
```python
Computadora.objects.all()
Computadora.objects.filter(estado__nombre='Activo')
Computadora.objects.select_related('fabricante', 'modelo')
```

### 6. Factory Pattern
Para creación de registros en Bitácora:
```python
@classmethod
def registrar_evento(cls, tipo_dispositivo, dispositivo_obj, ...):
    return cls.objects.create(...)
```

---

## 🔍 Características Avanzadas

### 1. Jerarquía de Lugares (hasta 7 niveles)

**Estructura Auto-Referencial:**
```python
class Lugares(models.Model):
    padre = models.ForeignKey('self', ...)
    nivel = models.PositiveIntegerField()  # 1-7
    ruta_jerarquica = models.TextField()   # "/1/5/12/"
    nombre_completo = models.CharField()   # "UE > UA > Servicio"
    
    def obtener_ancestros(self)
    def obtener_descendientes(self)
    def obtener_ruta_completa(self)
```

**Widget Jerárquico:**
- TreeSelectWidget para selección visual de lugares
- Expansión/colapso de niveles
- Búsqueda en árbol
- Muestra ruta completa

### 2. Vinculación de Dispositivos

**Computadora puede vincular:**
```python
monitores_vinculados = ManyToManyField(Monitor)
impresoras_vinculadas = ManyToManyField(Impresora)

def vincular_monitor(monitor):
    # Agregar y registrar en bitácora

def desvincular_monitor(monitor):
    # Remover y registrar en bitácora
```

### 3. Plantillas de Dispositivos

**Reutilización de configuraciones:**
```python
class PlantillaDispositivo:
    tipo_dispositivo: CharField
    # ... campos comunes precargados
    
    def aplicar_a_dispositivo(dispositivo_form):
        # Pre-cargar valores en formulario nuevo
```

### 4. Sistema de Facturación/Remitos

**Movimiento de activos entre lugares:**
```python
Factura (cabecera)
    ├── lugar_origen
    ├── lugar_destino
    ├── uuid (identificador único)
    ├── qr_token (para QR code)
    └── FacturaActivo (detalle)
        ├── tipo_activo
        ├── activo_id
        ├── cantidad
        └── metadata
```

### 5. Bitácora Automática

**Registro de eventos:**
```python
Eventos registrados automáticamente:
- registro → Al crear dispositivo
- cambio_estado → Al cambiar estado
- cambio_ubicacion → Al mover de lugar
- asignacion_personal → Al vincular dispositivos
- mantenimiento → Al crear/completar orden de servicio
- servicio_garantia → Servicios cubiertos
- reparacion → Reparaciones
- actualizacion → Cambios de datos
- baja → Dar de baja equipo
```

### 6. Alertas Inteligentes

**Tipos de Alertas:**
```python
# Garantías próximas a vencer (30 días)
dispositivos.filter(
    fecha_finalizacion_garantia__gte=today,
    fecha_finalizacion_garantia__lte=today + 30 días
)

# Calibración próxima (30 días)
@property
def requiere_calibracion_proxima(self):
    fecha_proxima = ultima_calibracion + frecuencia_meses
    return 0 <= (fecha_proxima - today).days <= 30

# Mantenimiento próximo (30 días)
@property
def requiere_mantenimiento_proximo(self):
    fecha_proxima = ultimo_mantenimiento + frecuencia_meses
    return 0 <= (fecha_proxima - today).days <= 30

# Insumos bajo stock
insumos.filter(cantidad_disponible__lte=F('punto_reorden'))

# Órdenes vencidas
@property
def esta_vencida(self):
    return fecha_estimada < today and estado != 'completada'
```

---

## 🗺️ Diagrama de Componentes

### Vista de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENTE                              │
│                    (Navegador Web)                           │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ HTTP/HTTPS
                        │
┌───────────────────────┴─────────────────────────────────────┐
│                    SERVIDOR WEB                              │
│                  (Django + Gunicorn)                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   FRONTEND   │  │   REST API   │  │   ADMIN      │     │
│  │   VIEWS      │  │   VIEWSETS   │  │   (disabled) │     │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘     │
│         │                  │                                │
│         └──────────┬───────┘                                │
│                    │                                        │
│         ┌──────────┴───────────┐                           │
│         │    MODELS LAYER      │                           │
│         │  (Business Logic)    │                           │
│         └──────────┬───────────┘                           │
│                    │                                        │
│         ┌──────────┴───────────┐                           │
│         │    DJANGO ORM        │                           │
│         └──────────┬───────────┘                           │
│                    │                                        │
└────────────────────┼─────────────────────────────────────────┘
                     │
                     │ SQL
                     │
┌────────────────────┴─────────────────────────────────────────┐
│                     BASE DE DATOS                            │
│             (SQLite / PostgreSQL / MySQL)                    │
└─────────────────────────────────────────────────────────────┘
```

### Diagrama de Módulos

```
┌─────────────────────────────────────────────────────────────┐
│                      ASSE-GestACT                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         MÓDULO DE ACTIVOS INFORMÁTICOS             │    │
│  ├────────────────────────────────────────────────────┤    │
│  │ • Computadoras    • Networking                     │    │
│  │ • Monitores       • Telefonía                      │    │
│  │ • Impresoras      • Periféricos                    │    │
│  └─────────────────────┬──────────────────────────────┘    │
│                        │                                    │
│  ┌────────────────────┼────────────────────────────────┐   │
│  │         MÓDULO DE TECNOLOGÍA MÉDICA                 │   │
│  ├────────────────────┼────────────────────────────────┤   │
│  │ • Ventiladores     • Clasificación de Riesgo       │   │
│  │ • Monitores Médicos• Calibración                   │   │
│  │ • Desfibriladores  • Mantenimiento Preventivo      │   │
│  │ • Bombas Infusión  • Registro Sanitario            │   │
│  └─────────────────────┬──────────────────────────────┘   │
│                        │                                    │
│  ┌────────────────────┴────────────────────────────────┐   │
│  │    MÓDULO DE SERVICIO (COMPARTIDO)                  │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ • Órdenes de Servicio                               │   │
│  │ • Mantenimientos                                    │   │
│  │ • Reparaciones                                      │   │
│  │ • Calibraciones                                     │   │
│  └─────────────────────┬──────────────────────────────┘   │
│                        │                                    │
│  ┌────────────────────┴────────────────────────────────┐   │
│  │         MÓDULOS DE SOPORTE                          │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ • Software          • Lugares (Jerarquía)           │   │
│  │ • Insumos           • Facturación/Remitos           │   │
│  │ • Bitácora          • Reportes                      │   │
│  │ • Plantillas        • Estados/Catálogos             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Modelo de Datos Relacional

### Diagrama ER Simplificado

```
┌──────────────┐         ┌──────────────┐
│  Fabricante  │────1:N──│    Modelo    │
└──────────────┘         └───────┬──────┘
                                 │
                              N:1│
                                 ↓
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│    Estado    │────1:N──│ Dispositivos │──N:1────│   Lugares    │
└──────────────┘         │  (Abstracto) │         └──────┬───────┘
                         └──────┬───────┘                │
┌──────────────┐                │                        │
│  Proveedor   │────1:N─────────┤                        │
└──────────────┘                │                   1:N  │
                                │                  (auto-│
┌──────────────┐                │                  ref.) │
│TipoGarantia  │────1:N─────────┤                        │
└──────────────┘                │                        ↓
                                │                 ┌──────────────┐
                         ┌──────┴───────┐         │  TipoNivel   │
                         │              │         └──────────────┘
         ┌───────────────┼──────────────┼───────────────┐
         │               │              │               │
    ┌────┴────┐    ┌────┴────┐    ┌───┴──────┐   ┌────┴─────────┐
    │Computad │    │Impresora│    │ Monitor  │   │TecnologiaMed.│
    └────┬────┘    └─────────┘    └──────────┘   └──────────────┘
         │
    M:N  │  M:N
    ┌────┴────┐
    │ Monitor │
    │Impresora│
    └─────────┘

┌──────────────┐         ┌──────────────┐
│OrdenServicio │────N:1──│ Dispositivos │
│              │  (Generic FK simulado) │
└──────┬───────┘         └──────────────┘
       │
    1:N│
       ↓
┌──────────────┐
│   Bitacora   │
└──────────────┘
```

### Relaciones Clave

**1:N (Uno a Muchos):**
- Fabricante → Modelos
- Estado → Dispositivos
- Lugares → Dispositivos
- Proveedor → Dispositivos

**M:N (Muchos a Muchos):**
- Computadora ↔ Monitor
- Computadora ↔ Impresora

**Auto-Referencial:**
- Lugares → Lugares (padre-hijo)

**Generic FK (Simulado):**
- OrdenServicio → Cualquier Dispositivo
- Bitacora → Cualquier Dispositivo

---

## 🔄 Ciclo de Vida de un Dispositivo

```
1. CREACIÓN
   ↓
   Usuario completa formulario
   ↓
   Sistema valida datos
   ↓
   Se genera número_inventario automáticamente
   ↓
   Se calcula fecha_finalizacion_garantia
   ↓
   Se guarda en BD
   ↓
   Se registra evento "registro" en Bitácora
   ↓
   Se muestra en listado

2. USO/OPERACIÓN
   ↓
   Sistema monitorea:
   - Garantía vigente
   - Calibración (si aplica)
   - Mantenimiento (si aplica)
   ↓
   Si hay alerta:
   - Muestra en Dashboard
   - Permite crear Orden de Servicio

3. MANTENIMIENTO/SERVICIO
   ↓
   Se crea OrdenServicio
   ↓
   Se asigna técnico
   ↓
   Se ejecuta servicio
   ↓
   Se completa orden
   ↓
   Se registra en Bitácora
   ↓
   Se actualizan fechas del dispositivo (si aplica)

4. MOVIMIENTO
   ↓
   Se crea Factura/Remito
   ↓
   Se agregan activos al remito
   ↓
   Se emite factura
   ↓
   Se actualiza ubicación (lugar)
   ↓
   Se registra "cambio_ubicacion" en Bitácora
   ↓
   Se genera PDF con QR

5. BAJA/ELIMINACIÓN
   ↓
   Usuario solicita eliminación
   ↓
   Sistema confirma acción
   ↓
   Se registra evento "baja" en Bitácora
   ↓
   Se elimina de BD (o marca como inactivo)
```

---

## 🎭 Casos de Uso Principales

### Caso 1: Registro de Equipo Médico

```
Actor: Personal de Tecnología Médica

1. Usuario accede al dashboard (automático: Dashboard Médica)
2. Navega: Menú → Tecnología Médica → Agregar Nuevo
3. Completa formulario:
   - Nombre: "Ventilador Mecánico UCI-01"
   - Tipo: "Ventilador Mecánico"
   - Fabricante: "Dräger"
   - Modelo: "Evita V500"
   - Registro Sanitario: "RS-12345"
   - Clasificación: "Clase III" (riesgo alto)
   - Área: "UCI"
   - Requiere calibración: Sí, cada 6 meses
   - Requiere mantenimiento: Sí, cada 3 meses
4. Sistema:
   - Genera número_inventario: "001/Evita-V500/SN789"
   - Calcula fecha_finalizacion_garantia
   - Registra en Bitácora
5. Equipo visible en listado con alertas configuradas
```

### Caso 2: Alerta de Calibración

```
Sistema (automático):

1. Equipo "Ventilador UCI-01" tiene:
   - última_calibracion: 01/05/2025
   - frecuencia: 6 meses
   - Próxima calibración: 01/11/2025

2. Hoy es: 15/10/2025 (faltan 17 días)

3. Sistema detecta: requiere_calibracion_proxima = True

4. Dashboard muestra:
   - Badge de advertencia en listado
   - Tabla de "Equipos que requieren calibración"
   - Alerta visual

5. Personal crea Orden de Servicio:
   - Tipo: "Calibración"
   - Dispositivo: Ventilador UCI-01
   - Prioridad: Alta
   - Técnico: Asignado

6. Se ejecuta calibración y completa orden

7. Sistema actualiza:
   - fecha_ultima_calibracion = fecha_actual
   - Recalcula próxima alerta
   - Registra en Bitácora
```

### Caso 3: Orden de Servicio Interdepartamental

```
Escenario: Computadora con problema en área médica

1. Personal médico reporta problema
2. Solicita servicio (crea orden básica)
3. Orden llega a Personal TI (visible en su dashboard)
4. Técnico TI:
   - Ve orden en módulo "Servicio"
   - Asigna técnico
   - Cambia a "En Proceso"
   - Diagnóstica: "Disco duro fallando"
   - Solicita repuesto
   - Cambia a "En Espera de Repuesto"
5. Llega repuesto:
   - Técnico continúa
   - Reemplaza disco
   - Registra costos
   - Completa orden
6. Sistema:
   - Actualiza Bitácora de la computadora
   - Notifica finalización
   - Calcula tiempo de resolución
```

---

## 🔧 Configuración y Extensibilidad

### Configuración de Base de Datos

**Soporta múltiples motores:**
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.{motor}',
        # motor: sqlite3, postgresql, mysql, oracle
        ...
    }
}
```

**Cambio en caliente:**
- ConfiguracionSistema model
- Actualización dinámica de settings
- Scripts de inicialización por motor

### Extensibilidad del Sistema

**Agregar nuevo tipo de dispositivo:**
```python
1. Crear modelo en models.py:
   class NuevoDispositivo(models.Model):
       # Campos comunes + específicos

2. Crear serializers en serializers.py

3. Crear ViewSet en views.py

4. Crear Form en forms.py

5. Crear vistas frontend en frontend_views.py

6. Agregar URLs en urls.py

7. Crear templates

8. Agregar a dashboard

9. makemigrations + migrate
```

**Agregar nuevo tipo de servicio:**
- Actualizar `TIPO_SERVICIO_CHOICES` en OrdenServicio
- No requiere migración (solo choices)

**Agregar nuevo estado:**
- Crear registro en modelo Estado
- Asociar a ModulosVisibles (si aplica)

---

## 📈 Escalabilidad

### Horizontal

**Soportado:**
- Múltiples workers (Gunicorn)
- Load balancer (Nginx)
- Cache (Redis - configurable)
- Archivos estáticos en CDN

### Vertical

**Optimizaciones implementadas:**
```python
# Query optimization
.select_related()     # JOIN en queries
.prefetch_related()   # Reducir N+1 queries
.only()               # Campos específicos
.defer()              # Diferir campos pesados

# Database indexes
models.Index(fields=['estado', 'lugar'])
models.Index(fields=['tipo_dispositivo', 'dispositivo_id'])

# Paginación
paginate_by = 20      # Limitar resultados

# Caché (futuro)
@method_decorator(cache_page(60 * 15))  # Cache 15 min
```

---

## 🔒 Seguridad

### Implementado

✅ **CSRF Protection:** Tokens en formularios
✅ **SQL Injection:** Django ORM previene
✅ **XSS:** Auto-escape en templates
✅ **Password Hashing:** PBKDF2
✅ **CORS:** Configurado para APIs
✅ **Validación de Entrada:** En forms y models

### Pendiente (Producción)

⏭️ HTTPS/SSL
⏭️ Rate Limiting
⏭️ Permisos granulares por grupo
⏭️ Auditoría de accesos
⏭️ 2FA (Two-Factor Authentication)

---

## 📊 Métricas del Sistema

### Código

| Archivo | Líneas | Descripción |
|---------|--------|-------------|
| `models.py` | 3,135 | Modelos y lógica de negocio |
| `frontend_views.py` | 3,270 | Vistas frontend |
| `serializers.py` | 959 | Serializers API |
| `views.py` | 888 | ViewSets API |
| `forms.py` | 469 | Formularios |
| `urls.py` | 369 | Routing |
| **Total** | **~9,090** | **Líneas de código Python** |

### Base de Datos

| Concepto | Cantidad |
|----------|----------|
| Tablas | 60+ |
| Modelos | 30+ |
| Migraciones | 20 |
| Índices | 40+ |

### Frontend

| Concepto | Cantidad |
|----------|----------|
| Templates | 48 |
| Vistas (CBV) | 60+ |
| Endpoints API | 150+ |

---

## 🚀 Deployment

### Desarrollo

```bash
# Activar entorno virtual
source venv/bin/activate

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver

# Acceder: http://localhost:8000/
```

### Producción (Recomendado)

```
┌────────────┐
│   Nginx    │  (Proxy reverso + Archivos estáticos)
└─────┬──────┘
      │
      ↓
┌────────────┐
│  Gunicorn  │  (Servidor WSGI)
└─────┬──────┘
      │
      ↓
┌────────────┐
│   Django   │  (Aplicación)
└─────┬──────┘
      │
      ↓
┌────────────┐
│ PostgreSQL │  (Base de datos)
└────────────┘
```

**Stack de producción:**
```bash
# Web Server
Nginx 1.24+

# Application Server
Gunicorn 21+ (workers: CPU_COUNT * 2 + 1)

# Database
PostgreSQL 15+ o MySQL 8+

# Cache (opcional)
Redis 7+

# Monitoring
Sentry (errores)
Prometheus + Grafana (métricas)
```

---

## 🧪 Testing

### Estructura de Tests

```python
inventario/tests/
├── test_models.py          # Tests de modelos
├── test_views.py           # Tests de vistas
├── test_api.py             # Tests de API
├── test_forms.py           # Tests de formularios
└── test_integration.py     # Tests de integración
```

### Comandos

```bash
# Ejecutar todos los tests
python manage.py test

# Tests específicos
python manage.py test inventario.tests.test_models

# Con cobertura
coverage run --source='.' manage.py test
coverage report
```

---

## 📱 Responsive Design

### Breakpoints (Bootstrap 5)

```
xs: <576px   → Móviles verticales
sm: ≥576px   → Móviles horizontales
md: ≥768px   → Tablets
lg: ≥992px   → Desktops pequeños
xl: ≥1200px  → Desktops medianos
xxl: ≥1400px → Desktops grandes
```

### Adaptaciones

- Tablas → Responsive (scroll horizontal)
- Cards → Grid adaptativo
- Menú → Colapsable en móviles
- Formularios → 1 columna en móvil, 2-3 en desktop
- Dashboards → Cards apilables

---

## 🎨 Sistema de Temas

### Soporte de Tema Oscuro

```css
[data-bs-theme="dark"] {
    --dashboard-hero-bg: linear-gradient(...);
    --card-bg: #1a1d20;
    --card-border: #2d3238;
    ...
}
```

**Componentes adaptados:**
- Cards
- Tables
- Forms
- Modals
- Navbars
- Dashboards

---

## 🔮 Roadmap Futuro

### Corto Plazo (1-3 meses)
- [ ] Permisos granulares por grupo
- [ ] Exportación de reportes (Excel, PDF)
- [ ] Notificaciones por email
- [ ] Dashboard personalizable por usuario
- [ ] Filtros guardados

### Medio Plazo (3-6 meses)
- [ ] App móvil para técnicos
- [ ] Firma digital en órdenes
- [ ] Códigos QR en equipos
- [ ] Scanner de códigos de barra
- [ ] Integración con Active Directory

### Largo Plazo (6-12 meses)
- [ ] Machine Learning para predicción de fallas
- [ ] Análisis predictivo de mantenimientos
- [ ] Integración con sistemas HIS
- [ ] API pública documentada (Swagger)
- [ ] Módulo de compras y cotizaciones

---

## 📚 Referencias Técnicas

### Django
- **Documentación:** https://docs.djangoproject.com/
- **REST Framework:** https://www.django-rest-framework.org/

### Bootstrap
- **Documentación:** https://getbootstrap.com/
- **Icons:** https://icons.getbootstrap.com/

### Chart.js
- **Documentación:** https://www.chartjs.org/

### Python
- **Documentación:** https://docs.python.org/3/

---

## 📞 Información del Proyecto

**Nombre:** ASSE-GestACT
**Versión:** 2.0
**Framework:** Django 5.1.4
**Python:** 3.10+
**Licencia:** Propietario
**Fecha:** Octubre 2025

---

## 👥 Stakeholders

### Usuarios del Sistema

1. **Personal de TI**
   - Gestiona activos informáticos
   - Crea órdenes de servicio para equipos TI
   - Acceso a Dashboard de Activos Informáticos

2. **Personal de Tecnología Médica/Biomédica**
   - Gestiona equipos médicos
   - Controla calibraciones y mantenimientos
   - Crea órdenes de servicio para equipos médicos
   - Acceso a Dashboard de Tecnología Médica

3. **Administradores**
   - Gestión de usuarios y grupos
   - Configuración del sistema
   - Acceso completo a todos los módulos
   - Reportes empresariales

4. **Gerencia**
   - Visualización de reportes
   - Métricas y KPIs
   - Costos y presupuestos

---

## ✅ Estado Actual del Sistema

**Sistema:** ✅ Completamente funcional
**Base de Datos:** ✅ 20 migraciones aplicadas
**Módulos:** ✅ 9 módulos activos
**APIs:** ✅ 150+ endpoints disponibles
**Templates:** ✅ 48 vistas HTML
**Documentación:** ✅ 20+ archivos .md

### Módulos Activos

1. ✅ Computadoras
2. ✅ Monitores
3. ✅ Impresoras
4. ✅ Networking
5. ✅ Telefonía
6. ✅ Periféricos
7. ✅ **Tecnología Médica** (NUEVO)
8. ✅ **Órdenes de Servicio** (NUEVO)
9. ✅ Software
10. ✅ Insumos
11. ✅ Facturación/Remitos
12. ✅ Bitácora
13. ✅ Reportes
14. ✅ Configuración

---

## 📖 Convenciones de Código

### Nomenclatura

**Modelos:**
```python
PascalCase, singular
class Computadora(models.Model):
class TecnologiaMedica(models.Model):
```

**Vistas:**
```python
PascalCase + sufijo View
class ComputadoraListView(ListView):
class OrdenServicioCreateView(CreateView):
```

**URLs:**
```python
kebab-case
'computadoras/', 'tecnologia-medica/', 'ordenes-servicio/'
```

**Templates:**
```python
snake_case
computadora_list.html, orden_servicio_form.html
```

**Variables:**
```python
snake_case
numero_inventario, fecha_finalizacion_garantia
```

### Estructura de Código

**Orden en models.py:**
```python
1. Imports
2. Constantes (MONEDA_CHOICES, etc.)
3. Funciones auxiliares
4. Modelos base/catálogos
5. Modelos principales
6. Modelos de gestión
```

**Orden en cada modelo:**
```python
1. CHOICES (constantes)
2. Campos del modelo
3. class Meta
4. def clean(self)
5. def save(self, *args, **kwargs)
6. def __str__(self)
7. @property (propiedades computadas)
8. Métodos regulares
9. @classmethod (métodos de clase)
```

---

## 🎓 Arquitectura de Decisiones

### ¿Por qué Django?
- ✅ ORM robusto
- ✅ Admin automático
- ✅ Migraciones automáticas
- ✅ Seguridad built-in
- ✅ Escalable
- ✅ Gran ecosistema

### ¿Por qué Class-Based Views?
- ✅ Reutilización de código
- ✅ Mixins para funcionalidad compartida
- ✅ Menos boilerplate
- ✅ Convenciones claras

### ¿Por qué REST API + Templates?
- ✅ Flexibilidad
- ✅ Posibilidad de app móvil futura
- ✅ Integración con otros sistemas
- ✅ Templates para UX rápida

### ¿Por qué Grupos de Django?
- ✅ Sistema nativo y probado
- ✅ Fácil integración
- ✅ Extensible a permisos
- ✅ No requiere modelo adicional

---

## 🏆 Mejores Prácticas Implementadas

### Backend
- ✅ DRY (Don't Repeat Yourself)
- ✅ Validaciones en múltiples capas
- ✅ Separación de responsabilidades
- ✅ Fat models, thin views
- ✅ Uso de signals donde apropiado
- ✅ Documentación en código (docstrings)

### Frontend
- ✅ Progressive enhancement
- ✅ Mobile-first design
- ✅ Accesibilidad (ARIA labels)
- ✅ Feedback visual al usuario
- ✅ Confirmaciones en acciones destructivas

### Base de Datos
- ✅ Normalización hasta 3NF
- ✅ Índices en campos consultados
- ✅ Constraints de integridad
- ✅ Valores por defecto sensatos

---

**Documento creado:** 31 de Octubre, 2025  
**Versión del sistema:** 2.0  
**Última actualización:** Implementación de Tecnología Médica y Servicio

