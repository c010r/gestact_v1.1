# Sistema de Dashboards por Rol de Usuario

## 📋 Descripción

El sistema ASSE-GestACT ahora cuenta con **dashboards separados** que se muestran automáticamente según el **rol/grupo** del usuario:

### 🖥️ Dashboard de Activos Informáticos
- **Para:** Personal de TI
- **Muestra:** Computadoras, Impresoras, Monitores, Networking, Telefonía, Periféricos, Software, Insumos TI

### 🏥 Dashboard de Tecnología Médica  
- **Para:** Personal de tecnología médica/biomédica
- **Muestra:** Equipos médicos, alertas de calibración, mantenimiento, clasificación de riesgo

---

## 🎯 Cómo Funciona

### Detección Automática por Grupo

El sistema detecta automáticamente el grupo al que pertenece el usuario:

1. **Usuario con grupo "Tecnología Médica"** → Dashboard de Tecnología Médica
2. **Usuario con grupo "Activos Informáticos" o "TI"** → Dashboard de Activos Informáticos
3. **Usuario sin grupo específico** → Dashboard de Activos Informáticos (por defecto)
4. **Usuario no autenticado** → Dashboard de Activos Informáticos (por defecto)

### Override Manual (Opcional)

Los usuarios pueden cambiar manualmente entre dashboards usando la URL:
- `http://localhost:8000/?type=informatica` - Dashboard de TI
- `http://localhost:8000/?type=medica` - Dashboard de Tecnología Médica

O usando los botones en la parte superior del dashboard.

---

## 👥 Gestión de Usuarios y Grupos

### Crear Usuario y Asignar Grupo

#### Opción 1: Desde el Admin de Django

1. Acceder al admin: `http://localhost:8000/admin/`
2. Ir a **Autenticación y Autorización** → **Usuarios**
3. Crear o editar un usuario
4. En la sección **Permisos**, buscar **grupos**
5. Seleccionar el grupo correspondiente:
   - **Activos Informáticos** - Para personal de TI
   - **Tecnología Médica** - Para personal de tecnología médica

#### Opción 2: Desde Python Shell

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User, Group

# Crear usuario
usuario = User.objects.create_user(
    username='juan.perez',
    email='juan.perez@asse.gub.uy',
    password='password123',
    first_name='Juan',
    last_name='Pérez'
)

# Asignar al grupo de Tecnología Médica
grupo_medica = Group.objects.get(name='Tecnología Médica')
usuario.groups.add(grupo_medica)

print(f'Usuario {usuario.username} creado y asignado a {grupo_medica.name}')
```

#### Opción 3: Script Automatizado

```bash
# Crear usuario de TI
python manage.py shell -c "
from django.contrib.auth.models import User, Group
user = User.objects.create_user('maria.lopez', 'maria@asse.gub.uy', 'pass123')
user.groups.add(Group.objects.get(name='Activos Informáticos'))
print('Usuario de TI creado: maria.lopez')
"

# Crear usuario de Tecnología Médica
python manage.py shell -c "
from django.contrib.auth.models import User, Group
user = User.objects.create_user('carlos.garcia', 'carlos@asse.gub.uy', 'pass123')
user.groups.add(Group.objects.get(name='Tecnología Médica'))
print('Usuario de Tecnología Médica creado: carlos.garcia')
"
```

---

## 🔐 Grupos Disponibles

El sistema incluye dos grupos predefinidos:

1. **Activos Informáticos**
   - Dashboard: Gestión de activos TI
   - Acceso a: Computadoras, Impresoras, Monitores, Networking, Telefonía, Periféricos, Software

2. **Tecnología Médica**
   - Dashboard: Gestión de equipos médicos
   - Acceso a: Equipos médicos, alertas de calibración, mantenimiento preventivo, clasificación de riesgo

---

## 📊 Características de cada Dashboard

### Dashboard de Activos Informáticos

- Total de activos TI
- Activos activos/inactivos
- Gráficos de distribución por tipo
- Alertas de garantías próximas a vencer
- Restock de insumos
- Bitácora de actividad
- Licencias de software

### Dashboard de Tecnología Médica

- Total de equipos médicos
- Equipos activos y críticos (Clase III/IV)
- **Alertas de calibración** (equipos que requieren calibración en 30 días)
- **Alertas de mantenimiento preventivo** (equipos que requieren mantenimiento en 30 días)
- Gráfico de clasificación de riesgo (Clase I-IV)
- Gráfico de equipos por tipo
- Equipos recientes
- Bitácora específica de tecnología médica

---

## 🛠️ Administración

### Ver Usuarios y sus Grupos

```bash
python manage.py shell -c "
from django.contrib.auth.models import User
for user in User.objects.all():
    grupos = ', '.join([g.name for g in user.groups.all()])
    print(f'{user.username}: {grupos or \"Sin grupo\"}')
"
```

### Cambiar Grupo de un Usuario

```bash
python manage.py shell -c "
from django.contrib.auth.models import User, Group
user = User.objects.get(username='nombre_usuario')
user.groups.clear()  # Limpiar grupos anteriores
user.groups.add(Group.objects.get(name='Tecnología Médica'))
print(f'Usuario {user.username} ahora está en Tecnología Médica')
"
```

### Ver Todos los Grupos

```bash
python manage.py shell -c "
from django.contrib.auth.models import Group
for group in Group.objects.all():
    usuarios = group.user_set.count()
    print(f'{group.name}: {usuarios} usuarios')
"
```

---

## 🎨 Personalización Futura

El sistema está diseñado para ser fácilmente extensible:

1. **Agregar más grupos:** Se pueden crear grupos adicionales (ej: "Administración", "Mantenimiento")
2. **Dashboards personalizados:** Cada grupo puede tener su propio dashboard específico
3. **Permisos granulares:** Se pueden agregar permisos específicos por grupo
4. **Dashboard predeterminado por usuario:** Se puede guardar la preferencia de dashboard en el perfil del usuario

---

## 📝 Notas Importantes

1. **Prioridad:** Si un usuario pertenece a múltiples grupos, se prioriza "Tecnología Médica" sobre "Activos Informáticos"
2. **Acceso manual:** Los usuarios pueden cambiar de dashboard usando los botones del selector en la parte superior
3. **Sin restricciones:** Actualmente, todos los usuarios pueden acceder a ambos dashboards, solo cambia cuál se muestra por defecto
4. **Permisos futuros:** Se pueden agregar permisos específicos para restringir el acceso a ciertos módulos según el grupo

---

## 🚀 Casos de Uso

### Caso 1: Hospital con Departamento de TI y Biomédica

- **Personal de TI:** Asignado a grupo "Activos Informáticos"
  - Ve computadoras, impresoras, switches, etc.
  - Dashboard optimizado para gestión de infraestructura TI

- **Personal de Biomédica:** Asignado a grupo "Tecnología Médica"
  - Ve ventiladores, monitores de pacientes, desfibriladores, etc.
  - Dashboard optimizado para calibración y mantenimiento

### Caso 2: Centro de Salud Pequeño

- **Administrador general:** Sin grupo específico o ambos grupos
  - Dashboard de TI por defecto
  - Puede cambiar manualmente al dashboard de Tecnología Médica

---

## ✅ Verificación

Para verificar que el sistema está funcionando correctamente:

1. Crear dos usuarios de prueba:
```bash
# Usuario de TI
python manage.py shell -c "
from django.contrib.auth.models import User, Group
user_ti = User.objects.create_user('test_ti', password='test123')
user_ti.groups.add(Group.objects.get(name='Activos Informáticos'))
print('Usuario test_ti creado (Activos Informáticos)')
"

# Usuario de Tecnología Médica
python manage.py shell -c "
from django.contrib.auth.models import User, Group
user_med = User.objects.create_user('test_medica', password='test123')
user_med.groups.add(Group.objects.get(name='Tecnología Médica'))
print('Usuario test_medica creado (Tecnología Médica)')
"
```

2. Iniciar sesión con cada usuario y verificar qué dashboard se muestra automáticamente

3. Probar el cambio manual entre dashboards usando los botones

---

## 📞 Soporte

Para más información o soporte, contactar al equipo de desarrollo.

