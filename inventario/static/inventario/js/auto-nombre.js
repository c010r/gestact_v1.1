// Función para generar automáticamente el nombre de la computadora
document.addEventListener('DOMContentLoaded', function() {
    console.log('Auto-nombre.js cargado correctamente');
    
    // Función para generar el nombre automáticamente (solo nombre, no número de inventario)
    function generarNombre() {
        const fabricanteSelect = document.getElementById('id_fabricante');
        const modeloSelect = document.getElementById('id_modelo');
        const nombreInput = document.getElementById('id_nombre');
        
        if (!fabricanteSelect || !modeloSelect || !nombreInput) {
            console.warn('Elementos no encontrados para generar nombre');
            return;
        }
        
        const fabricante = fabricanteSelect.options[fabricanteSelect.selectedIndex]?.text || '';
        const modelo = modeloSelect.options[modeloSelect.selectedIndex]?.text || '';
        
        // Solo generar si hay fabricante y modelo
        if (fabricante && fabricante !== '---------' && modelo && modelo !== '---------') {
            const nombreGenerado = `${fabricante} ${modelo}`;
            
            // Solo actualizar si el campo está vacío
            if (!nombreInput.value || nombreInput.value.trim() === '') {
                nombreInput.value = nombreGenerado;
                console.log('Nombre generado:', nombreGenerado);
            }
        }
    }
    
    // Función para obtener el texto de un select
    function getSelectText(selectElement) {
        if (!selectElement || selectElement.selectedIndex < 0) return '';
        return selectElement.options[selectElement.selectedIndex].text;
    }
    
    // Función para verificar si un valor es válido (no es la opción por defecto)
    function esValido(valor) {
        return valor && valor !== '---------' && valor.trim() !== '';
    }
    
    // Agregar event listeners a los campos
    const modeloSelect = document.getElementById('id_modelo');
    const numeroSerieInput = document.getElementById('id_numero_serie');
    
    if (modeloSelect) {
        modeloSelect.addEventListener('change', function() {
            console.log('Modelo cambiado:', getSelectText(this));
            generarNombre();
        });
    }
    
    // Generar nombre inicial si ya hay valores
    setTimeout(function() {
        generarNombre();
    }, 500);
    
    console.log('Event listeners configurados para auto-generación de nombre (Fabricante-Modelo)');
});
