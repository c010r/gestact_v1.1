// Función de respaldo para verificar si plantillaManager está disponible
function verificarPlantillaManager() {
    if (typeof window.plantillaManager === 'undefined') {
        // Reintentar inicialización silenciosamente
        const deviceType = window.deviceType || 'computadora';
        const formId = window.formId || 'deviceForm';
        window.plantillaManager = new PlantillaManager(deviceType, formId);
    }
    return window.plantillaManager;
}

// Funcionalidad para plantillas de dispositivos
document.addEventListener('DOMContentLoaded', function() {
    console.log('Plantillas.js cargado correctamente');
    
    // Obtener el tipo de dispositivo desde el contexto
    const deviceType = window.deviceType || 'computadora';
    const formId = window.formId || 'deviceForm';
    
    // Inicializar el gestor de plantillas
    window.plantillaManager = new PlantillaManager(deviceType, formId);
    
    // PlantillaManager inicializado
    if (window.plantillaManager) {
        console.log('PlantillaManager inicializado correctamente');
    }
});

// Clase para gestionar plantillas
class PlantillaManager {
    constructor(deviceType, formId) {
        this.deviceType = deviceType;
        this.formId = formId;
    }
    
    // Mostrar modal para guardar plantilla
    mostrarModalGuardarPlantilla() {
        const modal = document.getElementById('modalGuardarPlantilla');
        if (modal) {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        }
    }
    
    // Mostrar modal para cargar plantilla
    mostrarModalCargarPlantilla() {
        const modal = document.getElementById('modalCargarPlantilla');
        if (modal) {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
            this.cargarListaPlantillas();
        }
    }
    
    // Mostrar modal para gestionar plantillas
    mostrarModalGestionarPlantillas() {
        const modal = document.getElementById('modalGestionarPlantillas');
        if (modal) {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
            this.cargarGestionPlantillas();
        }
    }
    
    // Guardar plantilla
    guardarPlantilla() {
        const nombrePlantilla = document.getElementById('nombrePlantilla').value.trim();
        const descripcion = document.getElementById('descripcionPlantilla').value.trim();
        
        if (!nombrePlantilla) {
            this.mostrarAlerta('Por favor ingrese un nombre para la plantilla', 'warning');
            return;
        }
        
        // Recopilar datos del formulario
        const form = document.getElementById(this.formId);
        
        if (!form) {
            this.mostrarAlerta('Error: No se pudo encontrar el formulario', 'danger');
            return;
        }
        
        const formData = new FormData(form);
        
        // Construir objeto de plantilla con campos del modelo
        const plantillaData = {
            nombre: nombrePlantilla,
            descripcion: descripcion,
            tipo_dispositivo: this.deviceType
        };
        
        // Mapear campos del formulario a campos del modelo PlantillaDispositivo
        const camposMapeables = [
            'estado', 'lugar', 'fabricante', 'modelo', 'proveedor',
            'tipo_garantia', 'anos_garantia', 'valor_adquisicion', 'comentarios',
            'tipo_computadora', 'direccion_ip', 'direccion_mac',
            'tipo_impresora', 'tipo_monitor', 'tamano_pantalla', 'resolucion',
            'tipo_periferico', 'tipo_insumo', 'tipo_licencia'
        ];
        
        // Extraer valores del formulario
        for (let [key, value] of formData.entries()) {
            if (camposMapeables.includes(key) && value && value.trim() !== '') {
                plantillaData[key] = value;
            }
        }
        
        // Mostrar indicador de carga
        const btnGuardar = document.querySelector('#modalGuardarPlantilla .btn-primary');
        const textoOriginal = btnGuardar.innerHTML;
        btnGuardar.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Guardando...';
        btnGuardar.disabled = true;
        
        // Enviar datos al servidor
        fetch('/api/plantillas-dispositivo/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(plantillaData)
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Error al guardar la plantilla');
            }
        })
        .then(plantilla => {
            // Mostrar mensaje de éxito
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-success alert-dismissible fade show';
            alertDiv.innerHTML = `
                <i class="fas fa-check-circle me-2"></i>Plantilla "${plantilla.nombre}" guardada exitosamente
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            // Insertar alerta en el modal
            const modalBody = document.querySelector('#modalGuardarPlantilla .modal-body');
            modalBody.insertBefore(alertDiv, modalBody.firstChild);
            
            // Limpiar formulario
            document.getElementById('nombrePlantilla').value = '';
            document.getElementById('descripcionPlantilla').value = '';
            
            // Cerrar modal después de 2 segundos
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalGuardarPlantilla'));
                modal.hide();
            }, 2000);
        })
        .catch(error => {
            console.error('Error:', error);
            this.mostrarAlerta('Error al guardar la plantilla', 'danger');
        })
        .finally(() => {
            // Restaurar botón
            btnGuardar.innerHTML = textoOriginal;
            btnGuardar.disabled = false;
        });
    }
    
    // Cargar lista de plantillas
    cargarListaPlantillas() {
        const container = document.getElementById('listaPlantillas');
        container.innerHTML = '<div class="text-center py-4"><div class="spinner-border" role="status"></div><p class="mt-2 text-muted">Cargando plantillas...</p></div>';
        
        fetch(`/api/plantillas-dispositivo/?tipo_dispositivo=${this.deviceType}`)
        .then(response => response.json())
        .then(data => {
            console.log('Respuesta del servidor (lista):', data);
            // Manejar respuesta paginada o array directo
            const plantillas = Array.isArray(data) ? data : (data.results || []);
            this.mostrarListaPlantillas(plantillas, container);
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = '<div class="alert alert-danger">Error al cargar las plantillas</div>';
        });
    }
    
    // Mostrar lista de plantillas
    mostrarListaPlantillas(plantillas, container) {
        if (plantillas.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No hay plantillas disponibles</div>';
            return;
        }
        
        let html = '<div class="row">';
        plantillas.forEach(plantilla => {
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">${plantilla.nombre}</h6>
                            <p class="card-text text-muted small">${plantilla.descripcion || 'Sin descripción'}</p>
                            <div class="d-grid gap-2">
                                <button class="btn btn-primary btn-sm" onclick="verificarPlantillaManager().aplicarPlantilla(${plantilla.id})">
                                    <i class="fas fa-folder-open me-1"></i>Aplicar
                                </button>
                                <small class="text-muted mt-1">
                                    <i class="fas fa-info-circle me-1"></i>Para carga masiva, use el botón en la lista de dispositivos
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        
        container.innerHTML = html;
    }
    
    // Aplicar plantilla
    aplicarPlantilla(plantillaId) {
        console.log(`Aplicando plantilla ID: ${plantillaId}`);
        
        fetch(`/api/plantillas-dispositivo/${plantillaId}/`)
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(plantilla => {
            console.log('Datos recibidos:', plantilla);
            
            // Aplicar datos al formulario
            const form = document.getElementById(this.formId);
            if (!form) {
                this.mostrarAlerta('Formulario no encontrado', 'danger');
                return;
            }
            
            console.log('Datos a aplicar:', plantilla);
            
            // Mapear los campos de la plantilla a los campos del formulario
            const camposMapeables = [
                'estado', 'lugar', 'fabricante', 'modelo', 'proveedor',
                'tipo_garantia', 'anos_garantia', 'valor_adquisicion', 'comentarios',
                'tipo_computadora', 'direccion_ip', 'direccion_mac',
                'tipo_impresora', 'tamano_pantalla', 'resolucion',
                'tipo_periferico', 'tipo_insumo', 'tipo_licencia'
            ];
            
            camposMapeables.forEach(key => {
                if (plantilla[key] !== null && plantilla[key] !== undefined) {
                    const field = form.querySelector(`[name="${key}"]`);
                    if (field) {
                        if (field.type === 'checkbox' || field.type === 'radio') {
                            field.checked = plantilla[key];
                        } else {
                            field.value = plantilla[key];
                        }
                        console.log(`Campo ${key} actualizado con valor:`, plantilla[key]);
                    }
                }
            });
            
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalCargarPlantilla'));
            if (modal) {
                modal.hide();
            }
            
            this.mostrarAlerta(`Plantilla "${plantilla.nombre || 'desconocida'}" aplicada exitosamente`, 'success');
        })
        .catch(error => {
            console.error('Error al cargar plantilla:', error);
            this.mostrarAlerta('Error de conexión al cargar la plantilla', 'danger');
        });
    }
    
    // Cargar gestión de plantillas
    cargarGestionPlantillas() {
        const container = document.getElementById('gestionPlantillas');
        container.innerHTML = '<div class="text-center py-4"><div class="spinner-border" role="status"></div><p class="mt-2 text-muted">Cargando plantillas...</p></div>';
        
        fetch(`/api/plantillas-dispositivo/?tipo_dispositivo=${this.deviceType}`)
        .then(response => response.json())
        .then(data => {
            console.log('Respuesta del servidor:', data);
            // Manejar respuesta paginada o array directo
            const plantillas = Array.isArray(data) ? data : (data.results || []);
            this.mostrarGestionPlantillas(plantillas, container);
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = '<div class="alert alert-danger">Error al cargar las plantillas</div>';
        });
    }
    
    // Mostrar gestión de plantillas
    mostrarGestionPlantillas(plantillas, container) {
        if (!Array.isArray(plantillas) || plantillas.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No hay plantillas disponibles</div>';
            return;
        }
        
        let html = '<div class="table-responsive"><table class="table table-striped"><thead><tr><th>Nombre</th><th>Descripción</th><th>Fecha</th><th>Acciones</th></tr></thead><tbody>';
        plantillas.forEach(plantilla => {
            html += `
                <tr>
                    <td>${plantilla.nombre}</td>
                    <td>${plantilla.descripcion || 'Sin descripción'}</td>
                    <td>${new Date(plantilla.fecha_creacion).toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-danger btn-sm" onclick="verificarPlantillaManager().eliminarPlantilla(${plantilla.id}, '${plantilla.nombre}')">
                            <i class="fas fa-trash me-1"></i>Eliminar
                        </button>
                    </td>
                </tr>
            `;
        });
        html += '</tbody></table></div>';
        
        container.innerHTML = html;
    }
    
    // Mostrar alerta elegante
    mostrarAlerta(mensaje, tipo = 'info') {
        // Crear contenedor de alertas si no existe
        let alertContainer = document.getElementById('alert-container');
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.id = 'alert-container';
            alertContainer.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
            document.body.appendChild(alertContainer);
        }
        
        // Crear alerta
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${tipo} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="fas fa-${tipo === 'success' ? 'check-circle' : tipo === 'danger' ? 'exclamation-triangle' : tipo === 'warning' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Agregar a contenedor
        alertContainer.appendChild(alertDiv);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    // Mostrar confirmación elegante
    mostrarConfirmacion(mensaje, titulo, callback) {
        // Crear modal de confirmación
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'modalConfirmacion';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-exclamation-triangle me-2"></i>${titulo}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${mensaje}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-1"></i>Cancelar
                        </button>
                        <button type="button" class="btn btn-danger" id="btnConfirmar">
                            <i class="fas fa-check me-1"></i>Confirmar
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Mostrar modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Event listener para confirmar
        document.getElementById('btnConfirmar').addEventListener('click', () => {
            bootstrapModal.hide();
            callback();
            document.body.removeChild(modal);
        });
        
        // Limpiar modal al cerrar
        modal.addEventListener('hidden.bs.modal', () => {
            if (document.body.contains(modal)) {
                document.body.removeChild(modal);
            }
        });
    }
    
    // Eliminar plantilla
    eliminarPlantilla(plantillaId, nombrePlantilla) {
        this.mostrarConfirmacion(
            `¿Está seguro de que desea eliminar la plantilla "${nombrePlantilla}"?`,
            'Eliminar Plantilla',
            () => this.confirmarEliminacion(plantillaId)
        );
    }
    
    // Confirmar eliminación
    confirmarEliminacion(plantillaId) {
        fetch(`/api/plantillas-dispositivo/${plantillaId}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (response.ok) {
                this.mostrarAlerta('Plantilla eliminada exitosamente', 'success');
                this.cargarGestionPlantillas(); // Recargar lista
            } else {
                throw new Error('Error al eliminar la plantilla');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.mostrarAlerta('Error al eliminar la plantilla', 'danger');
        });
    }
    
    // Mostrar modal de carga masiva
    mostrarCargaMasiva(plantillaId, nombrePlantilla) {
        console.log('mostrarCargaMasiva llamado:', plantillaId, nombrePlantilla);
        
        // Verificar que el modal existe
        const modalElement = document.getElementById('modalCargaMasiva');
        if (!modalElement) {
            // Modal no encontrado, no hacer nada
            return;
        }
        
        // Cerrar el modal de cargar plantilla si está abierto
        const modalCargar = document.getElementById('modalCargarPlantilla');
        if (modalCargar) {
            const modalCargarInstance = bootstrap.Modal.getInstance(modalCargar);
            if (modalCargarInstance) {
                modalCargarInstance.hide();
            }
        }
        
        // Configurar el modal de carga masiva
        const nombreSpan = document.getElementById('nombrePlantillaCargaMasiva');
        const plantillaInput = document.getElementById('plantillaIdCargaMasiva');
        const numerosSerie = document.getElementById('numerosSerieCargaMasiva');
        const resultado = document.getElementById('resultadoCargaMasiva');
        
        if (nombreSpan) nombreSpan.textContent = nombrePlantilla;
        if (plantillaInput) plantillaInput.value = plantillaId;
        if (numerosSerie) numerosSerie.value = '';
        if (resultado) resultado.innerHTML = '';
        
        // Mostrar el modal
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    }
    
    // Procesar carga masiva
    procesarCargaMasiva() {
        const plantillaId = document.getElementById('plantillaIdCargaMasiva').value;
        const numerosSerie = document.getElementById('numerosSerieCargaMasiva').value
            .split('\n')
            .map(s => s.trim())
            .filter(s => s.length > 0);
        
        if (numerosSerie.length === 0) {
            this.mostrarAlerta('Por favor ingrese al menos un número de serie', 'warning');
            return;
        }
        
        const resultadoDiv = document.getElementById('resultadoCargaMasiva');
        resultadoDiv.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-spinner fa-spin me-2"></i>Procesando ${numerosSerie.length} dispositivo(s)...
            </div>
        `;
        
        // Obtener datos de la plantilla
        fetch(`/api/plantillas-dispositivo/${plantillaId}/`)
        .then(response => response.json())
        .then(plantilla => {
            // Procesar cada número de serie
            this.crearDispositivosMasivos(plantilla, numerosSerie, resultadoDiv);
        })
        .catch(error => {
            console.error('Error:', error);
            resultadoDiv.innerHTML = '<div class="alert alert-danger">Error al cargar la plantilla</div>';
        });
    }
    
    // Crear dispositivos masivamente
    async crearDispositivosMasivos(plantilla, numerosSerie, resultadoDiv) {
        const resultados = [];
        const tipoDispositivo = this.deviceType;
        
        for (let i = 0; i < numerosSerie.length; i++) {
            const numeroSerie = numerosSerie[i];
            
            // Actualizar progreso
            resultadoDiv.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-spinner fa-spin me-2"></i>Procesando ${i + 1} de ${numerosSerie.length}: ${numeroSerie}
                </div>
            `;
            
            try {
                // Generar nombre temporal (se puede actualizar luego en el backend)
                const nombreGenerado = plantilla.modelo_nombre 
                    ? `${plantilla.modelo_nombre}/${numeroSerie}` 
                    : `Dispositivo/${numeroSerie}`;
                
                // Crear datos del dispositivo basados en la plantilla
                const dispositivoData = {
                    nombre: nombreGenerado,
                    numero_serie: numeroSerie,
                    estado: plantilla.estado,
                    lugar: plantilla.lugar,
                    fabricante: plantilla.fabricante,
                    modelo: plantilla.modelo,
                    proveedor: plantilla.proveedor,
                    tipo_garantia: plantilla.tipo_garantia,
                    fecha_adquisicion: plantilla.fecha_adquisicion || new Date().toISOString().split('T')[0],
                    anos_garantia: plantilla.anos_garantia,
                    valor_adquisicion: plantilla.valor_adquisicion,
                    moneda: plantilla.moneda,
                    comentarios: plantilla.comentarios
                };
                
                // Agregar campos específicos según tipo de dispositivo
                if (tipoDispositivo === 'computadora') {
                    dispositivoData.tipo_computadora = plantilla.tipo_computadora;
                    dispositivoData.direccion_ip = plantilla.direccion_ip;
                    dispositivoData.direccion_mac = plantilla.direccion_mac;
                } else if (tipoDispositivo === 'impresora') {
                    dispositivoData.tipo_impresora = plantilla.tipo_impresora;
                } else if (tipoDispositivo === 'monitor') {
                    dispositivoData.tipo_monitor = plantilla.tipo_monitor;
                    dispositivoData.tamano_pantalla = plantilla.tamano_pantalla;
                    dispositivoData.resolucion = plantilla.resolucion;
                } else if (tipoDispositivo === 'periferico') {
                    dispositivoData.tipo_periferico = plantilla.tipo_periferico;
                }
                
                // Enviar al servidor
                const response = await fetch(`/api/${tipoDispositivo}s/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify(dispositivoData)
                });
                
                if (response.ok) {
                    const dispositivo = await response.json();
                    resultados.push({ 
                        serie: numeroSerie, 
                        exito: true, 
                        id: dispositivo.id,
                        nombre: dispositivo.nombre
                    });
                } else {
                    const error = await response.json();
                    resultados.push({ 
                        serie: numeroSerie, 
                        exito: false, 
                        error: JSON.stringify(error)
                    });
                }
            } catch (error) {
                resultados.push({ 
                    serie: numeroSerie, 
                    exito: false, 
                    error: error.message
                });
            }
        }
        
        // Mostrar resultados
        this.mostrarResultadosCargaMasiva(resultados, resultadoDiv);
    }
    
    // Mostrar resultados de carga masiva
    mostrarResultadosCargaMasiva(resultados, resultadoDiv) {
        const exitosos = resultados.filter(r => r.exito).length;
        const fallidos = resultados.filter(r => !r.exito).length;
        
        let html = `
            <div class="alert alert-${fallidos === 0 ? 'success' : 'warning'}">
                <h6 class="alert-heading">Proceso completado</h6>
                <p class="mb-0">
                    <i class="fas fa-check-circle text-success me-1"></i> ${exitosos} dispositivo(s) creado(s) exitosamente<br>
                    ${fallidos > 0 ? `<i class="fas fa-times-circle text-danger me-1"></i> ${fallidos} error(es)` : ''}
                </p>
            </div>
            <div class="table-responsive" style="max-height: 300px; overflow-y: auto;">
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
        
        resultados.forEach(r => {
            html += `
                <tr class="${r.exito ? 'table-success' : 'table-danger'}">
                    <td>${r.serie}</td>
                    <td>
                        ${r.exito 
                            ? '<i class="fas fa-check text-success"></i> Creado' 
                            : '<i class="fas fa-times text-danger"></i> Error'}
                    </td>
                    <td>
                        ${r.exito 
                            ? `<a href="/${this.deviceType}s/${r.id}/" target="_blank">${r.nombre}</a>` 
                            : `<small class="text-danger">${r.error}</small>`}
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        resultadoDiv.innerHTML = html;
        
        if (exitosos > 0) {
            this.mostrarAlerta(`${exitosos} dispositivo(s) creado(s) exitosamente`, 'success');
        }
    }
}
