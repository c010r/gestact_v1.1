#!/usr/bin/env python3
"""
Script para agregar funcionalidad de carga masiva a todos los tipos de activos
"""

DISPOSITIVOS = [
    {
        'tipo': 'impresora',
        'titulo': 'Impresoras',
        'singular': 'Impresora',
        'icono': 'printer',
        'api_endpoint': 'impresoras'
    },
    {
        'tipo': 'monitor',
        'titulo': 'Monitores',
        'singular': 'Monitor',
        'icono': 'display',
        'api_endpoint': 'monitores'
    },
    {
        'tipo': 'networking',
        'titulo': 'Networking',
        'singular': 'Networking',
        'icono': 'router',
        'api_endpoint': 'networking'
    },
    {
        'tipo': 'telefonia',
        'titulo': 'Telefonía',
        'singular': 'Teléfono',
        'icono': 'telephone',
        'api_endpoint': 'telefonia'
    },
    {
        'tipo': 'periferico',
        'titulo': 'Periféricos',
        'singular': 'Periférico',
        'icono': 'usb-drive',
        'api_endpoint': 'perifericos'
    },
    {
        'tipo': 'insumo',
        'titulo': 'Insumos',
        'singular': 'Insumo',
        'icono': 'box',
        'api_endpoint': 'insumos'
    },
    {
        'tipo': 'software',
        'titulo': 'Software',
        'singular': 'Software',
        'icono': 'app',
        'api_endpoint': 'software'
    }
]

def generar_boton_header(dispositivo):
    """Genera el HTML del botón de carga masiva en el header"""
    return f'''        <div class="col-md-4 text-end">
            <button type="button" class="btn btn-success me-2" data-bs-toggle="modal" data-bs-target="#modalCargaMasiva">
                <i class="bi bi-cloud-upload me-2"></i>
                Carga Masiva
            </button>
            <a href="{{{{ url 'inventario:{dispositivo['tipo']}_create' }}}}" class="btn btn-primary">
                <i class="bi bi-plus-circle me-2"></i>
                Agregar {dispositivo['singular']}
            </a>
        </div>'''

def generar_modal(dispositivo):
    """Genera el HTML completo del modal de carga masiva"""
    return f'''
<!-- Modal Carga Masiva -->
<div class="modal fade" id="modalCargaMasiva" tabindex="-1" aria-labelledby="modalCargaMasivaLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="modalCargaMasivaLabel">
                    <i class="bi bi-cloud-upload me-2"></i>Carga Masiva de {dispositivo['titulo']}
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <!-- Paso 1: Seleccionar plantilla -->
                <div id="paso1-plantilla">
                    <h6 class="mb-3">Paso 1: Seleccione una plantilla</h6>
                    <div class="mb-3">
                        <label for="selectPlantilla" class="form-label">Plantilla Base</label>
                        <select class="form-select" id="selectPlantilla">
                            <option value="">Cargando plantillas...</option>
                        </select>
                        <small class="form-text text-muted">
                            La plantilla contiene los datos base que se aplicarán a todos los dispositivos
                        </small>
                    </div>
                    <div class="d-grid gap-2">
                        <button type="button" class="btn btn-primary" id="btnContinuarPaso2" disabled>
                            Continuar <i class="bi bi-arrow-right ms-2"></i>
                        </button>
                    </div>
                </div>

                <!-- Paso 2: Ingresar números de serie -->
                <div id="paso2-numeros" class="d-none">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h6 class="mb-0">Paso 2: Ingrese los números de serie</h6>
                        <button type="button" class="btn btn-sm btn-outline-secondary" id="btnVolverPaso1">
                            <i class="bi bi-arrow-left me-1"></i> Volver
                        </button>
                    </div>
                    
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        <strong>Plantilla seleccionada:</strong> <span id="nombrePlantillaSeleccionada"></span>
                    </div>

                    <div class="mb-3">
                        <label for="numerosSerieTextarea" class="form-label">
                            Números de Serie <span class="text-danger">*</span>
                        </label>
                        <textarea 
                            class="form-control font-monospace" 
                            id="numerosSerieTextarea" 
                            rows="8" 
                            placeholder="Ingrese un número de serie por línea:&#10;ABC123&#10;DEF456&#10;GHI789"
                        ></textarea>
                        <small class="form-text text-muted">
                            Ingrese un número de serie por línea. Se crearán automáticamente los dispositivos con los datos de la plantilla.
                        </small>
                    </div>

                    <div class="d-grid gap-2">
                        <button type="button" class="btn btn-success" id="btnCrearDispositivos">
                            <i class="bi bi-cloud-upload me-2"></i>Crear Dispositivos
                        </button>
                    </div>
                </div>

                <!-- Paso 3: Resultados -->
                <div id="paso3-resultados" class="d-none">
                    <h6 class="mb-3">Resultados de la Carga</h6>
                    <div id="resultadosCargaMasiva"></div>
                    <div class="alert alert-info mt-3">
                        <i class="bi bi-info-circle me-2"></i>
                        Al cerrar este modal, la lista se actualizará automáticamente.
                    </div>
                    <div class="d-grid gap-2 mt-3">
                        <button type="button" class="btn btn-primary" data-bs-dismiss="modal">
                            <i class="bi bi-check-circle me-2"></i>Cerrar y Actualizar Lista
                        </button>
                        <button type="button" class="btn btn-outline-secondary" id="btnNuevaCarga">
                            <i class="bi bi-arrow-clockwise me-2"></i>Nueva Carga
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>'''

def generar_javascript(dispositivo):
    """Genera el JavaScript completo para la carga masiva"""
    campos_especificos = {
        'impresora': "tipo_impresora: plantillaSeleccionada.tipo_impresora,",
        'monitor': "tipo_monitor: plantillaSeleccionada.tipo_monitor,",
        'networking': "tipo_networking: plantillaSeleccionada.tipo_networking,",
        'telefonia': "tipo_telefonia: plantillaSeleccionada.tipo_telefonia,",
        'periferico': "tipo_periferico: plantillaSeleccionada.tipo_periferico,",
        'insumo': "tipo_insumo: plantillaSeleccionada.tipo_insumo,\n            unidad_medida: plantillaSeleccionada.unidad_medida,\n            cantidad_stock: plantillaSeleccionada.cantidad_stock,",
        'software': "tipo_software: plantillaSeleccionada.tipo_software,\n            licencia: plantillaSeleccionada.licencia,\n            cantidad_licencias: plantillaSeleccionada.cantidad_licencias,"
    }
    
    campos = campos_especificos.get(dispositivo['tipo'], '')
    
    return f'''
{{%block extra_js %}}
<script>
document.addEventListener('DOMContentLoaded', function() {{
    const modalElement = document.getElementById('modalCargaMasiva');
    const selectPlantilla = document.getElementById('selectPlantilla');
    const btnContinuarPaso2 = document.getElementById('btnContinuarPaso2');
    const btnVolverPaso1 = document.getElementById('btnVolverPaso1');
    const btnCrearDispositivos = document.getElementById('btnCrearDispositivos');
    const btnNuevaCarga = document.getElementById('btnNuevaCarga');
    const numerosSerieTextarea = document.getElementById('numerosSerieTextarea');
    
    let plantillaSeleccionada = null;
    window.dispositivosCreados = false;
    
    // Cargar plantillas cuando se abre el modal
    modalElement.addEventListener('show.bs.modal', function() {{
        cargarPlantillas();
        resetearModal();
    }});
    
    // Recargar la página cuando se cierra el modal si se crearon dispositivos
    modalElement.addEventListener('hidden.bs.modal', function() {{
        if (window.dispositivosCreados) {{
            // Mostrar spinner de carga
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
            loadingDiv.style.backgroundColor = 'rgba(0,0,0,0.5)';
            loadingDiv.style.zIndex = '9999';
            loadingDiv.innerHTML = `
                <div class="text-center text-white">
                    <div class="spinner-border mb-3" role="status" style="width: 3rem; height: 3rem;">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <h5>Actualizando lista...</h5>
                </div>
            `;
            document.body.appendChild(loadingDiv);
            
            // Recargar después de un pequeño delay
            setTimeout(() => {{
                window.location.reload();
            }}, 500);
        }}
    }});
    
    // Cargar lista de plantillas
    function cargarPlantillas() {{
        fetch('/api/plantillas-dispositivo/?tipo_dispositivo={dispositivo['tipo']}')
            .then(response => response.json())
            .then(data => {{
                const plantillas = Array.isArray(data) ? data : (data.results || []);
                
                selectPlantilla.innerHTML = '<option value="">Seleccione una plantilla...</option>';
                
                if (plantillas.length === 0) {{
                    selectPlantilla.innerHTML += '<option value="" disabled>No hay plantillas disponibles</option>';
                }} else {{
                    plantillas.forEach(plantilla => {{
                        const option = document.createElement('option');
                        option.value = plantilla.id;
                        option.textContent = plantilla.nombre;
                        option.dataset.plantilla = JSON.stringify(plantilla);
                        selectPlantilla.appendChild(option);
                    }});
                }}
            }})
            .catch(error => {{
                console.error('Error al cargar plantillas:', error);
                selectPlantilla.innerHTML = '<option value="" disabled>Error al cargar plantillas</option>';
            }});
    }}
    
    // Habilitar botón continuar cuando se selecciona plantilla
    selectPlantilla.addEventListener('change', function() {{
        if (this.value) {{
            btnContinuarPaso2.disabled = false;
            const selectedOption = this.options[this.selectedIndex];
            plantillaSeleccionada = JSON.parse(selectedOption.dataset.plantilla);
        }} else {{
            btnContinuarPaso2.disabled = true;
            plantillaSeleccionada = null;
        }}
    }});
    
    // Continuar al paso 2
    btnContinuarPaso2.addEventListener('click', function() {{
        if (!plantillaSeleccionada) return;
        
        document.getElementById('paso1-plantilla').classList.add('d-none');
        document.getElementById('paso2-numeros').classList.remove('d-none');
        document.getElementById('nombrePlantillaSeleccionada').textContent = plantillaSeleccionada.nombre;
    }});
    
    // Volver al paso 1
    btnVolverPaso1.addEventListener('click', function() {{
        document.getElementById('paso2-numeros').classList.add('d-none');
        document.getElementById('paso1-plantilla').classList.remove('d-none');
    }});
    
    // Crear dispositivos
    btnCrearDispositivos.addEventListener('click', function() {{
        const numerosSerieText = numerosSerieTextarea.value.trim();
        
        if (!numerosSerieText) {{
            alert('Por favor ingrese al menos un número de serie');
            return;
        }}
        
        const numeroserie = numerosSerieText.split('\\n')
            .map(ns => ns.trim())
            .filter(ns => ns.length > 0);
        
        if (numeroserie.length === 0) {{
            alert('Por favor ingrese números de serie válidos');
            return;
        }}
        
        // Deshabilitar botón y mostrar loading
        btnCrearDispositivos.disabled = true;
        btnCrearDispositivos.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creando...';
        
        procesarCargaMasiva(numeroserie);
    }});
    
    // Procesar carga masiva
    async function procesarCargaMasiva(numeroserie) {{
        const resultados = [];
        
        for (const numeroSerie of numeroserie) {{
            try {{
                const resultado = await crearDispositivo(numeroSerie);
                resultados.push({{
                    numero_serie: numeroSerie,
                    success: true,
                    data: resultado
                }});
            }} catch (error) {{
                resultados.push({{
                    numero_serie: numeroSerie,
                    success: false,
                    error: error.message || 'Error desconocido'
                }});
            }}
        }}
        
        mostrarResultados(resultados);
    }}
    
    // Crear un dispositivo
    async function crearDispositivo(numeroSerie) {{
        const nombreGenerado = plantillaSeleccionada.modelo_nombre 
            ? `${{plantillaSeleccionada.modelo_nombre}}/${{numeroSerie}}` 
            : `{dispositivo['singular']}/${{numeroSerie}}`;
        
        const dispositivoData = {{
            nombre: nombreGenerado,
            numero_serie: numeroSerie,
            fecha_adquisicion: plantillaSeleccionada.fecha_adquisicion || new Date().toISOString().split('T')[0],
            estado: plantillaSeleccionada.estado,
            lugar: plantillaSeleccionada.lugar,
            {campos}
            fabricante: plantillaSeleccionada.fabricante,
            modelo: plantillaSeleccionada.modelo,
            proveedor: plantillaSeleccionada.proveedor,
            tipo_garantia: plantillaSeleccionada.tipo_garantia,
            anos_garantia: plantillaSeleccionada.anos_garantia,
            valor_adquisicion: plantillaSeleccionada.valor_adquisicion,
            comentarios: plantillaSeleccionada.comentarios
        }};
        
        const response = await fetch('/api/{dispositivo['api_endpoint']}/', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }},
            body: JSON.stringify(dispositivoData)
        }});
        
        if (!response.ok) {{
            const errorData = await response.json();
            throw new Error(JSON.stringify(errorData));
        }}
        
        return await response.json();
    }}
    
    // Mostrar resultados
    function mostrarResultados(resultados) {{
        document.getElementById('paso2-numeros').classList.add('d-none');
        document.getElementById('paso3-resultados').classList.remove('d-none');
        
        const exitosos = resultados.filter(r => r.success).length;
        const fallidos = resultados.filter(r => !r.success).length;
        
        let html = `
            <div class="alert alert-${{exitosos > 0 ? 'success' : 'danger'}}">
                <h6><i class="bi bi-check-circle me-2"></i>Resumen</h6>
                <p class="mb-0">
                    <strong>Exitosos:</strong> ${{exitosos}} | 
                    <strong>Fallidos:</strong> ${{fallidos}}
                </p>
            </div>
            
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Número de Serie</th>
                            <th>Estado</th>
                            <th>Detalles</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        resultados.forEach(resultado => {{
            const badge = resultado.success 
                ? '<span class="badge bg-success">Creado</span>'
                : '<span class="badge bg-danger">Error</span>';
            
            const detalles = resultado.success
                ? `ID: ${{resultado.data.id}}`
                : `<small class="text-danger">${{resultado.error}}</small>`;
            
            html += `
                <tr>
                    <td><code>${{resultado.numero_serie}}</code></td>
                    <td>${{badge}}</td>
                    <td>${{detalles}}</td>
                </tr>
            `;
        }});
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        document.getElementById('resultadosCargaMasiva').innerHTML = html;
        
        // Marcar que hay cambios para recargar
        window.dispositivosCreados = exitosos > 0;
    }}
    
    // Nueva carga
    btnNuevaCarga.addEventListener('click', function() {{
        resetearModal();
    }});
    
    // Resetear modal
    function resetearModal() {{
        document.getElementById('paso1-plantilla').classList.remove('d-none');
        document.getElementById('paso2-numeros').classList.add('d-none');
        document.getElementById('paso3-resultados').classList.add('d-none');
        
        selectPlantilla.value = '';
        numerosSerieTextarea.value = '';
        btnContinuarPaso2.disabled = true;
        btnCrearDispositivos.disabled = false;
        btnCrearDispositivos.innerHTML = '<i class="bi bi-cloud-upload me-2"></i>Crear Dispositivos';
        plantillaSeleccionada = null;
        window.dispositivosCreados = false;
    }}
    
    // Obtener cookie CSRF
    function getCookie(name) {{
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {{
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {{
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {{
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }}
            }}
        }}
        return cookieValue;
    }}
}});
</script>
{{%endblock %}}'''

def mostrar_instrucciones(dispositivo):
    """Muestra las instrucciones para modificar el archivo manualmente"""
    print(f"\n{'='*80}")
    print(f"INSTRUCCIONES PARA: {dispositivo['titulo'].upper()}")
    print(f"Archivo: inventario/templates/inventario/{dispositivo['tipo']}_list.html")
    print(f"{'='*80}\n")
    
    print("1. BUSCAR la línea que contiene:")
    print(f"   <a href=\"{{{{ url 'inventario:{dispositivo['tipo']}_create' }}}}\" class=\"btn btn-primary\">")
    print("\n2. REEMPLAZAR esa sección del header con:")
    print(generar_boton_header(dispositivo))
    
    print("\n3. BUSCAR el final del archivo (antes de {% endblock %})")
    print("\n4. AGREGAR el modal:")
    print(generar_modal(dispositivo))
    
    print("\n5. AGREGAR el JavaScript:")
    print(generar_javascript(dispositivo))
    
    print(f"\n{'='*80}\n")

if __name__ == '__main__':
    print("GENERADOR DE CÓDIGO PARA CARGA MASIVA")
    print("="*80)
    
    for dispositivo in DISPOSITIVOS:
        mostrar_instrucciones(dispositivo)
        input(f"Presione Enter para continuar con el siguiente dispositivo ({dispositivo['titulo']})...")
