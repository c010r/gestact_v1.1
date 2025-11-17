(function() {
    'use strict';

    const ENDPOINT = '/api/lugares/';
    const DEFAULT_PLACEHOLDER = 'Seleccione una ubicación...';
    const DEFAULT_CLEAR_LABEL = 'Limpiar selección';

    const isNumeric = value => /^\d+$/.test(value || '');

    const normalizarLugares = (raw) => {
        return raw.map(item => ({
            id: item.id,
            nombre: item.nombre,
            nombre_completo: item.nombre_completo || item.nombre,
            nivel: item.nivel,
            tipo: item.tipo_nivel_nombre || '',
            tipo_nivel_id: item.tipo_nivel,
            tipo_nivel_requiere_codigo: false,
            padre_id: item.padre,
            es_hoja: false,
            codigo: item.codigo || '',
            activo: item.activo !== false,
        }));
    };

    const fetchAllLugares = async (url = ENDPOINT, acumulado = []) => {
        const response = await fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin',
        });

        if (!response.ok) {
            throw new Error(`Error ${response.status} al obtener lugares`);
        }

        const data = await response.json();
        const current = Array.isArray(data) ? data : (data.results || []);
        const merged = acumulado.concat(current);

        if (data.next) {
            return fetchAllLugares(data.next, merged);
        }

        return merged;
    };

    const renderFallbackInput = (container, rawValue, inputName, inputId) => {
        const fallback = document.createElement('input');
        fallback.type = 'text';
        fallback.className = 'form-control';
        fallback.name = inputName;
        fallback.id = inputId;
        fallback.value = rawValue || '';
        const parent = container.parentElement;
        if (parent) {
            parent.replaceChild(fallback, container);
        }
    };

    const renderTreeSelectFilter = (container, treeData) => {
        const rawValue = (container.dataset.selectedValue || '').trim();
    const selectedId = isNumeric(rawValue) ? rawValue : '';
    const selectedLabel = container.dataset.selectedLabel || '';
        const inputName = container.dataset.inputName || container.dataset.fieldName || 'lugar';
        const inputId = container.dataset.inputId || `${inputName}-id`;
        const placeholder = container.dataset.placeholder || DEFAULT_PLACEHOLDER;
        const clearLabel = container.dataset.clearLabel || DEFAULT_CLEAR_LABEL;
        const autoSubmit = container.dataset.autoSubmit === 'true';

        if (!selectedId && rawValue && !isNumeric(rawValue)) {
            renderFallbackInput(container, rawValue, inputName, inputId);
            return;
        }

        if (typeof window.TreeSelect !== 'function') {
            renderFallbackInput(container, rawValue, inputName, inputId);
            return;
        }

        container.dataset.skipAutoinit = 'true';
        container.classList.add('tree-select-container');
        container.dataset.tree = JSON.stringify(treeData);
        container.dataset.tiposNivel = '[]';

        container.innerHTML = `
            <input type="hidden" name="${inputName}" id="${inputId}" value="${selectedId}" class="tree-select-input">
            <div class="input-group">
                <div class="tree-select-display" id="${inputId}-display">
                    <div class="tree-select-content">
                        <span class="tree-select-placeholder">${placeholder}</span>
                        <span class="tree-select-value d-none"></span>
                    </div>
                    <span class="tree-select-arrow">▼</span>
                </div>
                <button type="button" class="btn btn-outline-secondary tree-select-clear-btn" data-tree-select-clear title="${clearLabel}">
                    <i class="bi bi-x-circle"></i>
                </button>
            </div>
            <div class="tree-select-dropdown">
                <div class="tree-search">
                    <input type="text" id="${inputId}-search" placeholder="Buscar ubicación..." autocomplete="off">
                </div>
                <ul class="tree-list"></ul>
            </div>
        `;

        if (selectedLabel) {
            const displayValue = container.querySelector('.tree-select-value');
            const placeholderEl = container.querySelector('.tree-select-placeholder');
            if (displayValue) {
                displayValue.textContent = selectedLabel;
                displayValue.classList.remove('d-none');
            }
            if (placeholderEl) {
                placeholderEl.classList.add('d-none');
            }
        }

        const instance = new window.TreeSelect(container);
        if (selectedId) {
            instance.setValue(selectedId, false);
        }

        const clearBtn = container.querySelector('[data-tree-select-clear]');
        if (clearBtn) {
            clearBtn.addEventListener('click', event => {
                event.preventDefault();
                if (instance) {
                    instance.setValue('', false);
                }
                if (autoSubmit) {
                    const form = container.closest('form');
                    if (form) {
                        form.submit();
                    }
                }
            });
        }
    };

    document.addEventListener('DOMContentLoaded', async () => {
        const containers = Array.from(document.querySelectorAll('.tree-select-filter'));
        if (!containers.length) {
            return;
        }

        try {
            const lugares = await fetchAllLugares();
            const treeData = normalizarLugares(lugares);
            containers.forEach(container => renderTreeSelectFilter(container, treeData));
        } catch (error) {
            console.error('[FilterTree] No se pudo cargar la jerarquía de lugares', error);
            containers.forEach(container => {
                const rawValue = (container.dataset.selectedValue || '').trim();
                const inputName = container.dataset.inputName || container.dataset.fieldName || 'lugar';
                const inputId = container.dataset.inputId || `${inputName}-id`;
                renderFallbackInput(container, rawValue, inputName, inputId);
            });
        }
    });
})();
