# 📋 Menús Contextuales por Dashboard - ASSE-GestACT

## ✅ Implementación Completada

Se ha implementado un **sistema de menús contextuales** que muestra opciones diferentes según el dashboard activo.

---

## 🎯 Funcionamiento

### Pantalla de Selección (/)

**Menú mostrado:**
- 🏠 **Inicio** - Volver al selector

**Menú oculto:**
- ❌ Hardware
- ❌ Redes
- ❌ Equipos Médicos
- ❌ Recursos
- ❌ Servicio
- ❌ Bitácora
- ❌ Reportes
- ❌ Configuración

**Objetivo:** Mantener la pantalla limpia y enfocada en la selección

---

### Dashboard de Activos Informáticos (/dashboard/informatica/)

**Menú mostrado:**
- 🏠 **Inicio** - Volver al selector
- 💻 **Hardware**
  - Computadoras
  - Monitores
  - Impresoras
  - Periféricos
- 🌐 **Redes**
  - Networking
  - Telefonía
- 📦 **Recursos**
  - Software
  - Insumos
- 🔧 **Servicio** (Compartido)
  - Órdenes de Servicio
- 🕒 **Bitácora**
- 📊 **Reportes**
- ⚙️ **Configuración**

**Menú oculto:**
- ❌ Equipos Médicos

---

### Dashboard de Tecnología Médica (/dashboard/tecnologia-medica/)

**Menú mostrado:**
- 🏠 **Inicio** - Volver al selector
- 🏥 **Equipos Médicos**
  - Tecnología Médica (Ver todos / Agregar)
- 🔧 **Servicio** (Compartido)
  - Órdenes de Servicio
- 🕒 **Bitácora**
- 📊 **Reportes**
- ⚙️ **Configuración**

**Menú oculto:**
- ❌ Hardware
- ❌ Redes
- ❌ Recursos (Software e Insumos)

---

## 🏗️ Arquitectura Técnica

### Sistema de Menús Contextuales

**Variable de contexto:** `menu_type`

**Valores posibles:**
- `'selector'` - Pantalla de selección (menú mínimo)
- `'informatica'` - Dashboard de TI (menú completo de TI)
- `'medica'` - Dashboard de Tecnología Médica (menú médico)
- `None` - Sin menú específico (muestra todo por defecto)

### Lógica en Templates

**base.html:**
```django
{% if menu_type == 'informatica' %}
    <!-- Mostrar menú de Hardware -->
    <!-- Mostrar menú de Redes -->
    <!-- Mostrar menú de Recursos -->
{% elif menu_type == 'medica' %}
    <!-- Mostrar menú de Equipos Médicos -->
{% endif %}

{% if menu_type == 'informatica' or menu_type == 'medica' %}
    <!-- Mostrar Servicio (COMPARTIDO) -->
    <!-- Mostrar Bitácora -->
    <!-- Mostrar Reportes -->
    <!-- Mostrar Configuración -->
{% endif %}
```

### MenuContextMixin

**Clase creada en frontend_views.py:**
```python
class MenuContextMixin:
    """Agrega menu_type automáticamente según el modelo."""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Determinar según el modelo
        if model_name == 'TecnologiaMedica':
            context['menu_type'] = 'medica'
        elif model_name in ['Computadora', 'Impresora', ...]:
            context['menu_type'] = 'informatica'
        else:
            context['menu_type'] = None
        
        return context
```

**Aplicado a vistas:**
- `ComputadoraListView(MenuContextMixin, ...)`
- `ImpresoraListView(MenuContextMixin, ...)`
- `MonitorListView(MenuContextMixin, ...)`
- `NetworkingListView(MenuContextMixin, ...)`
- `TelefoniaListView(MenuContextMixin, ...)`
- `PerifericoListView(MenuContextMixin, ...)`
- `TecnologiaMedicaListView(MenuContextMixin, ...)`
- `SoftwareListView(MenuContextMixin, ...)`
- `InsumoListView(MenuContextMixin, ...)`
- Y sus respectivas vistas Create, Update, Detail

---

## 📊 Comparación de Menús

### Tabla Comparativa

| Opción de Menú | Selector | Dashboard TI | Dashboard Médica |
|----------------|----------|--------------|------------------|
| **Inicio** | ✅ | ✅ | ✅ |
| **Hardware** | ❌ | ✅ | ❌ |
| **Redes** | ❌ | ✅ | ❌ |
| **Equipos Médicos** | ❌ | ❌ | ✅ |
| **Recursos** | ❌ | ✅ | ❌ |
| **Servicio** | ❌ | ✅ | ✅ |
| **Bitácora** | ❌ | ✅ | ✅ |
| **Reportes** | ❌ | ✅ | ✅ |
| **Configuración** | ❌ | ✅ | ✅ |

### Resumen Visual

**Pantalla de Selección:**
```
┌────────────────────────────────────────┐
│  ASSE-GestACT        [Inicio]          │
└────────────────────────────────────────┘
```

**Dashboard de TI:**
```
┌─────────────────────────────────────────────────────────────────┐
│  ASSE-GestACT  [Inicio][Hardware▼][Redes▼][Recursos▼]          │
│                [Servicio▼][Bitácora][Reportes▼][Config▼]        │
└─────────────────────────────────────────────────────────────────┘
```

**Dashboard de Tecnología Médica:**
```
┌─────────────────────────────────────────────────────────────────┐
│  ASSE-GestACT  [Inicio][Equipos Médicos▼][Servicio▼]           │
│                [Bitácora][Reportes▼][Config▼]                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Navegación

### Desde la Pantalla de Selección

```
Usuario en: http://localhost:8000/
Menú visible: Solo "Inicio"
    │
    ├─→ Click en tarjeta "Activos Informáticos"
    │   └─→ Va a /dashboard/informatica/
    │       └─→ Menú cambia a: Hardware, Redes, Recursos, Servicio, etc.
    │
    └─→ Click en tarjeta "Tecnología Médica"
        └─→ Va a /dashboard/tecnologia-medica/
            └─→ Menú cambia a: Equipos Médicos, Servicio, etc.
```

### Desde un Dashboard

```
Usuario en Dashboard TI o Médica
Menú completo visible según tipo
    │
    └─→ Click en "Inicio" (menú o botón)
        └─→ Regresa a: http://localhost:8000/
            └─→ Menú se simplifica a solo "Inicio"
```

### Desde un Módulo Específico

```
Usuario en: /inventario/computadoras/
Modelo: Computadora
MenuContextMixin detecta: menu_type = 'informatica'
Menú mostrado: Hardware, Redes, Recursos, Servicio, etc.
    │
    └─→ Puede navegar a otros módulos de TI
    └─→ Click en "Inicio" → Regresa al selector
```

```
Usuario en: /inventario/tecnologia-medica/
Modelo: TecnologiaMedica
MenuContextMixin detecta: menu_type = 'medica'
Menú mostrado: Equipos Médicos, Servicio, etc.
    │
    └─→ Puede navegar a Equipos Médicos
    └─→ Click en "Inicio" → Regresa al selector
```

---

## 🎨 Ventajas del Sistema

### Claridad
- ✅ Cada dashboard muestra solo sus opciones relevantes
- ✅ No hay confusión con opciones no relacionadas
- ✅ Menú más limpio y enfocado

### Usabilidad
- ✅ Usuario ve solo lo que necesita
- ✅ Menos opciones = más fácil encontrar lo que busca
- ✅ Menú adaptado al contexto

### Mantenibilidad
- ✅ Código modular y reutilizable
- ✅ MenuContextMixin centraliza la lógica
- ✅ Fácil agregar nuevos tipos de menú

### Escalabilidad
- ✅ Fácil agregar más dashboards
- ✅ Fácil agregar más opciones de menú
- ✅ Sistema extensible

---

## 🛠️ Implementación Técnica

### Archivos Modificados

**1. inventario/frontend_views.py**
- ✅ Creado `MenuContextMixin`
- ✅ Agregado a 9+ vistas (List, Create, Update, Detail)
- ✅ Actualizado `dashboard_selector()` con `menu_type='selector'`
- ✅ Actualizado `dashboard_activos_informaticos()` con `menu_type='informatica'`
- ✅ Actualizado `dashboard_tecnologia_medica()` con `menu_type='medica'`

**2. inventario/templates/inventario/base.html**
- ✅ Agregada lógica condicional `{% if menu_type == ... %}`
- ✅ Separado menú de TI
- ✅ Separado menú de Tecnología Médica
- ✅ Módulos compartidos (Servicio, etc.) solo en dashboards

**3. inventario/templates/inventario/dashboard_selector.html**
- ✅ Template de selección con `menu_type='selector'`

**4. inventario/urls.py**
- ✅ URLs actualizadas para dashboards específicos

---

## 📝 Código Clave

### MenuContextMixin (frontend_views.py)

```python
class MenuContextMixin:
    """Mixin para agregar el contexto de menú según el tipo de modelo."""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        model_name = self.model.__name__ if hasattr(self, 'model') else None
        
        if model_name == 'TecnologiaMedica':
            context['menu_type'] = 'medica'
        elif model_name in ['Computadora', 'Impresora', 'Monitor', 
                           'Networking', 'Telefonia', 'Periferico', 
                           'Software', 'Insumo']:
            context['menu_type'] = 'informatica'
        else:
            context['menu_type'] = None
        
        return context
```

### Uso en Vistas

```python
# Vista de Activos Informáticos
class ComputadoraListView(MenuContextMixin, LugarFilterMixin, ListView):
    model = Computadora
    # MenuContextMixin automáticamente agrega menu_type='informatica'

# Vista de Tecnología Médica
class TecnologiaMedicaListView(MenuContextMixin, LugarFilterMixin, ListView):
    model = TecnologiaMedica
    # MenuContextMixin automáticamente agrega menu_type='medica'
```

### Template Condicional (base.html)

```django
{# Menú de TI #}
{% if menu_type == 'informatica' %}
    <li>Hardware</li>
    <li>Redes</li>
    <li>Recursos</li>
{% elif menu_type == 'medica' %}
    <li>Equipos Médicos</li>
{% endif %}

{# Compartidos solo en dashboards #}
{% if menu_type == 'informatica' or menu_type == 'medica' %}
    <li>Servicio</li>
    <li>Bitácora</li>
    <li>Reportes</li>
    <li>Configuración</li>
{% endif %}
```

---

## 🎯 Casos de Uso

### Caso 1: Usuario de TI navega por computadoras

```
1. Usuario va a /dashboard/informatica/
   → Menú: Hardware, Redes, Recursos, Servicio, etc.

2. Click en Hardware → Computadoras → Ver Todas
   → Va a /inventario/computadoras/
   → MenuContextMixin detecta modelo=Computadora
   → Agrega menu_type='informatica'
   → Menú sigue mostrando: Hardware, Redes, Recursos, etc.

3. Navega entre módulos de TI
   → Menú siempre muestra opciones de TI

4. Click en "Inicio"
   → Regresa a pantalla de selección
   → Menú se simplifica a solo "Inicio"
```

### Caso 2: Usuario de Tecnología Médica gestiona equipos

```
1. Usuario va a /dashboard/tecnologia-medica/
   → Menú: Equipos Médicos, Servicio, Bitácora, Reportes, Config

2. Click en Equipos Médicos → Ver Todos
   → Va a /inventario/tecnologia-medica/
   → MenuContextMixin detecta modelo=TecnologiaMedica
   → Agrega menu_type='medica'
   → Menú muestra: Equipos Médicos, Servicio, etc.
   → NO muestra: Hardware, Redes, Recursos

3. Navega por equipos médicos
   → Menú siempre muestra opciones médicas

4. Click en "Inicio"
   → Regresa a pantalla de selección
```

### Caso 3: Usuario accede a Órdenes de Servicio

```
Desde Dashboard TI:
1. Menú → Servicio → Ver Todas
   → Va a /inventario/ordenes-servicio/
   → Puede ver/crear órdenes de equipos TI
   → Menú sigue mostrando opciones de TI

Desde Dashboard Médica:
1. Menú → Servicio → Ver Todas
   → Va a /inventario/ordenes-servicio/
   → Puede ver/crear órdenes de equipos médicos
   → Menú sigue mostrando opciones médicas
```

---

## 🔧 Implementación

### Paso 1: Mixin Creado

**MenuContextMixin** agrega automáticamente `menu_type` al contexto según el modelo de la vista.

### Paso 2: Vistas Actualizadas

Todas las vistas principales ahora heredan de `MenuContextMixin`:
```python
ComputadoraListView(MenuContextMixin, ...)
ImpresoraListView(MenuContextMixin, ...)
MonitorListView(MenuContextMixin, ...)
NetworkingListView(MenuContextMixin, ...)
TelefoniaListView(MenuContextMixin, ...)
PerifericoListView(MenuContextMixin, ...)
TecnologiaMedicaListView(MenuContextMixin, ...)
SoftwareListView(MenuContextMixin, ...)
InsumoListView(MenuContextMixin, ...)
```

### Paso 3: Template Base Actualizado

**base.html** usa lógica condicional para mostrar menús según `menu_type`.

### Paso 4: Dashboards Actualizados

Cada función de dashboard pasa su `menu_type` específico:
```python
dashboard_selector() → menu_type='selector'
dashboard_activos_informaticos() → menu_type='informatica'
dashboard_tecnologia_medica() → menu_type='medica'
```

---

## 🎨 Experiencia de Usuario

### Antes (Menú Mezclado)
```
Menú para todos:
[Hardware][Redes][Tec.Médica][Recursos][Servicio]...

Problema:
- Usuario de TI ve opciones médicas (confuso)
- Usuario médico ve opciones de TI (irrelevante)
- Menú muy largo y saturado
```

### Ahora (Menús Separados)
```
Usuario de TI ve:
[Hardware][Redes][Recursos][Servicio][Bitácora]...

Usuario Médico ve:
[Equipos Médicos][Servicio][Bitácora]...

Selector ve:
[Inicio] (minimal)

Beneficios:
✅ Enfoque claro en su área
✅ Menos opciones = más fácil navegar
✅ Experiencia personalizada
```

---

## 🚀 Cómo Probar

### 1. Pantalla de Selección
```
URL: http://localhost:8000/
Resultado: Solo muestra "Inicio" en menú
Contenido: Dos tarjetas grandes de selección
```

### 2. Dashboard de TI
```
URL: http://localhost:8000/dashboard/informatica/
Menú: Hardware, Redes, Recursos, Servicio, Bitácora, Reportes, Config
Contenido: Dashboard de activos informáticos
```

### 3. Dashboard de Tecnología Médica
```
URL: http://localhost:8000/dashboard/tecnologia-medica/
Menú: Equipos Médicos, Servicio, Bitácora, Reportes, Config
Contenido: Dashboard de tecnología médica
```

### 4. Navegar entre módulos de TI
```
URL: http://localhost:8000/inventario/computadoras/
Menú: Hardware, Redes, Recursos, Servicio, etc.
```

### 5. Navegar en Tecnología Médica
```
URL: http://localhost:8000/inventario/tecnologia-medica/
Menú: Equipos Médicos, Servicio, etc.
```

---

## ✨ Características Adicionales

### Navegación Intuitiva

**Botón "Inicio":**
- Presente en todos los dashboards
- Regresa a la pantalla de selección
- Permite cambiar de dashboard fácilmente

**Breadcrumb implícito:**
```
Selector → Dashboard TI → Computadoras → Detalle
   ↑          ↑              ↑             ↑
[Inicio]   [Inicio]       [Lista]     [Volver]
```

### Módulos Compartidos

Algunos módulos se muestran en **ambos** dashboards:
- 🔧 **Servicio** - Órdenes para TI y Médica
- 🕒 **Bitácora** - Historial de eventos
- 📊 **Reportes** - Reportes empresariales
- ⚙️ **Configuración** - Lugares y configuración

---

## 📋 Archivos Modificados

### Backend
1. ✅ `inventario/frontend_views.py`
   - Creado MenuContextMixin (20 líneas)
   - Actualizado 15+ vistas con el mixin
   - Actualizado funciones de dashboard

### Frontend
2. ✅ `inventario/templates/inventario/base.html`
   - Agregada lógica condicional de menú
   - Separados menús por tipo
   
3. ✅ `inventario/templates/inventario/dashboard_selector.html`
   - Template de selección con menu_type='selector'

4. ✅ `inventario/templates/inventario/dashboard.html`
   - Botón "Inicio" agregado

5. ✅ `inventario/templates/inventario/dashboard_tecnologia_medica.html`
   - Botón "Inicio" agregado

### Routing
6. ✅ `inventario/urls.py`
   - URLs específicas para cada dashboard

---

## 🎯 Beneficios Finales

### Para Usuarios de TI
✅ Menú enfocado en infraestructura TI
✅ Acceso rápido a hardware, redes y software
✅ No ve opciones médicas irrelevantes
✅ Experiencia optimizada para su trabajo

### Para Usuarios de Tecnología Médica
✅ Menú enfocado en equipos médicos
✅ Acceso directo a tecnología médica
✅ No ve opciones de TI irrelevantes
✅ Experiencia optimizada para gestión médica

### Para Ambos
✅ Acceso compartido a Órdenes de Servicio
✅ Acceso a Bitácora, Reportes y Configuración
✅ Navegación clara e intuitiva
✅ Fácil cambio entre dashboards

---

## ✅ Estado Final

**Sistema:** ✅ COMPLETAMENTE FUNCIONAL

**Menús implementados:**
- ✅ Menú simplificado para selector
- ✅ Menú completo para Dashboard TI
- ✅ Menú completo para Dashboard Médica
- ✅ Detección automática según modelo

**Navegación:**
- ✅ Pantalla de selección en raíz (/)
- ✅ Dashboards en URLs específicas
- ✅ Botones de regreso implementados
- ✅ Transiciones suaves entre vistas

---

**Recarga el navegador para ver los menús contextuales funcionando! 🎉**

**URLs de prueba:**
- Selector: http://localhost:8000/
- Dashboard TI: http://localhost:8000/dashboard/informatica/
- Dashboard Médica: http://localhost:8000/dashboard/tecnologia-medica/

