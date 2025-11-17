# 🎯 Guía de Uso del Sistema ASSE-GestACT v2 (Sin Django Admin)

## Inicio Rápido

El sistema ASSE-GestACT v2 ahora funciona **completamente sin Django Admin**. Todas las operaciones se realizan a través del frontend personalizado y la API REST.

---

## 🚀 Arrancar el Sistema

### 1. Activar entorno virtual
```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### 2. Iniciar servidor
```bash
python manage.py runserver
```

El sistema estará disponible en: **http://127.0.0.1:8000/**

---

## 📁 Gestión de Activos (Frontend)

### Dashboard Principal
```
URL: http://127.0.0.1:8000/
```
- Vista general del sistema
- Acceso a todos los módulos

### Computadoras

**Listar:**
```
URL: http://127.0.0.1:8000/computadoras/
```

**Crear Nueva:**
```
URL: http://127.0.0.1:8000/computadoras/crear/
```
El formulario incluye:
- ✅ Widget jerárquico para seleccionar lugar (7 niveles)
- ✅ Búsqueda de lugares en tiempo real
- ✅ Árbol expandible/contraíble
- ✅ Muestra ruta completa: "Hospital > Cirugía > Pabellón 1 > Sala 1"

**Editar:**
```
URL: http://127.0.0.1:8000/computadoras/editar/<id>/
```

**Ver Detalle:**
```
URL: http://127.0.0.1:8000/computadoras/<id>/
```

### Impresoras

```
Listar:  http://127.0.0.1:8000/impresoras/
Crear:   http://127.0.0.1:8000/impresoras/crear/
Editar:  http://127.0.0.1:8000/impresoras/editar/<id>/
```

### Monitores

```
Listar:  http://127.0.0.1:8000/monitores/
Crear:   http://127.0.0.1:8000/monitores/crear/
Editar:  http://127.0.0.1:8000/monitores/editar/<id>/
```

---

## 🔌 API REST

### Endpoints Principales

**Computadoras:**
```bash
# Listar todas
GET http://127.0.0.1:8000/api/computadoras/

# Ver una específica
GET http://127.0.0.1:8000/api/computadoras/<id>/

# Crear nueva
POST http://127.0.0.1:8000/api/computadoras/
Content-Type: application/json
{
  "nombre": "PC-001",
  "numero_serie": "ABC123",
  "numero_inventario": "INV-001",
  "lugar": 15,  // ID del lugar jerárquico
  "estado": 1,
  "tipo_computadora": 1,
  "fabricante": 1,
  "modelo": 1
}

# Actualizar
PUT/PATCH http://127.0.0.1:8000/api/computadoras/<id>/
{
  "nombre": "PC-001-Actualizado"
}

# Eliminar
DELETE http://127.0.0.1:8000/api/computadoras/<id>/
```

**Lugares (Jerárquicos):**
```bash
# Listar todos los lugares
GET http://127.0.0.1:8000/api/lugares/

# Ver lugar específico con jerarquía completa
GET http://127.0.0.1:8000/api/lugares/<id>/

# Crear nuevo lugar
POST http://127.0.0.1:8000/api/lugares/
{
  "nombre": "Sala 3",
  "tipo_nivel": 6,  // ID del TipoNivel (Ubicación)
  "padre": 10,      // ID del lugar padre
  "codigo": "SAL03",
  "activo": true
}
```

**Otros Endpoints:**
```
GET /api/impresoras/
GET /api/monitores/
GET /api/fabricantes/
GET /api/modelos/
GET /api/proveedores/
GET /api/estados/
GET /api/tipos-nivel/
GET /api/facturas/
```

---

## 🌳 Uso del Widget Jerárquico de Lugares

### En Formularios del Frontend

Cuando crees o edites un activo (Computadora, Impresora, Monitor):

1. **Hacer clic en el campo "Lugar"**
   - Se abrirá un dropdown con el árbol de lugares

2. **Buscar ubicación**
   - Escribir en el campo de búsqueda
   - El árbol se filtra automáticamente
   - Se expanden los nodos padre de las coincidencias

3. **Navegar por el árbol**
   - Expandir: Click en ▶
   - Contraer: Click en ▼
   - Seleccionar: Click en el lugar deseado

4. **Resultado**
   - El campo muestra la ruta completa:
   - Ejemplo: "Hospital Regional > Cirugía > Pabellón 1 > Quirófano > Sala 1"

### Ejemplo de Jerarquía

```
📁 Hospital Regional (Nivel 1: Unidad Ejecutora)
  └─ 🏢 Cirugía (Nivel 2: Unidad Asistencial)
     └─ 🏥 Pabellón Quirúrgico (Nivel 3: Servicio)
        ├─ 📋 Pabellón 1 (Nivel 4: Área)
        │  ├─ 🔧 Pre-Operatorio (Nivel 5: Sector)
        │  └─ 🔧 Quirófano (Nivel 5: Sector)
        │     ├─ 📍 Sala 1 (Nivel 6: Ubicación)
        │     │  ├─ 💺 Mesa Quirúrgica (Nivel 7: Puesto)
        │     │  ├─ 💺 Estación Anestesia (Nivel 7: Puesto)
        │     │  └─ 💺 Mesa Instrumental (Nivel 7: Puesto)
        │     └─ 📍 Sala 2 (Nivel 6: Ubicación)
        └─ 📋 Pabellón 2 (Nivel 4: Área)
           └─ 🔧 Recuperación (Nivel 5: Sector)
```

---

## 🛠️ Comandos de Gestión

### Datos de Ejemplo

**Crear lugares jerárquicos de ejemplo:**
```bash
python manage.py crear_lugares_ejemplo
```
Crea:
- 2 Unidades Ejecutoras
- 3 Unidades Asistenciales
- 3 Servicios
- 3 Áreas
- 3 Sectores
- 2 Ubicaciones
- 3 Puestos
**Total: 19 lugares**

**Inicializar tipos de nivel:**
```bash
python manage.py init_tipos_nivel
```
Crea los 7 niveles jerárquicos predefinidos

### Base de Datos

**Aplicar migraciones:**
```bash
python manage.py migrate
```

**Crear nuevas migraciones:**
```bash
python manage.py makemigrations
```

**Shell interactivo:**
```bash
python manage.py shell
```

Ejemplo de uso en shell:
```python
from inventario.models import Computadora, Lugares, Estado

# Ver todos los lugares
lugares = Lugares.objects.all()
for lugar in lugares:
    print(f"{lugar.nivel} - {lugar.nombre_completo}")

# Crear una computadora
lugar = Lugares.objects.get(nombre="Mesa Quirúrgica")
estado = Estado.objects.first()
pc = Computadora.objects.create(
    nombre="PC-QUIROFANO-01",
    numero_serie="SN123456",
    numero_inventario="INV-001",
    lugar=lugar,
    estado=estado
)

# Ver la ruta completa del lugar
print(pc.lugar.nombre_completo)
# Output: Hospital Regional > Cirugía > Pabellón Quirúrgico > Pabellón 1 > Quirófano > Sala 1 > Mesa Quirúrgica
```

---

## 📊 Consultas Útiles

### Python Shell

```python
# Contar activos por lugar
from inventario.models import Computadora
from django.db.models import Count

Computadora.objects.values('lugar__nombre_completo') \
    .annotate(total=Count('id')) \
    .order_by('-total')

# Ver jerarquía completa de un lugar
lugar = Lugares.objects.get(nombre="Sala 1")
ancestros = lugar.obtener_ancestros()
for ancestro in ancestros:
    print(" " * ancestro.nivel + ancestro.nombre)

# Ver todos los hijos de un lugar
lugar = Lugares.objects.get(nombre="Cirugía")
hijos = lugar.hijos.all()
for hijo in hijos:
    print(f"  - {hijo.nombre}")

# Ver todos los activos en un lugar y sus descendientes
lugar = Lugares.objects.get(nombre="Pabellón 1")
descendientes_ids = [d.id for d in lugar.obtener_descendientes()]
activos = Computadora.objects.filter(
    lugar__id__in=descendientes_ids
)
```

---

## 🔍 Solución de Problemas

### El servidor no arranca

**Problema:** Error al iniciar `runserver`

**Solución:**
```bash
# 1. Verificar que no haya errores
python manage.py check

# 2. Ver detalles del error
python manage.py runserver --traceback

# 3. Verificar migraciones
python manage.py showmigrations
python manage.py migrate
```

### No veo el widget jerárquico

**Problema:** El campo "Lugar" aparece como select normal

**Solución:**
1. Verificar que los archivos estáticos estén cargados:
   ```bash
   python manage.py collectstatic
   ```

2. Verificar que existan CSS y JS:
   ```
   inventario/static/inventario/css/tree-select.css
   inventario/static/inventario/js/tree-select.js
   ```

3. Limpiar caché del navegador (Ctrl+Shift+R)

### No hay lugares disponibles

**Problema:** El widget está vacío

**Solución:**
```bash
# Crear lugares de ejemplo
python manage.py crear_lugares_ejemplo

# Verificar en shell
python manage.py shell
>>> from inventario.models import Lugares
>>> Lugares.objects.count()
19
```

### Error de permisos en la API

**Problema:** 403 Forbidden en endpoints de la API

**Solución:**
1. Verificar configuración de `rest_framework` en `settings.py`
2. Agregar autenticación si es necesaria
3. Revisar permisos de los viewsets

---

## 📝 Archivos de Configuración Importantes

### settings.py
```python
# Django Admin: DESHABILITADO
INSTALLED_APPS = [
    # 'django.contrib.admin',  # ❌ No se usa
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django_filters',
    'inventario',
]
```

### urls.py
```python
urlpatterns = [
    # path('admin/', admin.site.urls),  # ❌ Admin deshabilitado
    path('', include('inventario.urls')),  # ✅ Frontend personalizado
]
```

---

## 📚 Documentación Adicional

- **ADMIN_ELIMINADO.md** - Detalles de la eliminación del admin
- **RESUMEN_ELIMINACION_ADMIN.md** - Resumen ejecutivo
- **JERARQUIA_LUGARES.md** - Sistema jerárquico completo
- **SISTEMA_JERARQUICO_WIDGETS.md** - Widgets personalizados
- **IMPLEMENTACION_COMPLETADA.md** - Implementación completa

---

## 🎯 Flujo de Trabajo Recomendado

### Para Agregar un Nuevo Activo

1. **Acceder al formulario**
   ```
   http://127.0.0.1:8000/computadoras/crear/
   ```

2. **Llenar información básica**
   - Nombre del equipo
   - Número de serie
   - Número de inventario

3. **Seleccionar lugar con widget jerárquico**
   - Click en el campo "Lugar"
   - Buscar o navegar por el árbol
   - Seleccionar la ubicación más específica (ej: "Mesa Quirúrgica")

4. **Completar especificaciones**
   - Fabricante, Modelo, Estado
   - Tipo de computadora
   - Proveedor

5. **Garantía**
   - Tipo de garantía
   - Fecha de adquisición
   - Años de garantía

6. **Guardar**

El sistema automáticamente calculará:
- Fecha de finalización de garantía
- Ruta jerárquica completa del lugar
- Timestamps de creación/modificación

---

## ✅ Verificación del Sistema

### Estado Actual
```bash
$ python manage.py check
System check identified no issues (0 silenced).
```

### Servidor Funcionando
```bash
$ python manage.py runserver
Starting development server at http://127.0.0.1:8000/
```

### Datos Disponibles
```bash
$ python manage.py shell
>>> from inventario.models import Lugares, Computadora
>>> Lugares.objects.count()
19
>>> Computadora.objects.count()
0  # (o el número de computadoras creadas)
```

---

## 🎉 ¡Sistema Listo!

El sistema ASSE-GestACT v2 está completamente operativo sin Django Admin. 

**Accede a:**
- Frontend: http://127.0.0.1:8000/
- API: http://127.0.0.1:8000/api/

**¡Disfruta del sistema de inventario con widgets jerárquicos!** 🚀
