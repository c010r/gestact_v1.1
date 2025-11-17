/**
 * Cart system for sending assets to provider service
 */
const ServicioProveedorCarrito = (() => {
    const endpoints = {
        agregar: '/api/servicio-proveedor/agregar/',
        remover: '/api/servicio-proveedor/remover/',
        obtener: '/api/servicio-proveedor/obtener/',
        actualizar: '/api/servicio-proveedor/actualizar/',
        limpiar: '/api/servicio-proveedor/limpiar/',
        emitir: '/api/servicio-proveedor/emitir/',
    };

    const state = {
        items: {},
        treeInitialized: false,
    };

    const selectors = {
        modal: '#modalCarritoServicioProveedor',
        tablaContainer: '#servicio-proveedor-items-container',
        counter: '#servicio-proveedor-counter',
        btnsServicio: '.btn-servicio-proveedor',
        proveedorSelect: '#servicio-proveedor-select',
        motivoEnvio: '#servicio-motivo-envio',
        fechaEstimada: '#servicio-fecha-estimada-retorno',
        observaciones: '#servicio-observaciones',
        btnLimpiar: '#servicio-limpiar',
        btnEmitir: '#servicio-emitir',
        alertsContainer: '.container-fluid',
    };

    const csrfToken = () => {
        const el = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return el ? el.value : '';
    };

    const fetchJSON = async (url, options = {}) => {
        const response = await fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken(),
            },
            credentials: 'same-origin',
            ...options,
        });
        const data = await response.json();
        if (!response.ok || data.success === false) {
            throw new Error(data.error || 'Error desconocido');
        }
        return data;
    };

    const renderCounter = () => {
        const counter = document.querySelector(selectors.counter);
        if (!counter) return;
        
        const total = Object.values(state.items).reduce(
            (acc, tipoItems) => acc + Object.keys(tipoItems).length,
            0
        );
        
        counter.textContent = total;
        counter.style.display = total > 0 ? '' : 'none';
    };

    const renderTable = () => {
        const container = document.querySelector(selectors.tablaContainer);
        if (!container) return;

        const allItems = Object.entries(state.items).flatMap(([tipo, items]) =>
            Object.values(items).map(item => ({ ...item, tipo }))
        );

        if (allItems.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No hay activos en el carrito de servicio.</p>';
            return;
        }

        const rows = allItems.map((item) => `
            <tr>
                <td>${item.numero_serie || '-'}</td>
                <td>${item.nombre}</td>
                <td><span class="badge bg-secondary">${getTipoLabel(item.tipo)}</span></td>
                <td>${item.estado || '-'}</td>
                <td>${item.lugar || '-'}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="ServicioProveedorCarrito.remover('${item.tipo}', ${item.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        container.innerHTML = `
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>N° Serie</th>
                        <th>Nombre</th>
                        <th>Tipo</th>
                        <th>Estado</th>
                        <th>Lugar</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        `;
    };

    const getTipoLabel = (tipo) => {
        const labels = {
            'computadora': 'Computadora',
            'impresora': 'Impresora',
            'monitor': 'Monitor',
            'networking': 'Networking',
            'telefonia': 'Telefonía',
            'periferico': 'Periférico',
            'tecnologia_medica': 'Tecnología Médica',
        };
        return labels[tipo] || tipo;
    };

    const showAlert = (message, type = 'success') => {
        const container = document.querySelector(selectors.alertsContainer);
        if (!container) return;

        const alertEl = document.createElement('div');
        alertEl.className = `alert alert-${type} alert-dismissible fade show`;
        alertEl.role = 'alert';
        alertEl.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        container.insertBefore(alertEl, container.firstChild);

        setTimeout(() => alertEl.remove(), 5000);
    };

    const agregar = async (tipo, activoId) => {
        try {
            const formData = new FormData();
            formData.append('tipo_activo', tipo);
            formData.append('activo_id', activoId);

            const data = await fetchJSON(endpoints.agregar, {
                method: 'POST',
                body: formData,
            });

            if (data.success) {
                if (!state.items[tipo]) state.items[tipo] = {};
                state.items[tipo][activoId] = data.item;
                renderCounter();
                showAlert('Activo agregado al carrito de servicio', 'success');
            }
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    };

    const remover = async (tipo, activoId) => {
        try {
            const formData = new FormData();
            formData.append('tipo_activo', tipo);
            formData.append('activo_id', activoId);

            const data = await fetchJSON(endpoints.remover, {
                method: 'POST',
                body: formData,
            });

            if (data.success) {
                if (state.items[tipo]) {
                    delete state.items[tipo][activoId];
                    if (Object.keys(state.items[tipo]).length === 0) {
                        delete state.items[tipo];
                    }
                }
                renderCounter();
                renderTable();
                showAlert('Activo removido del carrito', 'info');
            }
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    };

    const cargar = async () => {
        try {
            const data = await fetchJSON(endpoints.obtener);
            if (data.success) {
                state.items = data.carrito.items || {};
                
                // Fill form fields
                const proveedor = document.querySelector(selectors.proveedorSelect);
                const motivo = document.querySelector(selectors.motivoEnvio);
                const fecha = document.querySelector(selectors.fechaEstimada);
                const observaciones = document.querySelector(selectors.observaciones);
                
                if (proveedor && data.carrito.proveedor_id) {
                    proveedor.value = data.carrito.proveedor_id;
                }
                if (motivo) motivo.value = data.carrito.motivo_envio || '';
                if (fecha) fecha.value = data.carrito.fecha_estimada_retorno || '';
                if (observaciones) observaciones.value = data.carrito.observaciones || '';
                
                renderCounter();
                renderTable();
            }
        } catch (error) {
            console.error('Error cargando carrito:', error);
        }
    };

    const actualizar = async () => {
        try {
            const formData = new FormData();
            
            const proveedor = document.querySelector(selectors.proveedorSelect);
            const motivo = document.querySelector(selectors.motivoEnvio);
            const fecha = document.querySelector(selectors.fechaEstimada);
            const observaciones = document.querySelector(selectors.observaciones);
            
            if (proveedor) formData.append('proveedor_id', proveedor.value);
            if (motivo) formData.append('motivo_envio', motivo.value);
            if (fecha) formData.append('fecha_estimada_retorno', fecha.value);
            if (observaciones) formData.append('observaciones', observaciones.value);

            await fetchJSON(endpoints.actualizar, {
                method: 'POST',
                body: formData,
            });
        } catch (error) {
            console.error('Error actualizando carrito:', error);
        }
    };

    const limpiar = async () => {
        if (!confirm('¿Está seguro de limpiar el carrito?')) return;
        
        try {
            const data = await fetchJSON(endpoints.limpiar, {
                method: 'POST',
            });

            if (data.success) {
                state.items = {};
                renderCounter();
                renderTable();
                
                // Clear form fields
                const proveedor = document.querySelector(selectors.proveedorSelect);
                const motivo = document.querySelector(selectors.motivoEnvio);
                const fecha = document.querySelector(selectors.fechaEstimada);
                const observaciones = document.querySelector(selectors.observaciones);
                
                if (proveedor) proveedor.value = '';
                if (motivo) motivo.value = '';
                if (fecha) fecha.value = '';
                if (observaciones) observaciones.value = '';
                
                showAlert('Carrito limpiado', 'info');
            }
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    };

    const emitir = async () => {
        const proveedor = document.querySelector(selectors.proveedorSelect);
        const motivo = document.querySelector(selectors.motivoEnvio);

        if (!proveedor || !proveedor.value) {
            showAlert('Debe seleccionar un proveedor', 'warning');
            return;
        }

        if (!motivo || !motivo.value.trim()) {
            showAlert('Debe especificar el motivo del envío', 'warning');
            return;
        }

        if (Object.keys(state.items).length === 0) {
            showAlert('El carrito está vacío', 'warning');
            return;
        }

        if (!confirm('¿Está seguro de emitir el envío a servicio?')) return;

        try {
            // Update cart first
            await actualizar();

            const data = await fetchJSON(endpoints.emitir, {
                method: 'POST',
            });

            if (data.success) {
                state.items = {};
                renderCounter();
                renderTable();
                
                // Close modal
                const modal = document.querySelector(selectors.modal);
                if (modal) {
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) bsModal.hide();
                }

                showAlert(data.mensaje || 'Envío creado exitosamente', 'success');
                
                // Reload page after 2 seconds
                setTimeout(() => window.location.reload(), 2000);
            }
        } catch (error) {
            showAlert(error.message, 'danger');
        }
    };

    const init = () => {
        // Set up event listeners
        const btnLimpiar = document.querySelector(selectors.btnLimpiar);
        if (btnLimpiar) {
            btnLimpiar.addEventListener('click', limpiar);
        }

        const btnEmitir = document.querySelector(selectors.btnEmitir);
        if (btnEmitir) {
            btnEmitir.addEventListener('click', emitir);
        }

        // Auto-update when form fields change
        const proveedor = document.querySelector(selectors.proveedorSelect);
        const motivo = document.querySelector(selectors.motivoEnvio);
        const fecha = document.querySelector(selectors.fechaEstimada);
        const observaciones = document.querySelector(selectors.observaciones);
        
        [proveedor, motivo, fecha, observaciones].forEach(el => {
            if (el) {
                el.addEventListener('change', actualizar);
                el.addEventListener('blur', actualizar);
            }
        });

        // Load cart when modal opens
        const modal = document.querySelector(selectors.modal);
        if (modal) {
            modal.addEventListener('show.bs.modal', cargar);
        }

        renderCounter();
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Public API
    return {
        agregar,
        remover,
        cargar,
        limpiar,
        emitir,
    };
})();

