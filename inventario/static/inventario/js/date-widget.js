// Widget de fecha en español para Django
document.addEventListener('DOMContentLoaded', function() {
    // Configurar campos de fecha para formato español
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        // Agregar placeholder y patrón para formato dd/mm/yyyy
        input.setAttribute('placeholder', 'dd/mm/yyyy');
        input.setAttribute('pattern', '[0-9]{2}/[0-9]{2}/[0-9]{4}');
    });
    
    // Configurar campos de texto con clase spanish-date-input
    const spanishDateInputs = document.querySelectorAll('.spanish-date-input');
    spanishDateInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, ''); // Solo números
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2);
            }
            if (value.length >= 5) {
                value = value.substring(0, 5) + '/' + value.substring(5, 9);
            }
            e.target.value = value;
        });
    });
});
