# Vinculación de Dispositivos - Sistema de Inventario

## Descripción

Este módulo permite vincular monitores e impresoras a computadoras en el sistema de inventario, creando relaciones many-to-many que facilitan el seguimiento de qué dispositivos están asociados a cada computadora.

## Funcionalidades Implementadas

### Modelos

#### Computadora
Se agregaron los siguientes campos al modelo `Computadora`:

- `monitores_vinculados`: Relación Many-to-Many con el modelo `Monitor`
- `impresoras_vinculadas`: Relación Many-to-Many con el modelo `Impresora`

#### Métodos del Modelo Computadora

1. **`vincular_monitor(monitor)`**
   - Vincula un monitor a la computadora
   - Registra la acción en la bitácora
   - Retorna `True` si se vinculó exitosamente, `False` si ya estaba vinculado

2. **`desvincular_monitor(monitor)`**
   - Desvincula un monitor de la computadora
   - Registra la acción en la bitácora
   - Retorna `True` si se desvinculó exitosamente, `False` si no estaba vinculado

3. **`vincular_impresora(impresora)`**
   - Vincula una impresora a la computadora
   - Registra la acción en la bitácora
   - Retorna `True` si se vinculó exitosamente, `False` si ya estaba vinculada

4. **`desvincular_impresora(impresora)`**
   - Desvincula una impresora de la computadora
   - Registra la acción en la bitácora
   - Retorna `True` si se desvinculó exitosamente, `False` si no estaba vinculada

5. **`obtener_dispositivos_vinculados()`**
   - Retorna un diccionario con todos los dispositivos vinculados
   - Incluye contadores de total de monitores e impresoras

### API Endpoints

Todos los endpoints están disponibles en el `ComputadoraViewSet`:

#### 1. Vincular Monitor
- **URL**: `POST /api/computadoras/{id}/vincular_monitor/`
- **Parámetros**:
  ```json
  {
    "monitor_id": 123
  }
  ```
- **Respuesta exitosa**:
  ```json
  {
    "message": "Monitor [nombre] vinculado exitosamente"
  }
  ```

#### 2. Desvincular Monitor
- **URL**: `POST /api/computadoras/{id}/desvincular_monitor/`
- **Parámetros**:
  ```json
  {
    "monitor_id": 123
  }
  ```
- **Respuesta exitosa**:
  ```json
  {
    "message": "Monitor [nombre] desvinculado exitosamente"
  }
  ```

#### 3. Vincular Impresora
- **URL**: `POST /api/computadoras/{id}/vincular_impresora/`
- **Parámetros**:
  ```json
  {
    "impresora_id": 456
  }
  ```
- **Respuesta exitosa**:
  ```json
  {
    "message": "Impresora [nombre] vinculada exitosamente"
  }
  ```

#### 4. Desvincular Impresora
- **URL**: `POST /api/computadoras/{id}/desvincular_impresora/`
- **Parámetros**:
  ```json
  {
    "impresora_id": 456
  }
  ```
- **Respuesta exitosa**:
  ```json
  {
    "message": "Impresora [nombre] desvinculada exitosamente"
  }
  ```

#### 5. Obtener Dispositivos Vinculados
- **URL**: `GET /api/computadoras/{id}/dispositivos_vinculados/`
- **Respuesta**:
  ```json
  {
    "monitores": [
      {
        "id": 123,
        "nombre": "Monitor Samsung 24\"",
        "numero_serie": "SM123456",
        "estado_nombre": "Activo",
        "fabricante_nombre": "Samsung",
        "modelo_nombre": "S24F350"
      }
    ],
    "impresoras": [
      {
        "id": 456,
        "nombre": "Impresora HP LaserJet",
        "numero_serie": "HP789012",
        "estado_nombre": "Activo",
        "fabricante_nombre": "HP",
        "modelo_nombre": "LaserJet Pro"
      }
    ],
    "total_monitores": 1,
    "total_impresoras": 1
  }
  ```

## Manejo de Errores

Todos los endpoints manejan los siguientes errores:

- **400 Bad Request**: Cuando falta el ID del dispositivo o el dispositivo ya está/no está vinculado
- **404 Not Found**: Cuando no se encuentra la computadora o el dispositivo especificado
- **500 Internal Server Error**: Para errores internos del servidor

## Registro en Bitácora

Todas las operaciones de vinculación y desvinculación se registran automáticamente en la bitácora del sistema con:

- Descripción de la acción realizada
- Usuario que realizó la acción (si está autenticado)
- Fecha y hora de la operación
- Detalles de los dispositivos involucrados

## Ejemplos de Uso

### Usando cURL

```bash
# Vincular un monitor
curl -X POST http://localhost:8000/api/computadoras/1/vincular_monitor/ \
  -H "Content-Type: application/json" \
  -d '{"monitor_id": 123}'

# Obtener dispositivos vinculados
curl -X GET http://localhost:8000/api/computadoras/1/dispositivos_vinculados/

# Desvincular una impresora
curl -X POST http://localhost:8000/api/computadoras/1/desvincular_impresora/ \
  -H "Content-Type: application/json" \
  -d '{"impresora_id": 456}'
```

### Usando JavaScript (Frontend)

```javascript
// Vincular monitor
const vincularMonitor = async (computadoraId, monitorId) => {
  try {
    const response = await fetch(`/api/computadoras/${computadoraId}/vincular_monitor/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({ monitor_id: monitorId })
    });
    
    const data = await response.json();
    if (response.ok) {
      console.log(data.message);
    } else {
      console.error(data.error);
    }
  } catch (error) {
    console.error('Error:', error);
  }
};

// Obtener dispositivos vinculados
const obtenerDispositivos = async (computadoraId) => {
  try {
    const response = await fetch(`/api/computadoras/${computadoraId}/dispositivos_vinculados/`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
};
```

## Consideraciones Técnicas

1. **Relaciones Many-to-Many**: Un monitor o impresora puede estar vinculado a múltiples computadoras
2. **Validaciones**: Se valida que los dispositivos existan antes de vincular/desvincular
3. **Transacciones**: Las operaciones son atómicas para mantener la integridad de los datos
4. **Logging**: Todas las operaciones se registran para auditoría
5. **Serialización**: Se utilizan los serializers existentes para mantener consistencia en las respuestas

## Migración de Base de Datos

La migración `0009_computadora_impresoras_vinculadas_and_more.py` crea las tablas intermedias necesarias para las relaciones Many-to-Many.

```bash
# Aplicar migraciones
python manage.py makemigrations inventario
python manage.py migrate inventario
```