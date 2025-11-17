/**
 * Modal para crear jerarquías completas de lugares.
 */

(function() {
    'use strict';

    const NIVELES = [1, 2, 3, 4, 5, 6, 7];

    class LugarHierarchyModal {
        constructor() {
            this.modal = document.getElementById('modalNuevoLugar');
            if (!this.modal) {
                return;
            }

            this.parentSelect = document.getElementById('modal-lugar-padre-existente');
            this.saveButton = document.getElementById('modal-lugar-guardar-jerarquia');
            this.preview = document.getElementById('jerarquia-preview');

            this.currentContainer = null;
            this.treeData = [];
            this.treeDataById = {};
            this.tipoNiveles = {};
            this.currentSelection = null;
            this.csrfToken = null;
            this.saveButtonDefault = this.saveButton ? this.saveButton.innerHTML : '';

            this.levels = this.buildLevelConfig();
            this.levelMap = {};
            this.levels.forEach(cfg => {
                this.levelMap[cfg.nivel] = cfg;
            });

            this.registerEvents();
        }

        buildLevelConfig() {
            return NIVELES.map(nivel => {
                const toggle = document.getElementById(`nivel-${nivel}-activo`);
                const container = document.getElementById(`nivel-${nivel}-container`);
                const fields = container ? container.querySelector('.nivel-fields') : null;
                const inputs = fields ? Array.from(fields.querySelectorAll('input')) : [];
                return { nivel, toggle, container, fields, inputs };
            });
        }

        registerEvents() {
            if (this.modal) {
                this.modal.addEventListener('show.bs.modal', (event) => this.onModalShow(event));
                this.modal.addEventListener('shown.bs.modal', () => this.onModalShown());
                this.modal.addEventListener('hidden.bs.modal', () => this.onModalHidden());
            }

            if (this.parentSelect) {
                this.parentSelect.addEventListener('change', () => this.onParentChange());
            }

            if (this.saveButton) {
                this.saveButton.addEventListener('click', () => this.onSubmit());
            }

            this.levels.forEach(config => {
                if (config.toggle) {
                    config.toggle.addEventListener('change', () => {
                        if (config.toggle.checked) {
                            this.checkLevel(config);
                        } else {
                            this.uncheckLevel(config);
                        }
                    });
                }
                config.inputs.forEach(input => {
                    input.addEventListener('input', () => this.updatePreview());
                });
            });

            document.addEventListener('tree-select:open-modal', (event) => {
                const detail = event.detail || {};
                this.applyTreeContext(detail);
            });

            document.addEventListener('tree-select:selection', (event) => {
                const detail = event.detail || {};
                this.applyTreeContext(detail);
                if (detail.item) {
                    this.currentSelection = {
                        id: String(detail.item.id),
                        nivel: detail.item.nivel || 0
                    };
                }
                if (this.isModalVisible()) {
                    this.populateParentSelect();
                    this.preselectParent();
                    this.updatePreview();
                }
            });
        }

        applyTreeContext(detail) {
            if (detail.tipoNiveles) {
                this.mergeTipoNivelMap(detail.tipoNiveles);
            }

            if (detail.containerId) {
                const container = document.getElementById(detail.containerId);
                if (container) {
                    this.setCurrentContainer(container);
                }
            }

            if (detail.item) {
                this.currentSelection = {
                    id: String(detail.item.id),
                    nivel: detail.item.nivel || 0
                };
            }
        }

        onModalShow(event) {
            if (!this.currentContainer && event && event.relatedTarget) {
                const container = event.relatedTarget.closest('.tree-select-container');
                if (container) {
                    this.setCurrentContainer(container);
                }
            }
        }

        onModalShown() {
            this.populateParentSelect();
            this.preselectParent();
            this.updatePreview();
        }

        onModalHidden() {
            this.resetForm();
        }

        onParentChange() {
            const padreNivel = this.getPadreNivel();
            this.syncLevels(padreNivel);
            this.updatePreview();
        }

        isModalVisible() {
            return this.modal && this.modal.classList.contains('show');
        }

        setCurrentContainer(container) {
            if (!container) {
                return;
            }
            this.currentContainer = container;

            this.treeData = this.parseTreeData(container.dataset.tree);
            this.treeDataById = {};
            this.treeData.forEach(item => {
                this.treeDataById[String(item.id)] = item;
                if (item.tipo_nivel_id) {
                    this.ensureTipoNivelMeta(item.nivel, {
                        id: item.tipo_nivel_id,
                        requiereCodigo: item.tipo_nivel_requiere_codigo
                    });
                }
            });

            const listaTipos = this.parseTipoNiveles(container.dataset.tiposNivel);
            this.mergeTipoNivelList(listaTipos);
        }

        parseTreeData(raw) {
            if (!raw) {
                return [];
            }
            try {
                const data = JSON.parse(raw);
                return Array.isArray(data) ? data : [];
            } catch (error) {
                console.error('[Modal Lugares] No se pudo cargar data-tree', error);
                return [];
            }
        }

        parseTipoNiveles(raw) {
            if (!raw) {
                return [];
            }
            try {
                const data = JSON.parse(raw);
                if (Array.isArray(data)) {
                    return data;
                }
                if (data && Array.isArray(data.results)) {
                    return data.results;
                }
            } catch (error) {
                console.error('[Modal Lugares] No se pudo cargar data-tipos-nivel', error);
            }
            return [];
        }

        mergeTipoNivelMap(map) {
            Object.keys(map || {}).forEach(nivel => {
                const value = map[nivel];
                if (value && typeof value === 'object') {
                    this.ensureTipoNivelMeta(nivel, {
                        id: value.id,
                        requiereCodigo: value.requiereCodigo
                    });
                } else if (value) {
                    this.ensureTipoNivelMeta(nivel, { id: value });
                }
            });
        }

        mergeTipoNivelList(list) {
            (list || []).forEach(item => {
                if (item && item.nivel && item.id) {
                    this.ensureTipoNivelMeta(item.nivel, {
                        id: item.id,
                        requiereCodigo: item.requiere_codigo
                    });
                }
            });
        }

        ensureTipoNivelMeta(nivel, meta = {}) {
            if (!nivel) {
                return;
            }
            const previous = this.tipoNiveles[nivel] || {};
            const hasRequiere = Object.prototype.hasOwnProperty.call(meta, 'requiereCodigo');
            this.tipoNiveles[nivel] = {
                id: meta.id || previous.id || null,
                requiereCodigo: hasRequiere
                    ? Boolean(meta.requiereCodigo)
                    : Boolean(previous.requiereCodigo)
            };
        }

        populateParentSelect() {
            if (!this.parentSelect) {
                return;
            }

            const fragment = document.createDocumentFragment();
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Crear desde la raíz (nueva UE)';
            fragment.appendChild(defaultOption);

            const lugaresOrdenados = [...this.treeData].sort((a, b) => {
                if (a.nivel === b.nivel) {
                    return (a.nombre || '').localeCompare(b.nombre || '', 'es', { sensitivity: 'base' });
                }
                return a.nivel - b.nivel;
            });

            lugaresOrdenados.forEach(lugar => {
                if (lugar.activo === false) {
                    return;
                }
                const option = document.createElement('option');
                option.value = lugar.id;
                option.dataset.nivel = lugar.nivel;
                option.dataset.nombre = lugar.nombre_completo || lugar.nombre || '';
                if (lugar.tipo_nivel_id) {
                    option.dataset.tipoId = lugar.tipo_nivel_id;
                    option.dataset.requiereCodigo = lugar.tipo_nivel_requiere_codigo ? '1' : '0';
                    this.ensureTipoNivelMeta(lugar.nivel, {
                        id: lugar.tipo_nivel_id,
                        requiereCodigo: lugar.tipo_nivel_requiere_codigo
                    });
                }
                option.textContent = `${this.getIconForLevel(lugar.nivel)} ${lugar.nombre_completo || lugar.nombre}`;
                fragment.appendChild(option);
            });

            this.parentSelect.innerHTML = '';
            this.parentSelect.appendChild(fragment);
        }

        preselectParent() {
            if (!this.parentSelect) {
                return;
            }

            let selectedId = this.currentSelection ? this.currentSelection.id : '';
            if (!selectedId && this.currentContainer) {
                const input = this.currentContainer.querySelector('.tree-select-input');
                if (input && input.value) {
                    selectedId = input.value;
                }
            }

            if (selectedId) {
                const option = this.parentSelect.querySelector(`option[value="${selectedId}"]`);
                if (option) {
                    this.parentSelect.value = selectedId;
                } else {
                    this.parentSelect.value = '';
                }
            } else {
                this.parentSelect.value = '';
            }

            const padreNivel = this.getPadreNivel();
            this.syncLevels(padreNivel);
        }

        getPadreNivel() {
            if (!this.parentSelect) {
                return 0;
            }
            const option = this.parentSelect.selectedOptions[0];
            return option ? parseInt(option.dataset.nivel || '0', 10) : 0;
        }

        syncLevels(padreNivel) {
            this.levels.forEach(config => {
                if (!config.toggle) {
                    return;
                }

                if (config.nivel <= padreNivel) {
                    this.disableLevel(config);
                } else {
                    this.enableLevel(config);
                    if (config.toggle.checked) {
                        this.uncheckLevel(config, { updatePreview: false });
                    } else {
                        this.hideFields(config);
                        this.clearInputs(config);
                    }
                }
            });

            if (padreNivel >= 7) {
                this.preview.innerHTML = '<em class="text-muted">El lugar seleccionado es de nivel máximo; no es posible crear nuevos niveles.</em>';
                return;
            }

            const siguienteNivel = padreNivel + 1;
            const siguienteConfig = this.levelMap[siguienteNivel];
            if (siguienteConfig) {
                this.checkLevel(siguienteConfig, { autoFocus: true, updatePreview: false });
            }

            this.updatePreview();
        }

        disableLevel(config) {
            if (!config.toggle) {
                return;
            }
            config.toggle.checked = false;
            config.toggle.disabled = true;
            if (config.container) {
                config.container.classList.add('nivel-bloqueado');
            }
            this.hideFields(config);
            this.clearInputs(config);
        }

        enableLevel(config) {
            if (!config.toggle) {
                return;
            }
            config.toggle.disabled = false;
            if (config.container) {
                config.container.classList.remove('nivel-bloqueado');
            }
        }

        checkLevel(config, options = {}) {
            if (!config.toggle || config.toggle.disabled) {
                return;
            }
            const autoFocus = options.autoFocus !== false;
            const updatePreview = options.updatePreview !== false;

            config.toggle.checked = true;
            this.showFields(config);

            for (let nivel = 1; nivel < config.nivel; nivel++) {
                const previous = this.levelMap[nivel];
                if (previous && previous.toggle && !previous.toggle.disabled && !previous.toggle.checked) {
                    this.checkLevel(previous, { autoFocus: false, updatePreview: false });
                }
            }

            if (autoFocus) {
                this.focusFirstInput(config.nivel);
            }
            if (updatePreview) {
                this.updatePreview();
            }
        }

        uncheckLevel(config, options = {}) {
            if (!config.toggle) {
                return;
            }
            const updatePreview = options.updatePreview !== false;

            config.toggle.checked = false;
            this.hideFields(config);
            this.clearInputs(config);

            for (let nivel = config.nivel + 1; nivel <= 7; nivel++) {
                const next = this.levelMap[nivel];
                if (next && next.toggle && next.toggle.checked) {
                    this.uncheckLevel(next, { updatePreview: false });
                }
                if (next && next.toggle && !next.toggle.disabled) {
                    next.toggle.checked = false;
                    this.hideFields(next);
                    this.clearInputs(next);
                }
            }

            if (updatePreview) {
                this.updatePreview();
            }
        }

        showFields(config) {
            if (config.fields) {
                config.fields.style.display = 'block';
            }
        }

        hideFields(config) {
            if (config.fields) {
                config.fields.style.display = 'none';
            }
        }

        clearInputs(config) {
            config.inputs.forEach(input => {
                input.value = '';
            });
        }

        focusFirstInput(nivel) {
            const input = document.getElementById(`nivel-${nivel}-nombre`);
            if (input) {
                setTimeout(() => input.focus(), 120);
            }
        }

        updatePreview() {
            if (!this.preview) {
                return;
            }

            const padreOption = this.parentSelect ? this.parentSelect.selectedOptions[0] : null;
            const padreNivel = padreOption ? parseInt(padreOption.dataset.nivel || '0', 10) : 0;

            const fragment = document.createDocumentFragment();
            let tieneContenido = false;

            if (padreOption) {
                const padreDiv = document.createElement('div');
                padreDiv.className = 'mb-2';
                padreDiv.innerHTML = `<strong>Partir desde:</strong> ${padreOption.text}`;
                fragment.appendChild(padreDiv);
                tieneContenido = true;
            }

            if (padreNivel >= 7) {
                const info = document.createElement('em');
                info.className = 'text-muted';
                info.textContent = 'El lugar seleccionado es de nivel máximo; no es posible crear nuevos niveles.';
                fragment.appendChild(info);
                this.preview.innerHTML = '';
                this.preview.appendChild(fragment);
                return;
            }

            const nivelesActivos = this.levels.filter(config => config.toggle && config.toggle.checked && config.nivel > padreNivel);

            if (nivelesActivos.length === 0) {
                const mensaje = document.createElement('em');
                mensaje.className = 'text-muted';
                mensaje.textContent = padreOption
                    ? 'Marque los niveles que desea agregar...'
                    : 'Marque los niveles que desea crear para ver la vista previa...';
                fragment.appendChild(mensaje);
                this.preview.innerHTML = '';
                this.preview.appendChild(fragment);
                return;
            }

            const contenedor = document.createElement('div');
            contenedor.className = padreOption ? 'ms-3' : '';

            nivelesActivos.forEach(config => {
                const nombreInput = document.getElementById(`nivel-${config.nivel}-nombre`);
                const nombre = nombreInput && nombreInput.value.trim() ? nombreInput.value.trim() : `[Nivel ${config.nivel} - Sin nombre]`;
                const indent = '&nbsp;&nbsp;&nbsp;&nbsp;'.repeat(Math.max(0, config.nivel - padreNivel - 1));
                const prefijo = config.nivel > padreNivel + 1 ? '└─ ' : '';
                const row = document.createElement('div');
                row.innerHTML = `${indent}${prefijo}${this.getIconForLevel(config.nivel)} <strong>${nombre}</strong>`;
                contenedor.appendChild(row);
            });

            fragment.appendChild(contenedor);
            this.preview.innerHTML = '';
            this.preview.appendChild(fragment);
        }

        clearPreview() {
            if (this.preview) {
                this.preview.innerHTML = '<em class="text-muted">Marque los niveles que desea crear para ver la vista previa...</em>';
            }
        }

        getTipoNivelInfo(nivel) {
            if (this.tipoNiveles[nivel]) {
                return this.tipoNiveles[nivel];
            }
            const matching = this.treeData.find(item => item.nivel === nivel && item.tipo_nivel_id);
            if (matching) {
                this.ensureTipoNivelMeta(nivel, {
                    id: matching.tipo_nivel_id,
                    requiereCodigo: matching.tipo_nivel_requiere_codigo
                });
                return this.tipoNiveles[nivel];
            }
            return null;
        }

        getTipoNivelId(nivel) {
            const info = this.getTipoNivelInfo(nivel);
            return info ? info.id : null;
        }

        collectLevelsToCreate(padreNivel) {
            const niveles = [];

            for (const config of this.levels) {
                if (!config.toggle || config.nivel <= padreNivel) {
                    continue;
                }
                if (!config.toggle.checked) {
                    continue;
                }

                const nombreInput = document.getElementById(`nivel-${config.nivel}-nombre`);
                if (!nombreInput || !nombreInput.value.trim()) {
                    window.alert(`Por favor, ingrese un nombre para el Nivel ${config.nivel}`);
                    if (nombreInput) {
                        nombreInput.focus();
                    }
                    return null;
                }

                const tipoNivelId = this.getTipoNivelId(config.nivel);
                if (!tipoNivelId) {
                    window.alert(`No se encontró el tipo de nivel correspondiente al Nivel ${config.nivel}. Recargue la página e intente nuevamente.`);
                    return null;
                }

                const codigoInput = document.getElementById(`nivel-${config.nivel}-codigo`);
                const descripcionInput = document.getElementById(`nivel-${config.nivel}-descripcion`);
                const tipoInfo = this.getTipoNivelInfo(config.nivel);
                const requiereCodigo = tipoInfo ? Boolean(tipoInfo.requiereCodigo) : false;

                if (requiereCodigo && (!codigoInput || !codigoInput.value.trim())) {
                    window.alert(`El tipo de nivel seleccionado requiere un código en el Nivel ${config.nivel}.`);
                    if (codigoInput) {
                        codigoInput.focus();
                    }
                    return null;
                }

                niveles.push({
                    nivel: config.nivel,
                    nombre: nombreInput.value.trim(),
                    codigo: codigoInput && codigoInput.value.trim() ? codigoInput.value.trim() : null,
                    comentarios: descripcionInput && descripcionInput.value.trim() ? descripcionInput.value.trim() : null,
                    tipoNivelId,
                    requiereCodigo
                });
            }

            return niveles;
        }

        validateConsecutiveLevels(niveles, padreNivel) {
            if (!niveles || niveles.length === 0) {
                window.alert('Por favor, active y complete al menos un nivel para crear.');
                return false;
            }

            let esperado = padreNivel + 1;
            if (padreNivel === 0) {
                esperado = 1;
            }

            for (const item of niveles) {
                if (item.nivel !== esperado) {
                    window.alert(`La jerarquía debe ser consecutiva. Falta el nivel ${esperado}.`);
                    return false;
                }
                esperado += 1;
            }

            if (padreNivel === 0 && niveles[0].nivel !== 1) {
                window.alert('Si no selecciona un lugar padre, debe comenzar desde el Nivel 1 (Unidad Ejecutora).');
                return false;
            }

            if (padreNivel > 0 && niveles[0].nivel !== padreNivel + 1) {
                window.alert(`Si parte desde un lugar de nivel ${padreNivel}, el primer nivel a crear debe ser ${padreNivel + 1}.`);
                return false;
            }

            return true;
        }

        ensureCsrfToken() {
            if (this.csrfToken) {
                return this.csrfToken;
            }
            const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (tokenInput && tokenInput.value) {
                this.csrfToken = tokenInput.value;
                return this.csrfToken;
            }
            window.alert('No se encontró el token CSRF. Recargue la página e intente nuevamente.');
            return null;
        }

        async onSubmit() {
            if (!this.saveButton || this.saveButton.disabled) {
                return;
            }

            const padreInfo = this.getPadreInfo();
            const niveles = this.collectLevelsToCreate(padreInfo.nivel);
            if (!niveles) {
                return;
            }

            if (!this.validateConsecutiveLevels(niveles, padreInfo.nivel)) {
                return;
            }

            const csrf = this.ensureCsrfToken();
            if (!csrf) {
                return;
            }

            this.disableSaveButton();

            try {
                await this.createHierarchy({ niveles, padreInfo, csrf });
                window.alert(`✅ Jerarquía creada exitosamente: ${niveles.length} niveles`);
                const modalInstance = window.bootstrap ? window.bootstrap.Modal.getInstance(this.modal) : null;
                if (modalInstance) {
                    modalInstance.hide();
                }
                this.resetForm();
                window.location.reload();
            } catch (error) {
                console.error('[Modal Lugares] Error al crear jerarquía', error);
                window.alert(`❌ Error al crear la jerarquía: ${error.message}`);
            } finally {
                this.restoreSaveButton();
            }
        }

        getPadreInfo() {
            if (!this.parentSelect || !this.parentSelect.value) {
                return { id: null, nivel: 0 };
            }
            const option = this.parentSelect.selectedOptions[0];
            const nivel = option ? parseInt(option.dataset.nivel || '0', 10) : 0;
            return {
                id: this.parentSelect.value,
                nivel
            };
        }

        async createHierarchy({ niveles, padreInfo, csrf }) {
            let padreActualId = padreInfo.id ? parseInt(padreInfo.id, 10) : null;

            for (const nivelData of niveles) {
                const payload = {
                    nombre: nivelData.nombre,
                    tipo_nivel: nivelData.tipoNivelId,
                    nivel: nivelData.nivel,
                    activo: true
                };

                if (nivelData.codigo) {
                    payload.codigo = nivelData.codigo;
                }
                if (nivelData.comentarios) {
                    payload.comentarios = nivelData.comentarios;
                }
                if (padreActualId) {
                    payload.padre = padreActualId;
                }

                const response = await fetch('/api/lugares/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrf
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    let mensaje = `Error desconocido en nivel ${nivelData.nivel}`;
                    try {
                        const errorData = await response.json();
                        mensaje = this.extractErrorMessage(errorData) || mensaje;
                    } catch (parseError) {
                        // Ignorar errores de parseo
                    }
                    throw new Error(mensaje);
                }

                const json = await response.json();
                padreActualId = json.id;
            }
        }

        extractErrorMessage(errorData) {
            if (!errorData) {
                return null;
            }
            if (typeof errorData === 'string') {
                return errorData;
            }
            if (errorData.detail) {
                return Array.isArray(errorData.detail) ? errorData.detail.join(' ') : errorData.detail;
            }
            if (errorData.error) {
                return Array.isArray(errorData.error) ? errorData.error.join(' ') : errorData.error;
            }
            if (errorData.nombre) {
                return Array.isArray(errorData.nombre) ? errorData.nombre.join(' ') : errorData.nombre;
            }
            const firstKey = Object.keys(errorData)[0];
            if (firstKey) {
                const value = errorData[firstKey];
                if (Array.isArray(value)) {
                    return value.join(' ');
                }
                return String(value);
            }
            return null;
        }

        disableSaveButton() {
            if (!this.saveButton) {
                return;
            }
            this.saveButton.disabled = true;
            this.saveButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Guardando jerarquía...';
        }

        restoreSaveButton() {
            if (!this.saveButton) {
                return;
            }
            this.saveButton.disabled = false;
            this.saveButton.innerHTML = this.saveButtonDefault || '<i class="bi bi-save"></i> Guardar Jerarquía';
        }

        resetForm() {
            if (this.parentSelect) {
                this.parentSelect.value = '';
            }
            this.levels.forEach(config => {
                if (config.toggle) {
                    config.toggle.disabled = false;
                    config.toggle.checked = false;
                }
                if (config.container) {
                    config.container.classList.remove('nivel-bloqueado');
                }
                this.hideFields(config);
                this.clearInputs(config);
            });
            this.currentSelection = null;
            this.clearPreview();
        }

        getIconForLevel(nivel) {
            const icons = {
                1: '📁',
                2: '🏢',
                3: '🏥',
                4: '📋',
                5: '🔧',
                6: '📍',
                7: '💺'
            };
            return icons[nivel] || '•';
        }
    }

    function initModal() {
        new LugarHierarchyModal();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initModal);
    } else {
        initModal();
    }
})();/**
 * Gestión del modal de creación de jerarquía completa de lugares
 */

(function() {
    'use strict';

    const modal = document.getElementById('modalNuevoLugar');
    if (!modal) return;

    const padreExistenteSelect = document.getElementById('modal-lugar-padre-existente');
    const guardarBtn = document.getElementById('modal-lugar-guardar-jerarquia');
    const previewDiv = document.getElementById('jerarquia-preview');

    let currentTreeContainer = null;
    let ultimoPadreSeleccionado = null;
    const tipoNivelCache = {};

    // Mapeo de nivel a tipo
    const nivelIcono = {
        1: '📁',
        2: '🏢',
        3: '🏥',
        4: '📋',
        5: '🔧',
        6: '📍',
        7: '💺'
    };

    // Cargar lugares existentes en el selector de padre
    function obtenerTreeContainer() {
        if (currentTreeContainer) {
            return currentTreeContainer;
        }
        return document.querySelector('.tree-select-container');
    }

    function asegurarCacheTiposNivel(treeContainer) {
        const contenedor = treeContainer || obtenerTreeContainer();
        if (!contenedor) {
            return;
        }

        if (Object.keys(tipoNivelCache).length >= 7) {
            return;
        }

        const tiposRaw = contenedor.getAttribute('data-tipos-nivel');
        if (!tiposRaw) {
            return;
        }

        try {
            const parsed = JSON.parse(tiposRaw);
            const tipos = Array.isArray(parsed)
                ? parsed
                : Array.isArray(parsed?.results)
                    ? parsed.results
                    : [];

            tipos.forEach(tipo => {
                if (tipo && tipo.nivel && tipo.id && !tipoNivelCache[tipo.nivel]) {
                    tipoNivelCache[tipo.nivel] = tipo.id;
                }
            });
        } catch (error) {
            console.error('[Modal Lugares] No se pudo procesar data-tipos-nivel', error);
        }
    }

    function cargarLugaresExistentes() {
        const treeContainer = obtenerTreeContainer();
        if (!treeContainer) return;

        const treeData = treeContainer.getAttribute('data-tree');
        if (!treeData) return;

        try {
            const lugares = JSON.parse(treeData);
            asegurarCacheTiposNivel(treeContainer);

            // Limpiar y llenar el select
            padreExistenteSelect.innerHTML = '';
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Crear desde la raíz (nueva UE)';
            padreExistenteSelect.appendChild(defaultOption);

            lugares.forEach(lugar => {
                if (lugar.activo) {
                    if (lugar.tipo_nivel_id && !tipoNivelCache[lugar.nivel]) {
                        tipoNivelCache[lugar.nivel] = lugar.tipo_nivel_id;
                    }

                    const option = document.createElement('option');
                    option.value = lugar.id;
                    option.setAttribute('data-nivel', lugar.nivel);
                    option.setAttribute('data-nombre', lugar.nombre_completo || lugar.nombre);
                    if (lugar.tipo_nivel_id) {
                        option.setAttribute('data-tipo-id', lugar.tipo_nivel_id);
                    }
                    option.textContent = `${nivelIcono[lugar.nivel]} ${lugar.nombre_completo || lugar.nombre}`;
                    padreExistenteSelect.appendChild(option);
                }
            });

            console.debug('[Modal Lugares] Opciones cargadas', {
                total: padreExistenteSelect.options.length,
                primera: padreExistenteSelect.options[0]?.text,
                seleccionActual: padreExistenteSelect.value
            });
        } catch (e) {
            console.error('Error al cargar lugares:', e);
        }
    }

    /**
     * Ajusta los interruptores según el padre seleccionado
     */
    function sincronizarTogglesConPadre() {
        const padreId = padreExistenteSelect.value;

                    asegurarCacheTiposNivel(obtenerTreeContainer());
        const opcionSeleccionada = padreId ? padreExistenteSelect.selectedOptions[0] : null;
        const padreNivel = opcionSeleccionada ? parseInt(opcionSeleccionada.getAttribute('data-nivel') || '0', 10) : 0;

        if (padreId) {
            ultimoPadreSeleccionado = {
                id: padreId,
                nivel: padreNivel,
                nombre: opcionSeleccionada ? opcionSeleccionada.getAttribute('data-nombre') : ''
            };
        } else {
            ultimoPadreSeleccionado = null;
        }

        for (let nivel = 1; nivel <= 7; nivel++) {
            const toggle = document.getElementById(`nivel-${nivel}-activo`);
            const container = document.getElementById(`nivel-${nivel}-container`);
            if (!toggle || !container) continue;

            const fields = container.querySelector('.nivel-fields');

            if (nivel <= padreNivel) {
                toggle.checked = false;
                toggle.disabled = true;
                container.classList.add('nivel-bloqueado');
                if (fields) {
                    fields.style.display = 'none';
                    fields.querySelectorAll('input').forEach(input => input.value = '');
                }
            } else {
                const estabaDeshabilitado = toggle.disabled;
                toggle.disabled = false;
                container.classList.remove('nivel-bloqueado');

                // Si venimos de estar deshabilitado, aseguramos estado limpio
                if (estabaDeshabilitado) {
                    toggle.checked = false;
                    if (fields) {
                        fields.style.display = 'none';
                        fields.querySelectorAll('input').forEach(input => input.value = '');
                    }
                }
            }
        }

        if (padreId) {
            if (padreNivel >= 7) {
                previewDiv.innerHTML = '<em class="text-muted">El lugar seleccionado es de nivel máximo. No es posible agregar hijos.</em>';
                return;
            }

            // Activar automáticamente el primer nivel disponible
            const siguienteNivel = padreNivel + 1;
            const siguienteToggle = document.getElementById(`nivel-${siguienteNivel}-activo`);
            if (siguienteToggle && !siguienteToggle.disabled) {
                if (!siguienteToggle.checked) {
                    siguienteToggle.checked = true;
                    siguienteToggle.dispatchEvent(new Event('change'));
                }

                const container = document.getElementById(`nivel-${siguienteNivel}-container`);
                if (container) {
                    const nombreInput = container.querySelector('.nivel-fields input[id$="-nombre"]');
                    if (nombreInput) {
                        setTimeout(() => nombreInput.focus(), 150);
                    }
                }
            }

            // Desmarcar niveles superiores por defecto
            for (let nivel = siguienteNivel + 1; nivel <= 7; nivel++) {
                const toggle = document.getElementById(`nivel-${nivel}-activo`);
                if (toggle && !toggle.disabled && toggle.checked) {
                    toggle.checked = false;
                    toggle.dispatchEvent(new Event('change'));
                }
            }
        }
    }

    /**
     * Preselecciona el padre con base en el valor del widget de árbol
     */
    function preseleccionarPadre() {
        let valorSeleccionado = '';

        if (ultimoPadreSeleccionado && ultimoPadreSeleccionado.id) {
            valorSeleccionado = ultimoPadreSeleccionado.id;
        } else {
            const treeContainer = obtenerTreeContainer();
            const treeSelectInput = treeContainer ? treeContainer.querySelector('.tree-select-input') : null;
            valorSeleccionado = treeSelectInput ? treeSelectInput.value : '';
        }

        if (valorSeleccionado) {
            const opcion = padreExistenteSelect.querySelector(`option[value="${valorSeleccionado}"]`);
            padreExistenteSelect.value = opcion ? valorSeleccionado : '';
        } else {
            padreExistenteSelect.value = '';
        }

        sincronizarTogglesConPadre();
    }

    // Inicializar: cargar lugares existentes cuando se abre el modal
    modal.addEventListener('show.bs.modal', function(event) {
        if (!currentTreeContainer && event.relatedTarget) {
            currentTreeContainer = event.relatedTarget.closest('.tree-select-container');
        }
        if (currentTreeContainer) {
            const debugInput = currentTreeContainer.querySelector('.tree-select-input');
            console.debug('[Modal Lugares] Abriendo desde tree-select', {
                valorSeleccionado: debugInput ? debugInput.value : null,
                contenedor: currentTreeContainer
            });
        } else {
            console.debug('[Modal Lugares] Abriendo sin tree-select asociado');
        }
    });

    modal.addEventListener('shown.bs.modal', function() {
        cargarLugaresExistentes();
        preseleccionarPadre();
        actualizarPreview();
    });

    document.addEventListener('tree-select:open-modal', (event) => {
        const detalle = event.detail || {};
        if (detalle.containerId) {
            const contenedor = document.getElementById(detalle.containerId);
            if (contenedor) {
                currentTreeContainer = contenedor;
                asegurarCacheTiposNivel(contenedor);
            }
        }

        if (detalle.item) {
            ultimoPadreSeleccionado = {
                id: String(detalle.item.id),
                nivel: detalle.item.nivel || 0,
                nombre: detalle.item.nombre_completo || detalle.item.nombre || ''
            };
            if (detalle.item.tipo_nivel_id && !tipoNivelCache[detalle.item.nivel || 0]) {
                tipoNivelCache[detalle.item.nivel] = detalle.item.tipo_nivel_id;
            }
        }
    });

    document.addEventListener('tree-select:selection', (event) => {
        const detalle = event.detail || {};
        const item = detalle.item || null;

        if (detalle.containerId) {
            const contenedor = document.getElementById(detalle.containerId);
            if (contenedor) {
                currentTreeContainer = contenedor;
            }
        }

        if (item) {
            ultimoPadreSeleccionado = {
                id: String(item.id),
                nivel: item.nivel || 0,
                nombre: item.nombre_completo || item.nombre || ''
            };

            if (item.tipo_nivel_id && !tipoNivelCache[item.nivel || 0]) {
                tipoNivelCache[item.nivel] = item.tipo_nivel_id;
            }
        }

        if (modal.classList.contains('show')) {
            cargarLugaresExistentes();
            preseleccionarPadre();
            actualizarPreview();
        }
    });

    // Manejar toggle de niveles
    const nivelToggles = document.querySelectorAll('.nivel-toggle');
    nivelToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            if (this.disabled) {
                return;
            }
            const nivel = parseInt(this.getAttribute('data-nivel'));
            const container = document.getElementById(`nivel-${nivel}-container`);
            const fields = container.querySelector('.nivel-fields');
            
            if (this.checked) {
                fields.style.display = 'block';
                // Auto-activar niveles anteriores si no están activos
                for (let i = 1; i < nivel; i++) {
                    const prevToggle = document.getElementById(`nivel-${i}-activo`);
                    if (!prevToggle || prevToggle.disabled) {
                        continue;
                    }
                    if (!prevToggle.checked) {
                        prevToggle.checked = true;
                        prevToggle.dispatchEvent(new Event('change'));
                    }
                }
            } else {
                fields.style.display = 'none';
                // Limpiar campos
                document.getElementById(`nivel-${nivel}-nombre`).value = '';
                document.getElementById(`nivel-${nivel}-codigo`).value = '';
                document.getElementById(`nivel-${nivel}-descripcion`).value = '';
                
                // Desactivar niveles posteriores
                for (let i = nivel + 1; i <= 7; i++) {
                    const nextToggle = document.getElementById(`nivel-${i}-activo`);
                    if (nextToggle.checked) {
                        nextToggle.checked = false;
                        nextToggle.dispatchEvent(new Event('change'));
                    }
                }
            }
            
            actualizarPreview();
        });
    });

    // Actualizar preview cuando cambian los nombres
    for (let i = 1; i <= 7; i++) {
        const nombreInput = document.getElementById(`nivel-${i}-nombre`);
        if (nombreInput) {
            nombreInput.addEventListener('input', actualizarPreview);
        }
    }

    // Actualizar preview cuando cambia el padre existente
    padreExistenteSelect.addEventListener('change', function() {
        sincronizarTogglesConPadre();
        actualizarPreview();
    });

    /**
     * Actualizar vista previa de la jerarquía
     */
    function actualizarPreview() {
        const padreId = padreExistenteSelect.value;
        const padreNivel = padreId ? parseInt(padreExistenteSelect.selectedOptions[0]?.getAttribute('data-nivel') || 0) : 0;
        const padreNombre = padreId ? padreExistenteSelect.selectedOptions[0]?.text : '';

        if (padreId && padreNivel >= 7) {
            previewDiv.innerHTML = '<em class="text-muted">El lugar seleccionado es de nivel máximo; no es posible crear nuevos niveles.</em>';
            return;
        }

        let preview = '';
        let tieneNiveles = false;

        // Mostrar padre si existe
        if (padreId) {
            preview += `<div class="mb-2"><strong>Partir desde:</strong> ${padreNombre}</div>`;
            preview += '<div class="ms-3">';
        }

        // Generar preview de niveles nuevos
        for (let nivel = (padreNivel + 1); nivel <= 7; nivel++) {
            const toggle = document.getElementById(`nivel-${nivel}-activo`);
            const nombreInput = document.getElementById(`nivel-${nivel}-nombre`);
            
            if (toggle && toggle.checked) {
                tieneNiveles = true;
                const nombre = nombreInput.value || `[Nivel ${nivel} - Sin nombre]`;
                const indent = '&nbsp;'.repeat((nivel - padreNivel - 1) * 4);
                const prefijo = nivel > (padreNivel + 1) ? '└─ ' : '';
                preview += `<div>${indent}${prefijo}${nivelIcono[nivel]} <strong>${nombre}</strong></div>`;
            }
        }

        if (padreId) {
            preview += '</div>';
        }

        if (!tieneNiveles && !padreId) {
            preview = '<em class="text-muted">Marque los niveles que desea crear para ver la vista previa...</em>';
        } else if (!tieneNiveles && padreId) {
            preview += '<em class="text-muted">Marque los niveles que desea agregar...</em>';
        }

        previewDiv.innerHTML = preview;
    }

    /**
     * Guardar jerarquía completa
     */
    guardarBtn.addEventListener('click', async function() {
        asegurarCacheTiposNivel(obtenerTreeContainer());
        // Obtener padre existente (si lo hay)
        const padreExistenteId = padreExistenteSelect.value;
        const padreNivel = padreExistenteId ? 
            parseInt(padreExistenteSelect.selectedOptions[0]?.getAttribute('data-nivel') || 0) : 0;

        // Recolectar niveles a crear
        const nivelesACrear = [];
        
        for (let nivel = (padreNivel + 1); nivel <= 7; nivel++) {
            const toggle = document.getElementById(`nivel-${nivel}-activo`);
            
            if (toggle && toggle.checked) {
                const tipoNivelId = tipoNivelCache[nivel];
                if (!tipoNivelId) {
                    alert(`No se pudo determinar el tipo de nivel para el Nivel ${nivel}. Recargue la página e intente nuevamente.`);
                    return;
                }

                const nombre = document.getElementById(`nivel-${nivel}-nombre`).value.trim();
                const codigo = document.getElementById(`nivel-${nivel}-codigo`).value.trim();
                const descripcion = document.getElementById(`nivel-${nivel}-descripcion`).value.trim();
                
                if (!nombre) {
                    alert(`Por favor, ingrese un nombre para el Nivel ${nivel}`);
                    document.getElementById(`nivel-${nivel}-nombre`).focus();
                    return;
                }
                
                nivelesACrear.push({
                    nivel: nivel,
                    tipo_nivel_id: tipoNivelId,
                    nombre: nombre,
                    codigo: codigo || null,
                    descripcion: descripcion || null
                });
            }
        }

        if (nivelesACrear.length === 0) {
            alert('Por favor, active y complete al menos un nivel para crear');
            return;
        }

        // Validar que los niveles sean consecutivos
        const nivelesOrdenados = nivelesACrear.map(n => n.nivel).sort((a, b) => a - b);
        const primerNivel = nivelesOrdenados[0];
        const ultimoNivel = nivelesOrdenados[nivelesOrdenados.length - 1];
        
        for (let i = primerNivel; i <= ultimoNivel; i++) {
            if (!nivelesOrdenados.includes(i)) {
                alert(`La jerarquía debe ser consecutiva. Falta el nivel ${i}`);
                return;
            }
        }

        // Validar que el primer nivel sea correcto
        if (padreExistenteId && primerNivel !== padreNivel + 1) {
            alert(`Si parte desde un lugar de nivel ${padreNivel}, debe crear desde el nivel ${padreNivel + 1}`);
            return;
        }

        if (!padreExistenteId && primerNivel !== 1) {
            alert('Si no selecciona un padre existente, debe empezar desde el Nivel 1 (Unidad Ejecutora)');
            return;
        }

        // Deshabilitar botón
        guardarBtn.disabled = true;
        guardarBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Guardando jerarquía...';

        try {
            // Obtener CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // Crear lugares en orden jerárquico
            let padreActualId = padreExistenteId ? parseInt(padreExistenteId) : null;

            for (const nivelData of nivelesACrear) {
                const data = {
                    nombre: nivelData.nombre,
                    nivel: nivelData.nivel,
                    tipo_nivel: nivelData.tipo_nivel_id,
                    activo: true
                };

                if (nivelData.codigo) {
                    data.codigo = nivelData.codigo;
                }

                if (nivelData.descripcion) {
                    data.descripcion = nivelData.descripcion;
                }

                if (padreActualId) {
                    data.padre = padreActualId;
                }

                // Enviar petición
                const response = await fetch('/api/lugares/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(`Error en nivel ${nivelData.nivel}: ${error.detail || error.nombre || JSON.stringify(error)}`);
                }

                const nuevoLugar = await response.json();
                
                // El ID del lugar recién creado será el padre del siguiente
                padreActualId = nuevoLugar.id;

                console.log(`✅ Creado nivel ${nivelData.nivel}: ${nivelData.nombre} (ID: ${nuevoLugar.id})`);
            }

            // Éxito
            alert(`✅ Jerarquía creada exitosamente: ${nivelesACrear.length} niveles`);

            // Cerrar modal
            const bsModal = bootstrap.Modal.getInstance(modal);
            bsModal.hide();

            // Limpiar formulario
            limpiarFormulario();

            // Recargar la página
            window.location.reload();

        } catch (error) {
            console.error('Error:', error);
            alert('❌ Error al crear la jerarquía: ' + error.message);
        } finally {
            // Rehabilitar botón
            guardarBtn.disabled = false;
            guardarBtn.innerHTML = '<i class="bi bi-save"></i> Guardar Jerarquía';
        }
    });

    /**
     * Limpiar formulario
     */
    function limpiarFormulario() {
        padreExistenteSelect.value = '';
        
        for (let i = 1; i <= 7; i++) {
            const toggle = document.getElementById(`nivel-${i}-activo`);
            if (toggle && toggle.checked) {
                toggle.checked = false;
                toggle.dispatchEvent(new Event('change'));
            }
        }
        
        actualizarPreview();
    }

    // Limpiar al cerrar modal
    modal.addEventListener('hidden.bs.modal', function() {
        limpiarFormulario();
    });

    console.log('✅ Módulo lugar-modal.js (jerarquía completa) cargado');
})();
