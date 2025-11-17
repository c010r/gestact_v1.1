# Sistema Jerárquico de Lugares - Documentación

## Descripción General

El sistema de lugares ha sido rediseñado para soportar una estructura jerárquica flexible de hasta 7 niveles, reemplazando el sistema anterior de 3 niveles fijos (Unidad Ejecutora, Unidad Asistencial, Servicio).

## Modelos

### TipoNivel

Define los tipos de niveles disponibles en la jerarquía.

**Campos:**
- `nombre`: Nombre del tipo de nivel (ej: "Unidad Ejecutora", "Servicio", "Área")
- `nivel`: Nivel jerárquico (1-7)
- `descripcion`: Descripción del tipo de nivel
- `requiere_codigo`: Indica si este nivel requiere un código identificador
- `activo`: Indica si el tipo de nivel está activo

**Niveles Predeterminados:**
1. **Nivel 1 - Unidad Ejecutora**: Nivel raíz (requiere código)
2. **Nivel 2 - Unidad Asistencial**: Departamento o unidad asistencial
3. **Nivel 3 - Servicio**: Servicio específico
4. **Nivel 4 - Área**: Área o sección
5. **Nivel 5 - Sector**: Sector o zona
6. **Nivel 6 - Ubicación**: Ubicación específica
7. **Nivel 7 - Puesto**: Puesto o lugar físico específico

### Lugares

Modelo jerárquico autorreferencial que representa la ubicación de los activos.

**Campos:**
- `nombre`: Nombre del lugar
- `codigo`: Código identificador (opcional, excepto para niveles que lo requieren)
- `tipo_nivel`: FK a TipoNivel - Define el tipo y nivel jerárquico
- `padre`: FK autorreferencial - Lugar padre en la jerarquía
- `nombre_completo`: Campo calculado - Ruta completa (ej: "UE > Servicio > Área")
- `nivel`: Campo calculado - Nivel en la jerarquía (1-7)
- `ruta_jerarquica`: Campo calculado - Ruta de IDs (ej: "/1/5/12/")
- `comentarios`: Comentarios adicionales
- `activo`: Indica si el lugar está activo
- `fecha_creacion`: Fecha de creación
- `fecha_modificacion`: Fecha de última modificación

## Validaciones

1. **Nivel Máximo**: No se pueden crear más de 7 niveles
2. **Consistencia de Nivel**: El tipo de nivel debe corresponder al nivel calculado según el padre
3. **Código Requerido**: Si el tipo de nivel requiere código, debe proporcionarse
4. **Unicidad**: No pueden existir dos lugares con el mismo nombre bajo el mismo padre
5. **Nodo Raíz**: Los lugares sin padre deben ser de nivel 1

## Métodos Principales

### Métodos de Instancia

```python
# Obtener todos los ancestros ordenados desde la raíz
ancestros = lugar.obtener_ancestros()

# Obtener todos los descendientes recursivamente
descendientes = lugar.obtener_descendientes(incluir_self=False)

# Obtener la ruta completa como lista de lugares
ruta = lugar.obtener_ruta_completa()

# Verificar si es un nodo hoja (sin hijos)
es_hoja = lugar.es_hoja()

# Verificar si es un nodo raíz (sin padre)
es_raiz = lugar.es_raiz()

# Verificar si puede tener hijos (nivel < 7)
puede_hijos = lugar.puede_tener_hijos()

# Obtener representación del nivel
nivel_nombre = lugar.obtener_nivel_nombre()
```

### Métodos de Clase

```python
# Obtener todos los nodos raíz
raices = Lugares.obtener_raices()

# Obtener todos los lugares de un nivel específico
nivel_2 = Lugares.obtener_por_nivel(2)
```

## Ejemplos de Uso

### Crear una Estructura Jerárquica

```python
from inventario.models import TipoNivel, Lugares

# Obtener tipos de nivel
tipo_ue = TipoNivel.objects.get(nivel=1)
tipo_servicio = TipoNivel.objects.get(nivel=3)
tipo_area = TipoNivel.objects.get(nivel=4)

# Crear nivel 1 (Raíz)
ue = Lugares.objects.create(
    nombre="Hospital Central",
    codigo="UE001",
    tipo_nivel=tipo_ue
)
# nombre_completo: "Hospital Central"
# nivel: 1
# ruta_jerarquica: "/1/"

# Crear nivel 3 (hijo de nivel 1 - salta nivel 2)
servicio = Lugares.objects.create(
    nombre="Urgencias",
    padre=ue,
    tipo_nivel=tipo_servicio
)
# ERROR: tipo_nivel debe ser de nivel 2 para este padre

# Correcto: crear nivel 2 primero
tipo_ua = TipoNivel.objects.get(nivel=2)
ua = Lugares.objects.create(
    nombre="Área Médica",
    padre=ue,
    tipo_nivel=tipo_ua
)

# Ahora crear nivel 3
servicio = Lugares.objects.create(
    nombre="Urgencias",
    padre=ua,
    tipo_nivel=tipo_servicio
)
# nombre_completo: "Hospital Central > Área Médica > Urgencias"
# nivel: 3
# ruta_jerarquica: "/1/2/3/"

# Crear nivel 4
area = Lugares.objects.create(
    nombre="Consultorios",
    padre=servicio,
    tipo_nivel=tipo_area
)
# nombre_completo: "Hospital Central > Área Médica > Urgencias > Consultorios"
# nivel: 4
```

### Consultar la Jerarquía

```python
# Obtener todos los hijos directos
hijos = lugar.hijos.all()

# Obtener todos los descendientes recursivamente
todos_descendientes = lugar.obtener_descendientes()

# Obtener el camino desde la raíz
ruta = lugar.obtener_ruta_completa()
for nivel in ruta:
    print(f"Nivel {nivel.nivel}: {nivel.nombre}")

# Buscar lugares por ruta jerárquica
# Ejemplo: Todos los lugares bajo un lugar específico
lugares_bajo_ue = Lugares.objects.filter(
    ruta_jerarquica__startswith=ue.ruta_jerarquica
)
```

### Filtrar y Buscar

```python
# Lugares activos de un nivel específico
nivel_4_activos = Lugares.objects.filter(nivel=4, activo=True)

# Lugares de un tipo de nivel específico
servicios = Lugares.objects.filter(tipo_nivel__nombre='Servicio')

# Lugares hoja (sin hijos) - útil para asignar activos
from django.db.models import Count
lugares_hoja = Lugares.objects.annotate(
    num_hijos=Count('hijos')
).filter(num_hijos=0)
```

## Asignación de Activos

Los activos (Computadora, Monitor, Impresora) se asignan a lugares específicos.
Es recomendable asignarlos a nodos hoja (lugares sin hijos) para mejor organización.

```python
# Verificar si un lugar puede tener activos
if lugar.es_hoja():
    computadora.lugar = lugar
    computadora.save()
```

## Comandos de Gestión

### Inicializar Tipos de Nivel

```bash
python manage.py init_tipos_nivel
```

Este comando crea/actualiza los 7 tipos de nivel predeterminados.

## Migración de Datos Antiguos

Si tienes datos del sistema anterior (UnidadEjecutora, UnidadAsistencial, ServicioUE),
puedes crear un script de migración personalizado:

```python
# Ejemplo de migración
from inventario.models import (
    UnidadEjecutora, UnidadAsistencial, ServicioUE,
    TipoNivel, Lugares
)

tipo_ue = TipoNivel.objects.get(nivel=1)
tipo_ua = TipoNivel.objects.get(nivel=2)
tipo_servicio = TipoNivel.objects.get(nivel=3)

# Migrar Unidades Ejecutoras
for ue_antigua in UnidadEjecutora.objects.all():
    Lugares.objects.create(
        nombre=ue_antigua.nombre,
        codigo=ue_antigua.numero_ue,
        tipo_nivel=tipo_ue,
        comentarios=ue_antigua.comentarios
    )

# Continuar con niveles inferiores...
```

## Índices y Optimización

La tabla incluye índices en:
- `nivel`: Para búsquedas por nivel
- `padre`: Para navegación jerárquica
- `tipo_nivel`: Para filtrar por tipo
- `ruta_jerarquica`: Para búsquedas de descendientes

## Notas Importantes

1. **Cascada en Borrado**: Al eliminar un lugar, se eliminan todos sus descendientes
2. **Protección de Tipos**: Los tipos de nivel tienen protección PROTECT - no se pueden eliminar si hay lugares usándolos
3. **Campos Calculados**: `nombre_completo`, `nivel` y `ruta_jerarquica` se calculan automáticamente al guardar
4. **Unicidad**: El nombre es único solo dentro del mismo padre, permitiendo nombres duplicados en diferentes ramas

## Interfaz de Admin

El admin de Django incluye:
- Lista filtrable por nivel, tipo y estado activo
- Búsqueda por nombre, código y comentarios
- Campos de solo lectura para datos calculados
- Organización en fieldsets lógicos
- Optimización de consultas con select_related

## Próximos Pasos

1. Crear vistas de frontend para gestionar la jerarquía
2. Implementar un árbol visual interactivo
3. Agregar validaciones adicionales según necesidades del negocio
4. Crear reportes por estructura jerárquica
