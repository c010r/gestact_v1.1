# 🏥 Módulo de Tecnología Médica y Servicio - ASSE-GestACT

## ✅ Implementación Completada

Se han implementado dos módulos principales en el sistema ASSE-GestACT:

1. **Módulo de Tecnología Médica** - Gestión de equipos médicos
2. **Módulo de Servicio** - Gestión de órdenes de servicio y mantenimiento (compartido entre TI y Tecnología Médica)

---

## 🏥 Módulo de Tecnología Médica

### Características Principales

#### 📋 Campos Específicos
- **Registro Sanitario** - Número de registro ante autoridad sanitaria
- **Número de Activo Fijo** - Código contable
- **Clasificación de Riesgo** - Clase I a IV según normativa médica
- **Área de Aplicación** - UCI, Quirófano, Emergencia, etc.
- **Calibración Periódica** - Frecuencia y última calibración
- **Mantenimiento Preventivo** - Frecuencia y último mantenimiento
- **Especificaciones Técnicas** - Voltaje, potencia
- **Personal Especializado** - Indicador si requiere personal capacitado

#### 🎯 Funcionalidades
- ✅ CRUD completo de equipos médicos
- ✅ Alertas automáticas de calibración próxima (30 días)
- ✅ Alertas automáticas de mantenimiento próximo (30 días)
- ✅ Dashboard especializado con gráficos
- ✅ Clasificación visual por riesgo con colores
- ✅ Integración con bitácora
- ✅ Gestión de garantías
- ✅ Números de inventario automáticos

#### 📊 Dashboard de Tecnología Médica

**Estadísticas:**
- Total de equipos médicos
- Equipos activos
- Equipos críticos (Clase III y IV)
- Alertas pendientes (calibración + mantenimiento)

**Gráficos:**
- Distribución por clasificación de riesgo
- Equipos por tipo (Top 10)
- Equipos por estado

**Tablas de Alertas:**
- Equipos que requieren calibración
- Equipos que requieren mantenimiento

**Actividad:**
- Equipos registrados recientemente
- Bitácora específica de tecnología médica

#### 📍 URLs
- **Listado:** `/inventario/tecnologia-medica/`
- **Crear:** `/inventario/tecnologia-medica/crear/`
- **Detalle:** `/inventario/tecnologia-medica/<id>/`
- **Editar:** `/inventario/tecnologia-medica/<id>/editar/`
- **API:** `/inventario/api/tecnologia-medica/`

#### 🏷️ Tipos de Equipos Médicos Precargados
1. Ventilador Mecánico
2. Monitor de Paciente
3. Desfibrilador
4. Bomba de Infusión
5. Electrocardiógrafo
6. Oxímetro
7. Incubadora
8. Equipo de Rayos X
9. Ecógrafo
10. Autoclave

---

## 🔧 Módulo de Servicio (Órdenes de Servicio)

### Características Principales

#### 📋 Información de la Orden
- **Número de Orden Automático** - Formato: OS-YYYYMMDD-####
- **Tipo de Servicio:**
  - Mantenimiento Preventivo
  - Mantenimiento Correctivo
  - Reparación
  - Calibración
  - Instalación
  - Actualización
  - Diagnóstico
  - Limpieza
  - Otro

#### 🎨 Estados de la Orden
- ⏳ **Pendiente** - Recién creada
- ⚙️ **En Proceso** - Técnico trabajando
- ⏸️ **En Espera de Repuesto** - Esperando materiales
- ✅ **Completada** - Servicio finalizado
- ❌ **Cancelada** - Orden cancelada

#### ⚡ Niveles de Prioridad
- 🟢 **Baja**
- 🔵 **Media**
- 🟡 **Alta**
- 🔴 **Crítica**

#### 📝 Gestión Completa
- Descripción del problema
- Diagnóstico técnico
- Solución aplicada
- Repuestos utilizados
- Costos (mano de obra + repuestos)
- Fechas (solicitud, inicio, finalización, estimada)
- Asignación de técnico
- Solicitante

#### 🎯 Funcionalidades
- ✅ Aplica a **TODOS** los tipos de dispositivos:
  - Computadoras
  - Impresoras
  - Monitores
  - Networking
  - Telefonía
  - Periféricos
  - **Tecnología Médica**
  - Insumos
  - Software

- ✅ Alertas de órdenes vencidas
- ✅ Seguimiento de tiempo de resolución
- ✅ Cálculo automático de costos totales
- ✅ Filtros avanzados (estado, prioridad, tipo, dispositivo)
- ✅ Integración con bitácora automática
- ✅ Endpoints especializados:
  - `/api/ordenes-servicio/pendientes/`
  - `/api/ordenes-servicio/en_proceso/`
  - `/api/ordenes-servicio/vencidas/`
  - `/api/ordenes-servicio/por_dispositivo/`

#### 📍 URLs
- **Listado:** `/inventario/ordenes-servicio/`
- **Crear:** `/inventario/ordenes-servicio/crear/`
- **Detalle:** `/inventario/ordenes-servicio/<id>/`
- **Editar:** `/inventario/ordenes-servicio/<id>/editar/`
- **API:** `/inventario/api/ordenes-servicio/`

#### 🔄 Acciones Especiales
- **Iniciar Orden:** POST `/api/ordenes-servicio/<id>/iniciar/`
- **Completar Orden:** POST `/api/ordenes-servicio/<id>/completar/`

---

## 👥 Sistema de Dashboards por Rol

### 🔐 Carga Automática según Grupo de Usuario

El sistema detecta automáticamente qué dashboard mostrar:

#### 🖥️ Dashboard de Activos Informáticos
**Para usuarios del grupo:** "Activos Informáticos"

**Muestra:**
- Computadoras, Impresoras, Monitores
- Networking, Telefonía, Periféricos
- Software, Insumos TI
- **Órdenes de Servicio** de dispositivos TI

#### 🏥 Dashboard de Tecnología Médica
**Para usuarios del grupo:** "Tecnología Médica"

**Muestra:**
- Equipos médicos
- Alertas de calibración y mantenimiento
- Clasificación de riesgo
- **Órdenes de Servicio** de equipos médicos

### 🎯 Reglas de Asignación

```
Usuario con grupo "Tecnología Médica" → Dashboard de Tecnología Médica
Usuario con grupo "Activos Informáticos" → Dashboard de Activos Informáticos
Usuario sin grupo → Dashboard de Activos Informáticos (predeterminado)
Superusuario → Puede usar ?type=medica o ?type=informatica para cambiar
```

### 👥 Usuarios de Prueba Creados

#### 👨‍💻 Usuario TI:
- **Username:** `demo_ti`
- **Password:** `demo123`
- **Grupo:** Activos Informáticos
- **Dashboard:** Activos Informáticos

#### 👨‍⚕️ Usuario Tecnología Médica:
- **Username:** `demo_medica`
- **Password:** `demo123`
- **Grupo:** Tecnología Médica
- **Dashboard:** Tecnología Médica

---

## 🔧 Módulo de Servicio - Acceso Compartido

### 🔗 Accesible desde Ambos Departamentos

El módulo de **Órdenes de Servicio** está disponible para:
- ✅ **Personal de TI** - Gestiona mantenimiento de equipos informáticos
- ✅ **Personal de Tecnología Médica** - Gestiona mantenimiento de equipos médicos

### 📊 Casos de Uso

#### Ejemplo 1: Personal de TI
1. Recibe solicitud de reparación de computadora
2. Crea orden de servicio tipo "Reparación"
3. Asigna técnico
4. Registra diagnóstico y solución
5. Completa orden con costos
6. Sistema actualiza bitácora automáticamente

#### Ejemplo 2: Personal de Tecnología Médica
1. Sistema alerta que ventilador requiere calibración
2. Crea orden de servicio tipo "Calibración"
3. Asigna técnico especializado
4. Registra fecha de calibración realizada
5. Completa orden
6. Sistema actualiza bitácora y fecha de última calibración

---

## 📱 Navegación del Sistema

### Menú Principal (Barra de Navegación)

**Disponible para todos:**
1. 🏠 **Inicio** - Dashboard (según rol)
2. 💻 **Hardware** - Computadoras, Monitores, Impresoras, Periféricos
3. 🌐 **Redes** - Networking, Telefonía
4. 🏥 **Tecnología Médica** - Equipos médicos
5. 🔧 **Servicio** - Órdenes de servicio (¡NUEVO!)
6. 📦 **Recursos** - Software, Insumos
7. 📊 **Reportes** - Reportes empresariales
8. 📋 **Facturación** - Remitos
9. ⚙️ **Configuración** - Lugares y configuración

---

## 🚀 Cómo Usar el Sistema

### 1️⃣ Iniciar Sesión
```
URL: http://localhost:8000/admin/
Usuario TI: demo_ti / demo123
Usuario Médica: demo_medica / demo123
```

### 2️⃣ Ver Dashboard
```
URL: http://localhost:8000/
Muestra automáticamente el dashboard según tu grupo
```

### 3️⃣ Crear Orden de Servicio
```
Menú → Servicio → Nueva Orden
o
URL directa: http://localhost:8000/inventario/ordenes-servicio/crear/
```

### 4️⃣ Gestionar Tecnología Médica
```
Menú → Tecnología Médica → Ver Todos
o
URL directa: http://localhost:8000/inventario/tecnologia-medica/
```

---

## 🛠️ Herramientas de Administración

### Script de Gestión de Usuarios
```bash
python gestionar_usuarios.py
```

Permite:
- Crear usuarios
- Asignar a grupos (TI o Tecnología Médica)
- Listar usuarios y grupos
- Cambiar asignaciones

### Comandos Rápidos

**Crear usuario de TI:**
```bash
python manage.py shell -c "
from django.contrib.auth.models import User, Group
user = User.objects.create_user('nombre.usuario', password='contraseña')
user.groups.add(Group.objects.get(name='Activos Informáticos'))
"
```

**Crear usuario de Tecnología Médica:**
```bash
python manage.py shell -c "
from django.contrib.auth.models import User, Group
user = User.objects.create_user('nombre.usuario', password='contraseña')
user.groups.add(Group.objects.get(name='Tecnología Médica'))
"
```

**Listar usuarios y grupos:**
```bash
python manage.py shell -c "
from django.contrib.auth.models import User
for user in User.objects.all():
    grupos = ', '.join([g.name for g in user.groups.all()]) or 'Sin grupo'
    print(f'{user.username}: {grupos}')
"
```

---

## 📊 Estadísticas del Sistema

### Base de Datos
- ✅ 20 migraciones aplicadas
- ✅ 2 grupos de usuarios creados
- ✅ 2 usuarios de prueba creados
- ✅ 10 tipos de tecnología médica creados
- ✅ Todas las tablas creadas correctamente

### Modelos Implementados
- ✅ `TipoTecnologiaMedica` - Tipos de equipos médicos
- ✅ `TecnologiaMedica` - Equipos médicos con campos especializados
- ✅ `OrdenServicio` - Órdenes de servicio y mantenimiento

### APIs REST Disponibles
- `/api/tecnologia-medica/` - CRUD completo
- `/api/tecnologia-medica/requieren_calibracion/` - Equipos a calibrar
- `/api/tecnologia-medica/requieren_mantenimiento/` - Equipos a mantener
- `/api/ordenes-servicio/` - CRUD completo
- `/api/ordenes-servicio/pendientes/` - Órdenes pendientes
- `/api/ordenes-servicio/en_proceso/` - Órdenes en proceso
- `/api/ordenes-servicio/vencidas/` - Órdenes vencidas
- `/api/ordenes-servicio/por_dispositivo/` - Por dispositivo específico

---

## 🎨 Interfaz de Usuario

### Dashboards

#### Dashboard de Activos Informáticos
- Tarjetas de estadísticas por tipo de equipo
- Gráficos de distribución
- Alertas de garantías
- Restock de insumos
- Actividad reciente
- Acceso a: Hardware, Redes, Software, Insumos, **Servicio**

#### Dashboard de Tecnología Médica
- Tarjetas de estadísticas médicas
- Equipos críticos (Clase III/IV)
- Gráficos de clasificación de riesgo
- Gráficos de equipos por tipo
- **Alertas de calibración** (próximos 30 días)
- **Alertas de mantenimiento** (próximos 30 días)
- Equipos recientes
- Bitácora especializada
- Acceso a: Equipos Médicos, **Servicio**

### Menú de Navegación

Menús disponibles en la barra superior:
1. **Inicio** - Dashboard
2. **Hardware** - Computadoras, Monitores, Impresoras, Periféricos
3. **Redes** - Networking, Telefonía
4. **Tecnología Médica** - Equipos médicos
5. **Servicio** - Órdenes de servicio ⭐ (COMPARTIDO)
6. **Recursos** - Software, Insumos
7. **Reportes** - Reportes
8. **Facturación** - Remitos
9. **Configuración** - Lugares

---

## 🔄 Flujo de Trabajo

### Flujo de Servicio para TI

1. **Recepción de solicitud**
   - Usuario solicita reparación de computadora
   - Personal TI crea orden de servicio

2. **Asignación**
   - Se asigna técnico
   - Se establece prioridad

3. **Ejecución**
   - Técnico inicia orden (estado → En Proceso)
   - Registra diagnóstico
   - Aplica solución

4. **Cierre**
   - Registra repuestos utilizados
   - Registra costos
   - Completa orden
   - Sistema actualiza bitácora automáticamente

### Flujo de Servicio para Tecnología Médica

1. **Alerta automática**
   - Sistema detecta que ventilador requiere calibración en 15 días
   - Aparece en dashboard como alerta

2. **Creación de orden**
   - Personal médico crea orden tipo "Calibración"
   - Prioridad: Alta (por ser equipo crítico)

3. **Ejecución**
   - Se asigna técnico biomédico
   - Se registra fecha de calibración
   - Se actualiza certificado

4. **Cierre**
   - Se completa orden
   - Se actualiza "fecha_ultima_calibracion" del equipo
   - Sistema recalcula próxima alerta

---

## 📈 Mejoras Implementadas

### Integración Completa
- ✅ Bitácora automática en todos los eventos
- ✅ Números automáticos (inventario, órdenes)
- ✅ Cálculos automáticos (garantías, calibración, costos)
- ✅ Validaciones robustas
- ✅ Filtros avanzados en todas las vistas
- ✅ Paginación optimizada
- ✅ Búsqueda semántica

### Alertas Inteligentes
- ✅ Calibración próxima (30 días)
- ✅ Mantenimiento próximo (30 días)
- ✅ Garantías por vencer (30 días)
- ✅ Órdenes vencidas
- ✅ Equipos críticos sin mantenimiento

---

## 📚 Documentación Creada

1. **SISTEMA_DASHBOARDS_POR_ROL.md** - Documentación técnica completa
2. **GUIA_DASHBOARDS_ROL.md** - Guía rápida de uso
3. **MODULO_TECNOLOGIA_MEDICA_Y_SERVICIO.md** - Este documento (resumen completo)

---

## 🎓 Capacitación Recomendada

### Para Personal de TI
1. Gestión de activos informáticos
2. Creación de órdenes de servicio para equipos TI
3. Seguimiento de mantenimientos
4. Gestión de repuestos e insumos

### Para Personal de Tecnología Médica
1. Registro de equipos médicos
2. Clasificación de riesgo
3. Gestión de calibraciones
4. Mantenimiento preventivo
5. Órdenes de servicio para equipos médicos
6. Cumplimiento normativo

### Para Ambos
1. Sistema de órdenes de servicio compartido
2. Navegación entre módulos
3. Generación de reportes
4. Uso de la bitácora
5. Sistema de facturación/remitos

---

## ✨ Próximos Pasos Recomendados

1. ✅ **Probar el sistema** con los usuarios demo
2. ✅ **Crear usuarios reales** para cada departamento
3. ✅ **Registrar equipos médicos** reales
4. ✅ **Crear órdenes de servicio** de prueba
5. ✅ **Capacitar usuarios** en el uso del sistema
6. ⏭️ **Configurar alertas por email** (futuro)
7. ⏭️ **Reportes especializados** por departamento (futuro)
8. ⏭️ **App móvil** para técnicos en campo (futuro)

---

## 🎯 Resumen Ejecutivo

### Lo que se logró:
- ✅ Sistema completo de gestión de tecnología médica
- ✅ Sistema unificado de órdenes de servicio
- ✅ Dashboards especializados por rol
- ✅ Carga automática según grupo de usuario
- ✅ Alertas inteligentes de calibración y mantenimiento
- ✅ Trazabilidad completa con bitácora
- ✅ Cumplimiento normativo (clasificación de riesgo, registro sanitario)

### Beneficios:
- 🎯 **Especialización** - Cada departamento ve lo que necesita
- 🔧 **Unificación** - Servicio compartido entre departamentos
- 📊 **Visibilidad** - Dashboards con métricas relevantes
- ⚡ **Eficiencia** - Automatización de alertas y cálculos
- 📋 **Cumplimiento** - Registro sanitario y clasificación de riesgo
- 🔍 **Trazabilidad** - Bitácora automática de todos los eventos

---

## 🚀 Estado del Sistema

**Sistema:** ✅ **FUNCIONANDO**

**Servidor:** 🟢 Ejecutándose en http://localhost:8000/

**Base de Datos:** ✅ Todas las migraciones aplicadas

**Módulos Activos:**
- ✅ Activos Informáticos (Computadoras, Impresoras, Monitores, etc.)
- ✅ Tecnología Médica (Equipos médicos)
- ✅ Órdenes de Servicio (Compartido)
- ✅ Networking y Telefonía
- ✅ Software e Insumos
- ✅ Facturación y Remitos
- ✅ Reportes
- ✅ Bitácora

---

## 📞 Soporte

Para cualquier duda o problema:
1. Revisar la documentación incluida
2. Consultar el código fuente (comentado)
3. Usar el script `gestionar_usuarios.py` para administración de usuarios
4. Contactar al equipo de desarrollo

---

**Implementación realizada el:** 31 de Octubre, 2025
**Versión del sistema:** 2.0 - Módulos de Tecnología Médica y Servicio

