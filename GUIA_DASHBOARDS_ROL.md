# 🏥 Guía Rápida: Dashboards por Rol de Usuario

## ¿Cómo Funciona?

El sistema ahora detecta **automáticamente** qué dashboard mostrar según el **grupo** al que pertenece el usuario.

---

## 👥 Grupos Disponibles

### 1. **Activos Informáticos** (TI)
- Dashboard: Gestión de infraestructura TI
- Ve: Computadoras, Impresoras, Monitores, Networking, etc.

### 2. **Tecnología Médica** (Biomédica)
- Dashboard: Gestión de equipos médicos
- Ve: Ventiladores, Monitores de Pacientes, Desfibriladores, etc.
- **Alertas especiales:** Calibración y mantenimiento

---

## 🚀 Probar el Sistema

### Usuarios de Prueba Creados

He creado dos usuarios de demostración:

#### 👨‍💻 Usuario de TI:
- **Usuario:** `demo_ti`
- **Contraseña:** `demo123`
- **Dashboard:** Activos Informáticos

#### 👨‍⚕️ Usuario de Tecnología Médica:
- **Usuario:** `demo_medica`
- **Contraseña:** `demo123`
- **Dashboard:** Tecnología Médica

### Cómo Probar:

1. **Acceder al login:** http://localhost:8000/admin/
2. **Iniciar sesión** con uno de los usuarios de prueba
3. **Ir al dashboard:** http://localhost:8000/
4. **Verificar:** Verás automáticamente el dashboard correspondiente a tu grupo

---

## 🔧 Gestionar Usuarios

### Opción 1: Script Interactivo (Recomendado)

```bash
python gestionar_usuarios.py
```

Este script permite:
- ✅ Crear usuarios
- ✅ Asignar a grupos
- ✅ Listar usuarios
- ✅ Cambiar grupos
- ✅ Ver estadísticas

### Opción 2: Desde el Admin de Django

1. Ir a: http://localhost:8000/admin/
2. **Autenticación y Autorización** → **Usuarios**
3. Crear o editar usuario
4. En **grupos**, seleccionar:
   - **Activos Informáticos** (para personal de TI)
   - **Tecnología Médica** (para personal de biomédica)
5. Guardar

### Opción 3: Desde la Consola

```bash
# Crear usuario de TI
python manage.py shell -c "
from django.contrib.auth.models import User, Group
user = User.objects.create_user('nombre.apellido', password='contraseña123')
user.groups.add(Group.objects.get(name='Activos Informáticos'))
print('Usuario creado y asignado a TI')
"

# Crear usuario de Tecnología Médica
python manage.py shell -c "
from django.contrib.auth.models import User, Group
user = User.objects.create_user('nombre.apellido', password='contraseña123')
user.groups.add(Group.objects.get(name='Tecnología Médica'))
print('Usuario creado y asignado a Tecnología Médica')
"
```

---

## 🔄 Cambiar Entre Dashboards

Los usuarios pueden cambiar manualmente entre dashboards usando:

1. **Botones en la parte superior** del dashboard (selector visual)
2. **URLs directas:**
   - Dashboard TI: `http://localhost:8000/?type=informatica`
   - Dashboard Médica: `http://localhost:8000/?type=medica`

---

## 📊 Diferencias entre Dashboards

### Dashboard de Activos Informáticos
- 💻 Computadoras
- 🖨️ Impresoras  
- 🖥️ Monitores
- 🌐 Networking
- ☎️ Telefonía
- ⌨️ Periféricos
- 💿 Software
- 📦 Insumos TI

### Dashboard de Tecnología Médica
- 🏥 Equipos médicos por tipo
- ⚠️ Alertas de calibración (30 días)
- 🔧 Alertas de mantenimiento preventivo (30 días)
- 🎯 Clasificación de riesgo (Clase I-IV)
- 📍 Equipos críticos (Clase III y IV)
- 📝 Registro sanitario
- 🏢 Área de aplicación (UCI, Quirófano, etc.)

---

## ✅ Verificación

### Listar Usuarios y sus Grupos

```bash
python manage.py shell -c "
from django.contrib.auth.models import User
print('USUARIOS Y GRUPOS:')
print('-' * 50)
for user in User.objects.all():
    grupos = ', '.join([g.name for g in user.groups.all()]) or 'Sin grupo'
    print(f'{user.username:20} → {grupos}')
"
```

### Ver Cuántos Usuarios por Grupo

```bash
python manage.py shell -c "
from django.contrib.auth.models import Group
print('USUARIOS POR GRUPO:')
print('-' * 50)
for group in Group.objects.all():
    cantidad = group.user_set.count()
    print(f'{group.name:30} {cantidad} usuarios')
"
```

---

## 🎯 Recomendaciones

1. **Asignar todos los usuarios a un grupo** para una mejor experiencia
2. **Usuarios de ambos departamentos:** Pueden tener ambos grupos, el sistema priorizará Tecnología Médica
3. **Superusuarios:** Ven el dashboard de TI por defecto pero pueden cambiar manualmente
4. **Capacitación:** Informar a los usuarios sobre el botón selector para cambiar de dashboard si es necesario

---

## 📞 Soporte

Para cualquier duda o problema, contactar al equipo de desarrollo.

