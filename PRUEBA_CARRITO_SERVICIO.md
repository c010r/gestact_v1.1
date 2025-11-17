# 🧪 Guía de Prueba - Carrito de Servicio a Proveedor

## ✅ Sistema Listo para Probar

Todo está configurado y funcionando:
- ✅ Modelos creados y migrados
- ✅ Estado "En Servicio" creado
- ✅ 4 proveedores de demo creados
- ✅ Vistas API funcionando
- ✅ JavaScript cargado
- ✅ Templates actualizados
- ✅ Estilos aplicados

---

## 🚀 Prueba Rápida (5 minutos)

### Paso 1: Abrir Listado

```
URL: http://localhost:8000/inventario/computadoras/
```

**Verás:**
- Botón azul 🧾 (Enviar a Unidad) - Existente
- **Botón naranja/amarillo 🔧 (Enviar a Servicio) - NUEVO**
- Botón rojo 🗑️ (Eliminar)

---

### Paso 2: Agregar Activo al Carrito de Servicio

```
1. Click en botón 🔧 de cualquier computadora
2. Ver mensaje: "Activo agregado al carrito de servicio"
3. Ver en navbar (arriba derecha):
   - Botón 🔧 con badge naranja: 🔧¹
```

---

### Paso 3: Agregar Más Activos

```
1. Agregar otra computadora → 🔧²
2. Ir a: http://localhost:8000/inventario/tecnologia-medica/
3. Agregar un equipo médico → 🔧³
```

**Resultado:** Contador muestra 🔧³

---

### Paso 4: Abrir Carrito

```
1. Click en botón 🔧 (navbar - arriba derecha)
2. Se abre modal: "Carrito de Envío a Servicio"
3. Ver tabla con 3 activos agregados
```

**Tabla muestra:**
```
┌─────────────┬──────────────┬─────────────────────┬─────────┬────────┬──────────┐
│ N° Serie    │ Nombre       │ Tipo                │ Estado  │ Lugar  │ Acciones │
├─────────────┼──────────────┼─────────────────────┼─────────┼────────┼──────────┤
│ SN-DELL-001 │ Dell Lat...  │ Computadora         │ Activo  │ Lab 1  │ [🗑️]     │
│ SN-DELL-002 │ Dell Opt...  │ Computadora         │ Activo  │ Lab 2  │ [🗑️]     │
│ MED-ECG-001 │ ECG GE...    │ Tecnología Médica   │ Activo  │ Sala 3 │ [🗑️]     │
└─────────────┴──────────────┴─────────────────────┴─────────┴────────┴──────────┘
```

---

### Paso 5: Completar Formulario

```
Proveedor de Servicio: *
[TechService Uruguay                    ▼]

Fecha Estimada de Retorno:
[2024-12-31                            📅]

Motivo del Envío: *
┌────────────────────────────────────────────────────────┐
│ Reparación general - equipos con fallas de hardware   │
└────────────────────────────────────────────────────────┘

Observaciones:
┌────────────────────────────────────────────────────────┐
│ Urgente - equipos críticos para área de cardiología   │
└────────────────────────────────────────────────────────┘
```

---

### Paso 6: Emitir Envío

```
1. Click en botón "Emitir Envío" (azul, abajo derecha)
2. Confirmar en diálogo
3. Ver:
   - ✓ Mensaje de éxito
   - "Envío ENV-20241103HHMMSS creado exitosamente. 3 activos enviados a servicio."
4. Modal se cierra automáticamente
5. Página se recarga
6. Contador 🔧 desaparece (carrito vacío)
```

---

### Paso 7: Verificar Cambios

```
1. Volver a listados de activos
2. Buscar los activos enviados
3. Ver que ahora tienen estado: "En Servicio"
```

---

## 🔍 Pruebas Adicionales

### Prueba: Remover del Carrito

```
1. Agregar 3 activos al carrito → 🔧³
2. Abrir modal 🔧
3. Click en 🗑️ en uno de los activos
4. Ver:
   - Activo desaparece de la tabla
   - Contador baja a 🔧²
```

---

### Prueba: Limpiar Carrito

```
1. Agregar varios activos → 🔧⁵
2. Abrir modal 🔧
3. Click en botón "Limpiar"
4. Confirmar
5. Ver:
   - Tabla vacía
   - Formulario limpio
   - Contador desaparece
```

---

### Prueba: Validación de Proveedor

```
1. Agregar activos al carrito
2. Abrir modal 🔧
3. NO seleccionar proveedor
4. Escribir motivo
5. Click "Emitir Envío"
6. Ver error: "Debe seleccionar un proveedor"
```

---

### Prueba: Validación de Motivo

```
1. Agregar activos
2. Abrir modal
3. Seleccionar proveedor
4. NO escribir motivo
5. Click "Emitir Envío"
6. Ver error: "Debe especificar el motivo del envío"
```

---

### Prueba: Ambas Categorías

```
1. Agregar 2 computadoras → 🔧²
2. Agregar 1 impresora → 🔧³
3. Ir a tecnología médica
4. Agregar 1 equipo médico → 🔧⁴
5. Abrir modal
6. Ver:
   - 2 computadoras
   - 1 impresora
   - 1 equipo médico
   - Total: 4 activos
7. Emitir
8. Todos cambian a "En Servicio"
```

---

## 📊 Proveedores Disponibles

Los siguientes proveedores fueron creados automáticamente:

1. **TechService Uruguay**
   - Tel: +598 2900 1234
   - Email: contacto@techservice.uy
   - Dir: Av. 18 de Julio 1234

2. **MedEquip Service**
   - Tel: +598 2900 5678
   - Email: servicio@medequip.com.uy
   - Dir: Bulevar Artigas 5678

3. **CompuFix SA**
   - Tel: +598 2900 9999
   - Email: reparaciones@compufix.com
   - Dir: 8 de Octubre 4567

4. **HP Service Center**
   - Tel: +598 2900 0001
   - Email: service@hp.com.uy
   - Dir: Luis Alberto de Herrera 3456

---

## 🎯 Escenarios de Prueba

### Escenario 1: Servicio Urgente de TI

```
Contexto:
- 3 computadoras con fallas críticas
- Necesitan reparación urgente

Pasos:
1. Ir a listado de computadoras
2. Agregar las 3 al carrito de servicio
3. Proveedor: "TechService Uruguay"
4. Motivo: "Reparación urgente - fallas de hardware"
5. Fecha estimada: Hoy + 7 días
6. Observaciones: "URGENTE - equipos de producción"
7. Emitir
8. Verificar estado "En Servicio"
```

---

### Escenario 2: Calibración Anual Médica

```
Contexto:
- Equipos médicos requieren calibración anual
- Enviar a proveedor certificado

Pasos:
1. Ir a listado de tecnología médica
2. Filtrar equipos que requieren calibración
3. Agregar al carrito de servicio
4. Proveedor: "MedEquip Service"
5. Motivo: "Calibración anual obligatoria"
6. Fecha estimada: Hoy + 15 días
7. Observaciones: "Solicitar certificados de calibración"
8. Emitir
9. Verificar registro creado
```

---

### Escenario 3: Servicio Mixto

```
Contexto:
- Mix de activos TI y médicos
- Mismo proveedor hace ambos

Pasos:
1. Agregar 2 computadoras
2. Agregar 1 monitor
3. Agregar 1 equipo médico
4. Proveedor: "CompuFix SA"
5. Motivo: "Mantenimiento preventivo"
6. Emitir
7. Ver que todos cambian a "En Servicio"
```

---

## ⚠️ Validaciones a Probar

### ✅ Validación Exitosa

**Caso 1: Todo correcto**
```
✓ Proveedor seleccionado
✓ Motivo escrito
✓ Activos en carrito
→ Resultado: Envío creado
```

---

### ❌ Validaciones de Error

**Caso 2: Sin proveedor**
```
❌ Proveedor no seleccionado
✓ Motivo escrito
✓ Activos en carrito
→ Error: "Debe seleccionar un proveedor"
```

**Caso 3: Sin motivo**
```
✓ Proveedor seleccionado
❌ Motivo vacío
✓ Activos en carrito
→ Error: "Debe especificar el motivo del envío"
```

**Caso 4: Carrito vacío**
```
✓ Proveedor seleccionado
✓ Motivo escrito
❌ Sin activos
→ Error: "El carrito está vacío"
```

---

## 🎨 Elementos Visuales

### Botones en Navbar

```
┌────────────────────────────────────────┐
│ [...] [🌓] [🧾²] [🔧³] [User▼]        │
└────────────────────────────────────────┘
           ↑    ↑    ↑
        Tema Envío Servicio
             Unidad Proveedor
            (Rojo) (Naranja)
```

### Botones en Listados

```
Acciones por activo:
┌─────────────────────────────────────────┐
│ [👁️] [✏️] [🧾] [🔧] [🗑️]              │
│ Ver Edit Envío Serv Elim                │
│          Unid  Prov                     │
└─────────────────────────────────────────┘
```

---

## 📊 Verificación en Base de Datos

Después de emitir un envío, verificar:

### Tabla: inventario_envioservicioproveedor

```sql
SELECT * FROM inventario_envioservicioproveedor 
ORDER BY fecha_envio DESC LIMIT 5;
```

**Columnas importantes:**
- `numero` - ENV-20241103HHMMSS
- `proveedor_id` - ID del proveedor
- `motivo_envio` - Texto del motivo
- `estado` - "enviado"
- `fecha_envio` - Timestamp

---

### Tabla: inventario_envioservicioactivo

```sql
SELECT * FROM inventario_envioservicioactivo 
WHERE envio_id = [ID_DEL_ENVIO];
```

**Columnas importantes:**
- `envio_id` - Relación con envío
- `tipo_activo` - computadora, impresora, etc.
- `activo_id` - ID del activo
- `numero_serie` - Serie del activo
- `nombre_activo` - Nombre completo
- `estado_previo` - Estado antes del envío
- `lugar_previo` - Lugar antes del envío

---

### Estados de Activos

```sql
-- Ver activos en servicio
SELECT tipo, COUNT(*) 
FROM (
    SELECT 'computadora' as tipo FROM inventario_computadora WHERE estado_id = 6
    UNION ALL
    SELECT 'impresora' FROM inventario_impresora WHERE estado_id = 6
    UNION ALL
    SELECT 'tecnologia_medica' FROM inventario_tecnologiamedica WHERE estado_id = 6
) activos_servicio
GROUP BY tipo;
```

---

## ✅ Checklist de Prueba

### Básicas

- [ ] Ver botón 🔧 en navbar
- [ ] Ver botones 🔧 en listados
- [ ] Agregar activo al carrito
- [ ] Ver contador aumentar
- [ ] Abrir modal
- [ ] Ver activo en tabla
- [ ] Seleccionar proveedor
- [ ] Escribir motivo
- [ ] Emitir envío
- [ ] Ver confirmación
- [ ] Verificar estado "En Servicio"

---

### Avanzadas

- [ ] Agregar de múltiples tipos
- [ ] Remover del carrito
- [ ] Limpiar carrito completo
- [ ] Validar sin proveedor
- [ ] Validar sin motivo
- [ ] Validar carrito vacío
- [ ] Fecha estimada opcional
- [ ] Observaciones opcionales

---

### Integración

- [ ] Carrito de servicio independiente del de envío
- [ ] Ambos contadores funcionan
- [ ] Agregar a ambos carritos simultáneamente
- [ ] Emitir ambos independientemente

---

## 🐛 Posibles Problemas

### Problema 1: No aparece botón 🔧 en navbar

**Solución:**
```
1. Ctrl + Shift + R (limpiar caché)
2. Verificar que custom.css se cargó
3. Inspeccionar consola del navegador
```

---

### Problema 2: Error "Estado 'En Servicio' no encontrado"

**Verificar:**
```bash
cd /home/usuario/Escritorio/ASSE-GestIT
source venv/bin/activate
python manage.py shell -c "from inventario.models import Estado; print(Estado.objects.filter(nombre__icontains='servicio').values_list('nombre', flat=True))"
```

**Si no existe:**
```python
from inventario.models import Estado
Estado.objects.create(nombre="En Servicio")
```

---

### Problema 3: No hay proveedores en dropdown

**Verificar:**
```bash
python manage.py shell -c "from inventario.models import Proveedor; print(f'Proveedores: {Proveedor.objects.count()}')"
```

**Si es 0, ejecutar:**
```bash
# Volver a ejecutar crear_proveedores_demo.py
```

---

### Problema 4: JavaScript no funciona

**Verificar en consola del navegador:**
1. F12 → Console
2. Buscar errores
3. Verificar que servicio-proveedor.js se cargó
4. Probar: `ServicioProveedorCarrito`

---

## 📸 Capturas Esperadas

### Vista de Listado

```
Deberías ver en cada fila:
[👁️ Ver] [✏️ Editar] [🧾 Enviar Unidad] [🔧 Enviar Servicio] [🗑️ Eliminar]
                        ↑ Azul              ↑ Naranja/Amarillo
```

---

### Navbar con Contadores

```
[🌓] [🧾²] [🔧³] [Admin▼]
      ↑      ↑
   Badge   Badge
   Rojo   Naranja
```

---

### Modal Abierto

```
┌─────────────────────────────────────────────────────────┐
│ 🔧 Carrito de Envío a Servicio                      [X] │
├─────────────────────────────────────────────────────────┤
│ Proveedor: [TechService Uruguay ▼]  Fecha: [____📅]   │
│ Motivo: [Reparación...                              ]   │
│ Observ: [Urgente...                                 ]   │
│                                                          │
│ [Tabla con activos]                                      │
│                                                          │
│                              [Limpiar] [Emitir Envío]   │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Resultado Exitoso

Si todo funciona:

1. ✅ Botones visibles en navbar y listados
2. ✅ Agregar activos aumenta contador
3. ✅ Modal abre y muestra activos
4. ✅ Proveedores disponibles en dropdown
5. ✅ Emitir crea registro
6. ✅ Activos cambian a "En Servicio"
7. ✅ Carrito se limpia
8. ✅ Mensaje de confirmación

---

## 📞 Soporte

Si algo no funciona:

1. Verificar logs del servidor Django
2. Verificar consola del navegador (F12)
3. Revisar que migraciones se aplicaron
4. Verificar que estado "En Servicio" existe
5. Verificar que hay proveedores

---

**¡El sistema está listo! Prueba ahora mismo! 🚀**

**URLs de prueba:**
- Computadoras: http://localhost:8000/inventario/computadoras/
- Impresoras: http://localhost:8000/inventario/impresoras/
- Tecnología Médica: http://localhost:8000/inventario/tecnologia-medica/

