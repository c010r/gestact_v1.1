(function() {
    console.log('[COMPUTADORA-FORM.JS] Script cargado');
    const formId = 'computadoraForm';
    const form = document.getElementById(formId);
    if (!form) {
        console.log('[COMPUTADORA-FORM.JS] Formulario no encontrado');
        return;
    }
    console.log('[COMPUTADORA-FORM.JS] Formulario encontrado, inicializando...');

    const fields = {
        nombre: document.getElementById('id_nombre'),
        numeroInventario: document.getElementById('id_numero_inventario'),
        numeroSerie: document.getElementById('id_numero_serie'),
        modelo: document.getElementById('id_modelo'),
        lugar: document.getElementById('id_lugar'),
        tipoComputadora: document.getElementById('id_tipo_computadora'),
        estado: document.getElementById('id_estado'),
        unidadEjecutora: document.getElementById('id_unidad_ejecutora'),
        unidadAsistencial: document.getElementById('id_unidad_asistencial'),
        servicio: document.getElementById('id_servicio'),
    };

    let numeroUECache = '';
    let numeroUECacheKey = '';
    const treeDataCache = new Map();

    const obtenerContenedorLugar = () => {
        if (!fields.lugar || typeof fields.lugar.closest !== 'function') {
            return null;
        }
        return fields.lugar.closest('.tree-select-container');
    };

    const obtenerMetaArbol = containerId => {
        if (!containerId) {
            return null;
        }
        if (treeDataCache.has(containerId)) {
            return treeDataCache.get(containerId);
        }
        const container = document.getElementById(containerId);
        if (!container || !container.dataset || !container.dataset.tree) {
            treeDataCache.set(containerId, null);
            return null;
        }
        try {
            const parsed = JSON.parse(container.dataset.tree);
            const mapa = new Map();
            parsed.forEach(item => {
                if (item && typeof item.id !== 'undefined') {
                    mapa.set(String(item.id), item);
                }
            });
            const meta = { lista: parsed, mapa };
            treeDataCache.set(containerId, meta);
            return meta;
        } catch (error) {
            console.error('No se pudo procesar datos del árbol de lugares:', error);
            treeDataCache.set(containerId, null);
            return null;
        }
    };

    const obtenerCodigoDesdeArbol = (containerId, lugarId) => {
        const meta = obtenerMetaArbol(containerId);
        if (!meta || !meta.mapa || !lugarId) {
            return '';
        }
        let current = meta.mapa.get(String(lugarId));
        const visitados = new Set();
        while (current && !visitados.has(current.id)) {
            if (current.codigo) {
                return current.codigo;
            }
            visitados.add(current.id);
            current = current.padre_id ? meta.mapa.get(String(current.padre_id)) : null;
        }
        return '';
    };

    const API = {
        lugar: id => `/api/lugares/${id}/`,
        unidadesEjecutoras: '/api/unidades-ejecutoras/',
        unidadEjecutora: id => `/api/unidades-ejecutoras/${id}/`,
        unidadesAsistencialesBase: '/api/unidades-asistenciales/',
        unidadesAsistenciales: ueId => `/api/unidades-asistenciales/?unidad_ejecutora=${ueId}`,
        serviciosBase: '/api/servicios-ue/',
        servicios: ueId => `/api/servicios-ue/?unidad_ejecutora=${ueId}`,
        tipos: '/api/tipos-computadora/',
        estados: '/api/estados/',
    };

    const obtenerToken = () => {
        const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return input ? input.value : '';
    };

    const fetchJSON = async (url, options = {}) => {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': obtenerToken(),
            },
            credentials: 'same-origin',
            ...options,
        });
        if (!response.ok) {
            const text = await response.text();
            throw new Error(text || 'Error en la solicitud');
        }
        return response.json();
    };

    const obtenerNumeroUE = async () => {
        const ueSelect = fields.unidadEjecutora;
        const lugarSelect = fields.lugar;
        if (ueSelect && ueSelect.value) {
            if (numeroUECache && numeroUECacheKey === `ue:${ueSelect.value}`) {
                return numeroUECache;
            }
            try {
                const data = await fetchJSON(API.unidadEjecutora(ueSelect.value));
                numeroUECache = data.numero_ue || data.codigo || '';
                numeroUECacheKey = `ue:${ueSelect.value}`;
                return numeroUECache;
            } catch (error) {
                console.error('No se pudo obtener número UE por unidad ejecutora:', error);
            }
        }
        if (lugarSelect && lugarSelect.value) {
            if (numeroUECache && numeroUECacheKey === `lugar:${lugarSelect.value}`) {
                return numeroUECache;
            }
            const contenedor = obtenerContenedorLugar();
            const codigoArbol = contenedor
                ? obtenerCodigoDesdeArbol(contenedor.id, lugarSelect.value)
                : '';
            if (codigoArbol) {
                numeroUECache = codigoArbol;
                numeroUECacheKey = `lugar:${lugarSelect.value}`;
                return numeroUECache;
            }
            try {
                const data = await fetchJSON(API.lugar(lugarSelect.value));
                numeroUECache = data.numero_ue || data.codigo || '';
                numeroUECacheKey = `lugar:${lugarSelect.value}`;
                if (numeroUECache) {
                    return numeroUECache;
                }
                const visitados = new Set([String(lugarSelect.value)]);
                let parentId = data.padre;
                while (parentId && !numeroUECache) {
                    const parentKey = String(parentId);
                    if (visitados.has(parentKey)) {
                        break;
                    }
                    visitados.add(parentKey);
                    try {
                        const parentData = await fetchJSON(API.lugar(parentId));
                        numeroUECache = parentData.numero_ue || parentData.codigo || '';
                        if (numeroUECache) {
                            numeroUECacheKey = `lugar:${lugarSelect.value}`;
                            break;
                        }
                        parentId = parentData.padre;
                    } catch (parentError) {
                        console.error('No se pudo obtener número UE por lugar padre:', parentError);
                        break;
                    }
                }
                return numeroUECache;
            } catch (error) {
                console.error('No se pudo obtener número UE por lugar:', error);
            }
        }
        numeroUECache = '';
        numeroUECacheKey = '';
        return '';
    };

    const obtenerModelo = () => {
        const select = fields.modelo;
        const option = select ? select.options[select.selectedIndex] : null;
        return option ? option.text.trim() : '';
    };

    const generarNombre = (modelo, numeroSerie) => {
        if (!modelo || !numeroSerie) {
            return '';
        }
        return `${modelo}/${numeroSerie}`;
    };

    const generarInventario = (numeroUE, modelo, numeroSerie) => {
        if (!numeroUE || !modelo || !numeroSerie) {
            return '';
        }
        return `${numeroUE}/${modelo}/${numeroSerie}`;
    };

    const actualizarCampos = async () => {
        const modelo = obtenerModelo();
        const numeroSerie = fields.numeroSerie ? fields.numeroSerie.value.trim() : '';
        const numeroUE = await obtenerNumeroUE();

        if (fields.nombre) {
            const generatedName = generarNombre(modelo, numeroSerie);
            if (generatedName) {
                fields.nombre.value = generatedName;
            }
        }

        if (fields.numeroInventario) {
            const generatedInventory = generarInventario(numeroUE, modelo, numeroSerie);
            if (generatedInventory) {
                fields.numeroInventario.value = generatedInventory;
            }
        }
    };

    const inicializarEventos = () => {
        if (fields.numeroSerie) {
            fields.numeroSerie.addEventListener('input', actualizarCampos);
        }
        if (fields.modelo) {
            fields.modelo.addEventListener('change', actualizarCampos);
        }
        if (fields.lugar) {
            fields.lugar.addEventListener('change', actualizarCampos);
        }
        if (fields.unidadEjecutora) {
            fields.unidadEjecutora.addEventListener('change', async () => {
                await actualizarCatalogosDependientes();
                await actualizarCampos();
            });
        }
    };

    document.addEventListener('tree-select:selection', event => {
        if (!event || !event.detail || !fields.lugar || !fields.lugar.name) {
            return;
        }
        const { fieldName, item, containerId } = event.detail;
        if (fieldName !== fields.lugar.name) {
            return;
        }
        let contenedorId = containerId;
        if (!contenedorId) {
            const contenedorElemento = obtenerContenedorLugar();
            contenedorId = contenedorElemento ? contenedorElemento.id : '';
        }
        const codigoArbol = contenedorId && item
            ? obtenerCodigoDesdeArbol(contenedorId, item.id)
            : '';
        numeroUECache = codigoArbol || (item && (item.codigo || item.numero_ue)) || '';
        numeroUECacheKey = item ? `lugar:${item.id}` : '';
        actualizarCampos();
    });

    const limpiarModal = modalId => {
        const modal = document.getElementById(modalId);
        if (!modal) {
            return;
        }
        modal.querySelectorAll('input, textarea').forEach(field => {
            field.value = '';
        });
    };

    const agregarOpcion = (select, { id, nombre }) => {
        if (!select) {
            return;
        }
        const option = document.createElement('option');
        option.value = id;
        option.textContent = nombre;
        option.selected = true;
        select.appendChild(option);
    };

    const mostrarError = mensaje => {
        const alertContainer = document.createElement('div');
        alertContainer.className = 'alert alert-danger alert-dismissible fade show mt-3';
        alertContainer.innerHTML = `
            <i class="bi bi-exclamation-triangle-fill me-2"></i>${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        form.prepend(alertContainer);
        setTimeout(() => {
            alertContainer.remove();
        }, 5000);
    };

    const guardarCatalogo = async (modalId, apiUrl, selectField, payloadBuilder) => {
        const modal = document.getElementById(modalId);
        const nombre = document.getElementById(`${modalId}-nombre`);
        const comentarios = document.getElementById(`${modalId}-comentarios`);
        if (!modal || !nombre || nombre.value.trim() === '') {
            mostrarError('El nombre es obligatorio.');
            return;
        }
        try {
            const basePayload = {
                nombre: nombre.value.trim(),
                comentarios: comentarios ? comentarios.value.trim() : '',
            };
            const payload = payloadBuilder ? payloadBuilder(basePayload) : basePayload;
            if (!payload) {
                return;
            }
            const data = await fetchJSON(apiUrl, {
                method: 'POST',
                body: JSON.stringify(payload),
            });
            agregarOpcion(selectField, { id: data.id, nombre: data.nombre });
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            if (bootstrapModal) {
                bootstrapModal.hide();
            }
            limpiarModal(modalId);
        } catch (error) {
            console.error('Error al guardar catálogo:', error);
            mostrarError('No se pudo guardar el registro.');
        }
    };

    const inicializarModales = () => {
        const tipoGuardar = document.getElementById('modal-tipo-guardar');
        const estadoGuardar = document.getElementById('modal-estado-guardar');
        if (tipoGuardar) {
            tipoGuardar.addEventListener('click', () =>
                guardarCatalogo('modal-tipo', API.tipos, fields.tipoComputadora)
            );
        }
        if (estadoGuardar) {
            estadoGuardar.addEventListener('click', () =>
                guardarCatalogo('modal-estado', API.estados, fields.estado)
            );
        }
        const ueGuardar = document.getElementById('modal-ue-guardar');
        if (ueGuardar) {
            ueGuardar.addEventListener('click', () =>
                guardarCatalogo('modal-ue', API.unidadesEjecutoras, fields.unidadEjecutora, values => {
                    const numeroInput = document.getElementById('modal-ue-numero');
                    if (!numeroInput || numeroInput.value.trim() === '') {
                        mostrarError('El número de unidad ejecutora es obligatorio.');
                        return null;
                    }
                    return {
                        numero_ue: numeroInput.value.trim(),
                        nombre: values.nombre,
                        comentarios: values.comentarios,
                    };
                })
            );
        }
        const uaGuardar = document.getElementById('modal-ua-guardar');
        if (uaGuardar) {
            uaGuardar.addEventListener('click', () => {
                const ueId = fields.unidadEjecutora ? fields.unidadEjecutora.value : '';
                if (!ueId) {
                    mostrarError('Seleccione primero una unidad ejecutora.');
                    return;
                }
                guardarCatalogo('modal-ua', API.unidadesAsistencialesBase, fields.unidadAsistencial, values => ({
                    nombre: values.nombre,
                    comentarios: values.comentarios,
                    unidad_ejecutora: ueId,
                }));
            });
        }
        const servicioGuardar = document.getElementById('modal-servicio-guardar');
        if (servicioGuardar) {
            servicioGuardar.addEventListener('click', () => {
                const ueId = fields.unidadEjecutora ? fields.unidadEjecutora.value : '';
                if (!ueId) {
                    mostrarError('Seleccione primero una unidad ejecutora.');
                    return;
                }
                guardarCatalogo('modal-servicio', API.serviciosBase, fields.servicio, values => ({
                    nombre: values.nombre,
                    comentarios: values.comentarios,
                    unidad_ejecutora: ueId,
                }));
            });
        }
        ['modal-tipo', 'modal-estado', 'modal-ue', 'modal-ua', 'modal-servicio'].forEach(modalId => {
            const modal = document.getElementById(modalId);
            if (!modal) {
                return;
            }
            ['shown.bs.modal', 'hidden.bs.modal'].forEach(eventName => {
                modal.addEventListener(eventName, () => limpiarModal(modalId));
            });
        });
    };

    const validarAntesDeEnviar = () => {
        console.log('[VALIDACIÓN] Configurando listener de submit');
        form.addEventListener('submit', async event => {
            console.log('[VALIDACIÓN] Submit detectado, actualizando campos...');
            await actualizarCampos();
            const valores = {
                nombre: fields.nombre ? fields.nombre.value.trim() : '',
                inventario: fields.numeroInventario ? fields.numeroInventario.value.trim() : '',
                serie: fields.numeroSerie ? fields.numeroSerie.value.trim() : '',
            };
            
            console.log('[VALIDACIÓN SUBMIT]', valores);
            
            // Solo validar si estamos creando (no en edición)
            const isEditing = form.action.includes('/editar/');
            console.log('[VALIDACIÓN] ¿Es edición?', isEditing, 'Action:', form.action);
            
            if (!isEditing && (!valores.nombre || !valores.inventario || !valores.serie)) {
                console.log('[VALIDACIÓN] BLOQUEANDO submit - campos vacíos');
                event.preventDefault();
                mostrarError('Verifique número de serie, modelo y lugar para generar nombre e inventario.');
            } else {
                console.log('[VALIDACIÓN] ✅ Submit permitido');
            }
        });
    };

    const actualizarCatalogosDependientes = async () => {
        const ueSelect = fields.unidadEjecutora;
        if (!ueSelect) {
            return;
        }
        const ueId = ueSelect.value;
        const isRAP = ueSelect.options[ueSelect.selectedIndex] && ueSelect.options[ueSelect.selectedIndex].text.toUpperCase().startsWith('RAP');
        if (fields.unidadAsistencial) {
            fields.unidadAsistencial.innerHTML = '<option value="">---------</option>';
        }
        if (fields.servicio) {
            fields.servicio.innerHTML = '<option value="">---------</option>';
        }
        if (!ueId) {
            return;
        }
        try {
            if (isRAP && fields.unidadAsistencial) {
                const data = await fetchJSON(API.unidadesAsistenciales(ueId));
                data.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.id;
                    option.textContent = item.nombre;
                    fields.unidadAsistencial.appendChild(option);
                });
            } else if (!isRAP && fields.servicio) {
                const data = await fetchJSON(API.servicios(ueId));
                data.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.id;
                    option.textContent = item.nombre;
                    fields.servicio.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error al cargar catálogos dependientes:', error);
        }
    };

    console.log('[COMPUTADORA-FORM.JS] Ejecutando inicializaciones...');
    inicializarEventos();
    inicializarModales();
    validarAntesDeEnviar();
    actualizarCampos();
    console.log('[COMPUTADORA-FORM.JS] ✅ Inicialización completada');
})();
