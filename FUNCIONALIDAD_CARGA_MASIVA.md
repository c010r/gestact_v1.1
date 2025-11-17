# Funcionalidad de Carga Masiva desde Plantillas

## Descripción

Se implementó una funcionalidad que permite crear múltiples dispositivos de forma masiva a partir de una plantilla, ingresando únicamente los números de serie.

## Flujo de Uso

1. **Crear una plantilla** con la configuración base (fabricante, modelo, estado, lugar, etc.)
2. **Cargar Plantillas** → Seleccionar plantilla → Clic en **"Carga Masiva"**
3. **Ingresar números de serie**, uno por línea
4. **Procesar** → El sistema crea automáticamente un dispositivo por cada número de serie

## Características

### Interfaz de Usuario

- **Botón "Carga Masiva"** junto al botón "Aplicar" en cada plantilla
- **Modal dedicado** con área de texto para ingresar números de serie
- **Barra de progreso** que muestra el avance de la creación
- **Tabla de resultados** con:
  - Estado de cada creación (éxito/error)
  - Enlaces directos a los dispositivos creados
  - Mensajes de error detallados

### Procesamiento

- **Carga asíncrona**: Procesa un dispositivo a la vez para evitar sobrecargar el servidor
- **Feedback en tiempo real**: Muestra qué número de serie se está procesando
- **Manejo de errores**: Continúa procesando aunque falle alguno
- **Resumen final**: Muestra cantidad de éxitos y errores

### Datos Heredados de la Plantilla

Cada dispositivo creado hereda de la plantilla:

**Comunes:**
- Estado
- Lugar
- Fabricante
- Modelo
- Proveedor
- Tipo de garantía
- Años de garantía
- Valor de adquisición
- Moneda
- Comentarios

**Específicos por tipo:**
- **Computadoras**: Tipo, Dirección IP, Dirección MAC
- **Impresoras**: Tipo de impresora
- **Monitores**: Tipo, Tamaño de pantalla, Resolución
- **Periféricos**: Tipo de periférico

**Único por dispositivo:**
- Número de serie (ingresado por el usuario)
- Nombre (generado automáticamente)
- Número de inventario (generado automáticamente)

## Implementación Técnica

### Archivos Modificados

1. **inventario/static/inventario/js/plantillas.js**
   - Función `mostrarCargaMasiva()`: Muestra el modal
   - Función `procesarCargaMasiva()`: Valida y procesa los números de serie
   - Función `crearDispositivosMasivos()`: Crea dispositivos uno por uno
   - Función `mostrarResultadosCargaMasiva()`: Muestra tabla de resultados
   - Botón "Carga Masiva" agregado a cada plantilla en la lista

2. **inventario/templates/inventario/partials/plantillas_sidebar.html**
   - Modal `modalCargaMasiva` con formulario de carga
   - Área de texto para números de serie
   - Sección de resultados

### Flujo de Datos

```
1. Usuario abre modal "Cargar Plantilla"
2. Selecciona plantilla → Clic "Carga Masiva"
3. Modal muestra nombre de plantilla seleccionada
4. Usuario ingresa números de serie (uno por línea)
5. Clic "Procesar Carga Masiva"
6. JavaScript:
   - Divide el texto en líneas
   - Obtiene datos de la plantilla vía API
   - Para cada número de serie:
     a. Crea objeto con datos de plantilla + número de serie
     b. Envía POST a /api/{tipo}s/
     c. Guarda resultado (éxito/error)
   - Muestra tabla de resultados
```

### Endpoints API Utilizados

- **GET** `/api/plantillas-dispositivo/{id}/` - Obtener datos de plantilla
- **POST** `/api/computadoras/` - Crear computadora
- **POST** `/api/impresoras/` - Crear impresora
- **POST** `/api/monitores/` - Crear monitor
- **POST** `/api/networking/` - Crear dispositivo de red
- **POST** `/api/telefonia/` - Crear dispositivo de telefonía
- **POST** `/api/perifericos/` - Crear periférico

### Ejemplo de Datos Enviados

```json
{
  "numero_serie": "ABC123",
  "estado": 5,
  "lugar": 12,
  "fabricante": 3,
  "modelo": 45,
  "proveedor": 8,
  "tipo_garantia": 2,
  "anos_garantia": 3,
  "valor_adquisicion": "1500.00",
  "moneda": "USD",
  "comentarios": "Plantilla oficina estándar",
  "tipo_computadora": 1,
  "direccion_ip": null,
  "direccion_mac": null
}
```

## Interfaz de Usuario

### Modal de Carga Masiva

```
┌─────────────────────────────────────────────────────┐
│ Carga Masiva desde Plantilla                     × │
├─────────────────────────────────────────────────────┤
│ ℹ️ Plantilla seleccionada: Computadora HP Estándar │
│                                                     │
│ Números de Serie                                    │
│ ┌───────────────────────────────────────────────┐  │
│ │ ABC123                                         │  │
│ │ DEF456                                         │  │
│ │ GHI789                                         │  │
│ │                                                │  │
│ └───────────────────────────────────────────────┘  │
│ 💡 Ingrese un número de serie por línea           │
│                                                     │
│ [Resultados aparecen aquí]                         │
│                                                     │
├─────────────────────────────────────────────────────┤
│ [Cerrar]              [Procesar Carga Masiva] ⬆️   │
└─────────────────────────────────────────────────────┘
```

### Tabla de Resultados

```
┌─────────────────────────────────────────────────────┐
│ ✓ 3 dispositivo(s) creado(s) exitosamente          │
├──────────────┬────────────┬──────────────────────────┤
│ Nº de Serie  │ Estado     │ Detalles                │
├──────────────┼────────────┼──────────────────────────┤
│ ABC123       │ ✓ Creado   │ HP/ABC123 [Ver]         │
│ DEF456       │ ✓ Creado   │ HP/DEF456 [Ver]         │
│ GHI789       │ ✗ Error    │ Número ya existe        │
└──────────────┴────────────┴──────────────────────────┘
```

## Casos de Uso

### Caso 1: Compra de Lote de Computadoras

**Escenario:** Se compraron 20 computadoras HP ProDesk del mismo modelo

1. Crear plantilla "HP ProDesk G6"
   - Fabricante: HP
   - Modelo: ProDesk G6
   - Estado: Nuevo
   - Lugar: Almacén
   - Valor: $800
   - Moneda: USD

2. Carga Masiva
   - Pegar 20 números de serie
   - Procesar
   - Resultado: 20 computadoras creadas en segundos

### Caso 2: Inventario de Monitores

**Escenario:** Inventariar monitores Samsung 24" en diferentes ubicaciones

1. Crear plantilla "Monitor Samsung 24\""
   - Fabricante: Samsung
   - Modelo: S24F350
   - Tamaño: 24"
   - Resolución: 1920x1080

2. Carga Masiva
   - Ingresar números de serie de monitores
   - Los dispositivos se crean con ubicación de la plantilla
   - Posteriormente se pueden mover a ubicaciones específicas

### Caso 3: Configuración de Red

**Escenario:** Configurar switches de red del mismo modelo

1. Crear plantilla "Switch Cisco Catalyst"
   - Fabricante: Cisco
   - Modelo: Catalyst 2960
   - Estado: Operativo

2. Carga Masiva
   - Ingresar números de serie de switches
   - Todos se crean con configuración base
   - Luego se asignan IPs específicas

## Ventajas

✅ **Ahorro de tiempo**: Crear 100 dispositivos en minutos vs. horas  
✅ **Consistencia**: Todos los dispositivos tienen la misma configuración base  
✅ **Menos errores**: Se ingresa cada dato una sola vez (en la plantilla)  
✅ **Trazabilidad**: Tabla de resultados permite identificar problemas  
✅ **Flexibilidad**: Se pueden editar dispositivos después de crearlos  

## Validaciones

- ✓ Al menos un número de serie ingresado
- ✓ Números de serie únicos por tipo de dispositivo
- ✓ Campos requeridos heredados de la plantilla
- ✓ Manejo de errores de red y servidor
- ✓ Feedback visual durante el proceso

## Mejoras Futuras (No Implementadas)

- [ ] Importar desde archivo CSV/Excel
- [ ] Asignar ubicaciones diferentes por dispositivo
- [ ] Editar valores específicos antes de crear
- [ ] Programar creación para fecha futura
- [ ] Enviar notificación al completar
- [ ] Exportar resultados a PDF/Excel

## Pruebas Recomendadas

1. Crear plantilla de prueba
2. Ir a "Cargar Plantilla"
3. Seleccionar plantilla → "Carga Masiva"
4. Ingresar 3-5 números de serie de prueba
5. Procesar
6. Verificar resultados en la tabla
7. Visitar enlaces de dispositivos creados
8. Probar con número de serie duplicado (debería fallar)

## Notas Técnicas

- El campo `nombre` se genera automáticamente en el backend
- El campo `numero_inventario` se genera automáticamente con formato UE/Modelo/Serie
- La creación es secuencial (no paralela) para evitar race conditions
- Se usa `async/await` para manejo de promesas
- Los errores no detienen el proceso completo
- El modal permanece abierto para revisar resultados
