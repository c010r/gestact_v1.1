const FacturacionCarrito = (() => {
    const endpoints = {
        agregar: '/api/facturacion/agregar/',
        remover: '/api/facturacion/remover/',
        obtener: '/api/facturacion/obtener/',
        actualizar: '/api/facturacion/actualizar/',
        limpiar: '/api/facturacion/limpiar/',
        emitir: '/api/facturacion/emitir/',
    };

    const state = {
        items: {},
        treeInitialized: false,
        treeInstance: null,
    };

    const selectors = {
        modal: '#modalCarritoFacturacion',
        tablaContainer: '#facturacion-items-container',
        counter: '#facturacion-counter',
        btnsFacturacion: '.btn-facturacion',
        lugarDestino: '#facturacion-lugar-destino .tree-select-input',
        lugarDestinoContainer: '#facturacion-lugar-destino',
        observaciones: '#facturacion-observaciones',
        btnLimpiar: '#facturacion-limpiar',
        btnEmitir: '#facturacion-emitir',
        alertsContainer: '.container-fluid',
    };

    const csrfToken = () => {
        const el = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return el ? el.value : ''; // safe fallback
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
        const counterEl = document.querySelector(selectors.counter);
        if (!counterEl) return;
        const total = Object.values(state.items).reduce((acc, items) => acc + Object.keys(items).length, 0);
        counterEl.textContent = total;
        counterEl.style.display = total > 0 ? 'inline' : 'none';
    };

    const renderTabla = () => {
        const container = document.querySelector(selectors.tablaContainer);
        if (!container) return;

        const total = Object.values(state.items).reduce((acc, items) => acc + Object.keys(items).length, 0);
        if (total === 0) {
            container.innerHTML = '<p class="text-muted text-center">No hay activos seleccionados.</p>';
            return;
        }

        let html = '<table class="table table-bordered"><thead><tr><th>Tipo</th><th>Nombre</th><th>N° Serie</th><th>Lugar</th><th></th></tr></thead><tbody>';
        Object.entries(state.items).forEach(([tipo, items]) => {
            Object.values(items).forEach(item => {
                html += `<tr>
                    <td>${tipo}</td>
                    <td>${item.nombre || ''}</td>
                    <td>${item.numero_serie || ''}</td>
                    <td>${item.lugar || ''}</td>
                    <td><button class="btn btn-sm btn-danger" data-remove="${tipo}:${item.id}"><i class="bi bi-x"></i></button></td>
                </tr>`;
            });
        });
        html += '</tbody></table>';
        container.innerHTML = html;
    };

    const cargarLugares = async () => {
        const container = document.querySelector(selectors.lugarDestinoContainer);
        if (!container) {
            return;
        }

        if (state.treeInitialized && state.treeInstance) {
            return;
        }

        const data = await fetchJSON('/api/lugares/');

        const lugares = Array.isArray(data)
            ? data
            : Array.isArray(data.results)
                ? data.results
                : [];

        const treeData = lugares.map(l => ({
            id: l.id,
            nombre: l.nombre,
            nombre_completo: l.nombre_completo || l.nombre,
            nivel: l.nivel,
            tipo: l.tipo_nivel_nombre || '',
            tipo_nivel_id: l.tipo_nivel,
            tipo_nivel_requiere_codigo: false,
            padre_id: l.padre,
            es_hoja: false,
            codigo: l.codigo || '',
            activo: true,
        }));

        container.dataset.tree = JSON.stringify(treeData);
        container.dataset.tiposNivel = '[]';

        // Limpiar contenido previo y renderizar plantilla del widget
        container.innerHTML = `
            <input type="hidden" name="lugar_destino" value="" class="tree-select-input">
            <div class="input-group">
                <div class="tree-select-display">
                    <div class="tree-select-content">
                        <span class="tree-select-placeholder">Seleccione una ubicación...</span>
                        <span class="tree-select-value d-none"></span>
                    </div>
                    <span class="tree-select-arrow">▼</span>
                </div>
                <button type="button" class="btn btn-outline-secondary tree-select-add-btn" data-bs-toggle="modal" data-bs-target="#modalNuevoLugar" title="Agregar nuevo lugar">
                    <i class="bi bi-plus"></i>
                </button>
            </div>
            <div class="tree-select-dropdown">
                <div class="tree-search">
                    <input type="text" placeholder="Buscar ubicación..." autocomplete="off">
                </div>
                <ul class="tree-list"></ul>
            </div>
        `;

        if (window.TreeSelect) {
            state.treeInstance = new window.TreeSelect(container);
            state.treeInitialized = true;
        }
    };

    const syncFields = carrito => {
        const lugar = document.querySelector(selectors.lugarDestino);
        const obs = document.querySelector(selectors.observaciones);
        if (lugar && carrito.lugar_destino_id) {
            lugar.value = carrito.lugar_destino_id;
            if (state.treeInstance) {
                state.treeInstance.setValue(carrito.lugar_destino_id, false);
            }
        } else {
            if (lugar) {
                lugar.value = '';
            }
            if (state.treeInstance) {
                state.treeInstance.setValue('', false);
            }
        }
        if (obs) {
            obs.value = carrito.observaciones || '';
        }
    };

    const cargarCarrito = async () => {
        const data = await fetchJSON(endpoints.obtener);
        state.items = data.carrito.items || {};
        renderCounter();
        renderTabla();
        syncFields(data.carrito);
    };

    const addListeners = () => {
        const modal = document.querySelector(selectors.modal);
        if (modal) {
            modal.addEventListener('show.bs.modal', async () => {
                await cargarLugares();
                await cargarCarrito();
            });

            modal.addEventListener('click', async event => {
                const removeBtn = event.target.closest('button[data-remove]');
                if (removeBtn) {
                    const [tipo, id] = removeBtn.getAttribute('data-remove').split(':');
                    try {
                        await fetchJSON(endpoints.remover, {
                            method: 'POST',
                            body: new URLSearchParams({ tipo_activo: tipo, activo_id: id }),
                        });
                        await cargarCarrito();
                        mostrarMensaje('Activo removido del carrito.', 'success');
                    } catch (err) {
                        mostrarMensaje(err.message, 'danger');
                    }
                }
            });
        }

        document.body.addEventListener('click', async event => {
            const btn = event.target.closest(selectors.btnsFacturacion);
            if (!btn) return;
            const tipo = btn.dataset.tipo;
            const id = btn.dataset.id;

            try {
                await fetchJSON(endpoints.agregar, {
                    method: 'POST',
                    body: new URLSearchParams({ tipo_activo: tipo, activo_id: id }),
                });
                await cargarCarrito();
                mostrarMensaje('Activo agregado al carrito.', 'success');
            } catch (err) {
                mostrarMensaje(err.message, 'danger');
            }
        });

        const btnLimpiar = document.querySelector(selectors.btnLimpiar);
        if (btnLimpiar) {
            btnLimpiar.addEventListener('click', async () => {
                try {
                    await fetchJSON(endpoints.limpiar, { method: 'POST' });
                    await cargarCarrito();
                    mostrarMensaje('Carrito limpiado.', 'success');
                } catch (err) {
                    mostrarMensaje(err.message, 'danger');
                }
            });
        }

        const btnEmitir = document.querySelector(selectors.btnEmitir);
        if (btnEmitir) {
            btnEmitir.addEventListener('click', async () => {
                const lugar = document.querySelector(selectors.lugarDestino);
                const obs = document.querySelector(selectors.observaciones);
                if (!lugar || !lugar.value) {
                    mostrarMensaje('Debe seleccionar un lugar de destino.', 'warning');
                    return;
                }

                try {
                    // Actualizar carrito con lugar y observaciones
                    await fetchJSON(endpoints.actualizar, {
                        method: 'POST',
                        body: new URLSearchParams({
                            lugar_destino_id: lugar.value,
                            observaciones: obs ? obs.value : '',
                        }),
                    });

                    // Emitir factura - puede devolver PDF o JSON
                    const response = await fetch(endpoints.emitir, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                        },
                    });

                    if (!response.ok) {
                        // Error en la emisión
                        const errorData = await response.json();
                        throw new Error(errorData.error || 'Error al emitir la factura');
                    }

                    const contentType = response.headers.get('content-type');
                    
                    if (contentType && contentType.includes('application/pdf')) {
                        // PDF generado exitosamente - descargarlo
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.style.display = 'none';
                        a.href = url;
                        const filename = response.headers.get('content-disposition')?.split('filename=')[1]?.replace(/"/g, '') || 'factura.pdf';
                        a.download = filename;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                        
                        await cargarCarrito();
                        mostrarMensaje('Factura emitida y PDF descargado correctamente.', 'success');
                    } else if (contentType && contentType.includes('application/json')) {
                        // Respuesta JSON - puede ser éxito con advertencia o error
                        const data = await response.json();
                        
                        if (data.success) {
                            // Factura creada pero error en PDF
                            await cargarCarrito();
                            let mensaje = `Factura ${data.factura_numero} emitida correctamente.`;
                            if (data.error_pdf) {
                                mensaje += ` Advertencia: ${data.error_pdf}`;
                                mensaje += ` Puede descargar el PDF desde el historial de facturas.`;
                                mostrarMensaje(mensaje, 'warning');
                            } else {
                                mostrarMensaje(mensaje, 'success');
                            }
                        } else {
                            throw new Error(data.error || 'Error desconocido');
                        }
                    } else {
                        throw new Error('Respuesta inesperada del servidor');
                    }
                    
                } catch (err) {
                    mostrarMensaje(err.message, 'danger');
                }
            });
        }

        // Helper para obtener cookie CSRF
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    };

    const mostrarMensaje = (texto, tipo) => {
        const container = document.querySelector(selectors.alertsContainer);
        if (!container) return;
        const alerta = document.createElement('div');
        alerta.className = `alert alert-${tipo} alert-dismissible fade show`;
        alerta.innerHTML = `${texto}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
        container.prepend(alerta);
        setTimeout(() => {
            if (alerta.parentNode) alerta.remove();
        }, 4000);
    };

    const init = () => {
        addListeners();
        renderCounter();
    };

    return { init };
})();

if (document.readyState !== 'loading') {
    FacturacionCarrito.init();
} else {
    document.addEventListener('DOMContentLoaded', () => FacturacionCarrito.init());
}



