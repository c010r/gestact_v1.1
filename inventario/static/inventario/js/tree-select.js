/**
 * Tree Select Widget
 * Selector jerárquico con soporte para creación de lugares.
 */

(function() {
    'use strict';

    class TreeSelect {
        constructor(container) {
            this.container = container;
            this.input = container.querySelector('.tree-select-input');
            this.display = container.querySelector('.tree-select-display');
            this.dropdown = container.querySelector('.tree-select-dropdown');
            this.searchInput = container.querySelector('.tree-search input');
            this.treeList = container.querySelector('.tree-list');
            this.arrow = container.querySelector('.tree-select-arrow');
            this.addButton = container.querySelector('.tree-select-add-btn');

            this.isOpen = false;
            this.treeData = this.safeParse(container.dataset.tree);
            const tipoNivelParsed = this.safeParse(container.dataset.tiposNivel);
            if (Array.isArray(tipoNivelParsed)) {
                this.tipoNivelList = tipoNivelParsed;
            } else if (tipoNivelParsed && Array.isArray(tipoNivelParsed.results)) {
                this.tipoNivelList = tipoNivelParsed.results;
            } else {
                this.tipoNivelList = [];
            }
            this.tipoNivelMap = this.buildTipoNivelMap(this.tipoNivelList);
            this.selectedValue = this.input ? this.input.value : '';

            this.ensureContainerId();
            this.init();

            this.container.__treeSelectInstance = this;
        }

        safeParse(raw) {
            if (!raw) {
                return [];
            }
            try {
                return JSON.parse(raw);
            } catch (error) {
                console.error('[TreeSelect] No se pudo parsear JSON', error);
                return [];
            }
        }

        buildTipoNivelMap(lista) {
            const map = {};
            lista.forEach(item => {
                if (item && item.nivel && item.id) {
                    map[item.nivel] = {
                        id: item.id,
                        requiereCodigo: Boolean(item.requiere_codigo)
                    };
                }
            });
            return map;
        }

        ensureContainerId() {
            if (!this.container.id) {
                this.container.id = `tree-select-${Math.random().toString(36).slice(2, 10)}`;
            }
            if (this.input && this.input.name) {
                this.container.dataset.treeSelectName = this.input.name;
            }
        }

        init() {
            this.buildTree();
            this.attachEvents();
            this.updateDisplay();

            if (this.selectedValue) {
                this.expandToSelected();
                this.notifySelectionById(this.selectedValue);
            }
        }

        attachEvents() {
            if (this.display) {
                this.display.addEventListener('click', () => this.toggle());
            }

            if (this.searchInput) {
                this.searchInput.addEventListener('input', (event) => {
                    this.filterTree(event.target.value);
                });
            }

            if (this.addButton) {
                this.addButton.addEventListener('click', () => {
                    this.notifyModalOpen();
                });
            }

            document.addEventListener('click', (event) => {
                if (!this.container.contains(event.target)) {
                    this.close();
                }
            });
        }

        buildTree() {
            if (!this.treeList) {
                return;
            }

            this.treeList.innerHTML = '';

            const childrenMap = {};
            this.treeData.forEach(item => {
                const parentKey = item.padre_id || 'root';
                if (!childrenMap[parentKey]) {
                    childrenMap[parentKey] = [];
                }
                childrenMap[parentKey].push(item);
            });

            const roots = childrenMap['root'] || [];
            roots.sort(this.sortByNombre);
            roots.forEach(item => {
                this.appendNode(item, this.treeList, childrenMap);
            });
        }

        sortByNombre(a, b) {
            return (a.nombre || '').localeCompare(b.nombre || '', 'es', {
                sensitivity: 'base'
            });
        }

        appendNode(item, parentElement, childrenMap) {
            const li = document.createElement('li');
            li.className = 'tree-node';
            li.dataset.id = item.id;
            li.dataset.nivel = item.nivel;
            li.dataset.padre = item.padre_id || '';
            li.dataset.nombre = (item.nombre || '').toLowerCase();

            const children = childrenMap[item.id] || [];
            children.sort(this.sortByNombre);
            const hasChildren = children.length > 0;

            const content = document.createElement('div');
            content.className = 'tree-node-content';

            const toggle = document.createElement('span');
            toggle.className = 'tree-node-toggle';
            if (hasChildren) {
                toggle.textContent = '▶';
                toggle.addEventListener('click', (event) => {
                    event.stopPropagation();
                    this.toggleNode(li);
                });
            } else {
                toggle.classList.add('empty');
            }
            content.appendChild(toggle);

            const icon = document.createElement('span');
            icon.className = 'tree-node-icon';
            icon.textContent = this.getIconForLevel(item.nivel);
            content.appendChild(icon);

            const label = document.createElement('span');
            label.className = 'tree-node-label';
            label.textContent = item.nombre;
            content.appendChild(label);

            const type = document.createElement('span');
            type.className = 'tree-node-type';
            type.textContent = item.tipo;
            content.appendChild(type);

            li.appendChild(content);

            li.addEventListener('click', (event) => {
                event.stopPropagation();
                this.selectNode(item);
            });

            if (this.selectedValue && String(this.selectedValue) === String(item.id)) {
                li.classList.add('selected');
            }

            parentElement.appendChild(li);

            if (hasChildren) {
                const childList = document.createElement('ul');
                childList.className = 'tree-list tree-children';
                childList.style.display = 'none';
                children.forEach(child => this.appendNode(child, childList, childrenMap));
                li.appendChild(childList);
            }
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

        toggle() {
            if (this.isOpen) {
                this.close();
            } else {
                this.open();
            }
        }

        open() {
            this.isOpen = true;
            if (this.dropdown) {
                this.dropdown.classList.add('open');
            }
            if (this.display) {
                this.display.classList.add('open');
            }
            if (this.arrow) {
                this.arrow.classList.add('open');
            }

            if (this.searchInput) {
                setTimeout(() => this.searchInput.focus(), 100);
            }
        }

        close() {
            this.isOpen = false;
            if (this.dropdown) {
                this.dropdown.classList.remove('open');
            }
            if (this.display) {
                this.display.classList.remove('open');
            }
            if (this.arrow) {
                this.arrow.classList.remove('open');
            }

            if (this.searchInput) {
                this.searchInput.value = '';
                this.filterTree('');
            }
        }

        toggleNode(nodeElement) {
            const toggle = nodeElement.querySelector('.tree-node-toggle');
            const childList = nodeElement.querySelector('.tree-children');
            if (!childList) {
                return;
            }

            if (childList.style.display === 'none') {
                childList.style.display = 'block';
                if (toggle) {
                    toggle.textContent = '▼';
                }
            } else {
                childList.style.display = 'none';
                if (toggle) {
                    toggle.textContent = '▶';
                }
            }
        }

        selectNode(item) {
            if (!this.input) {
                return;
            }

            this.input.value = item.id;
            this.selectedValue = item.id;
            this.updateDisplay();
            this.markSelectedNode(item.id);
            this.close();
            this.notifySelection(item);
        }

        markSelectedNode(id) {
            if (!this.treeList) {
                return;
            }
            this.treeList.querySelectorAll('.tree-node').forEach(node => {
                node.classList.remove('selected');
            });
            if (!id) {
                return;
            }
            const selectedNode = this.treeList.querySelector(`[data-id="${id}"]`);
            if (selectedNode) {
                selectedNode.classList.add('selected');
            }
        }

        updateDisplay() {
            if (!this.display) {
                return;
            }
            const displayValue = this.display.querySelector('.tree-select-value');
            const placeholder = this.display.querySelector('.tree-select-placeholder');

            if (this.selectedValue) {
                const selected = this.treeData.find(item => String(item.id) === String(this.selectedValue));
                if (selected) {
                    if (displayValue) {
                        displayValue.textContent = selected.nombre_completo || selected.nombre;
                        displayValue.classList.remove('d-none');
                    }
                    if (placeholder) {
                        placeholder.classList.add('d-none');
                    }
                }
            } else {
                if (displayValue) {
                    displayValue.textContent = '';
                    displayValue.classList.add('d-none');
                }
                if (placeholder) {
                    placeholder.classList.remove('d-none');
                }
            }
        }

        filterTree(term) {
            const text = term.toLowerCase().trim();
            if (!this.treeList) {
                return;
            }
            this.treeList.querySelectorAll('.tree-node').forEach(node => {
                const nombre = node.dataset.nombre || '';
                if (!text || nombre.includes(text)) {
                    node.classList.remove('hidden');
                    if (text) {
                        this.expandParents(node);
                    }
                } else {
                    node.classList.add('hidden');
                }
            });
        }

        expandParents(node) {
            let current = node.parentElement;
            while (current && current !== this.treeList) {
                if (current.classList.contains('tree-children')) {
                    current.style.display = 'block';
                    const parentNode = current.closest('.tree-node');
                    if (parentNode) {
                        const toggle = parentNode.querySelector('.tree-node-toggle');
                        if (toggle) {
                            toggle.textContent = '▼';
                        }
                    }
                }
                current = current.parentElement;
            }
        }

        expandToSelected() {
            if (!this.treeList || !this.selectedValue) {
                return;
            }
            const selectedNode = this.treeList.querySelector(`[data-id="${this.selectedValue}"]`);
            if (selectedNode) {
                selectedNode.classList.add('selected');
                this.expandParents(selectedNode);
                setTimeout(() => {
                    selectedNode.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }, 100);
            }
        }

        notifySelection(item) {
            const tipoNivelesMeta = JSON.parse(JSON.stringify(this.tipoNivelMap || {}));
            document.dispatchEvent(new CustomEvent('tree-select:selection', {
                detail: {
                    item: { ...item },
                    containerId: this.container.id,
                    fieldName: this.input ? this.input.name : null,
                    tipoNiveles: tipoNivelesMeta
                }
            }));
        }

        notifySelectionById(id) {
            const item = this.treeData.find(lugar => String(lugar.id) === String(id));
            if (item) {
                this.notifySelection(item);
            }
        }

        notifyModalOpen() {
            const selectedItem = this.treeData.find(lugar => String(lugar.id) === String(this.selectedValue));
            const tipoNivelesMeta = JSON.parse(JSON.stringify(this.tipoNivelMap || {}));
            document.dispatchEvent(new CustomEvent('tree-select:open-modal', {
                detail: {
                    containerId: this.container.id,
                    fieldName: this.input ? this.input.name : null,
                    item: selectedItem ? { ...selectedItem } : null,
                    tipoNiveles: tipoNivelesMeta
                }
            }));
        }

        setValue(value, notify = true) {
            if (!this.input) {
                return;
            }

            if (value) {
                this.selectedValue = value;
                this.input.value = value;
                this.updateDisplay();
                this.markSelectedNode(value);
                this.expandToSelected();
                if (notify) {
                    this.notifySelectionById(value);
                }
            } else {
                this.selectedValue = '';
                this.input.value = '';
                this.markSelectedNode(null);
                this.updateDisplay();
            }
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.tree-select-container').forEach(container => {
            if (container.dataset.skipAutoinit === 'true' || container.dataset.skipAutoinit === '1') {
                return;
            }
            if (container.__treeSelectInstance) {
                return;
            }
            new TreeSelect(container);
        });
    });

    if (typeof window !== 'undefined') {
        window.TreeSelect = TreeSelect;
    }
})();
