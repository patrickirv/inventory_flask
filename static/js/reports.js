// Función para inicializar las fechas predeterminadas
function initializeDates() {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);

    // Formatear fecha en formato YYYY-MM-DD
    const formatDate = (date) => {
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    // Establecer valores predeterminados en los campos de fecha
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    if (startDateInput && endDateInput) {
        startDateInput.value = formatDate(yesterday); // Fecha de inicio: Ayer
        endDateInput.value = formatDate(today); // Fecha de fin: Hoy
    }
}

// Función para manejar el cambio de selección en el periodo
function handlePeriodChange() {
    const periodSelect = document.getElementById('period_select');
    const customDateRange = document.getElementById('custom_date_range');

    if (periodSelect.value === 'custom') {
        customDateRange.style.display = 'flex'; // Mostrar rango personalizado
        initializeDates(); // Configurar fechas predeterminadas
    } else {
        customDateRange.style.display = 'none'; // Ocultar rango personalizado
    }
}

// Configurar el evento para el cambio de selección
document.getElementById('period_select').addEventListener('change', handlePeriodChange);

// Configurar el estado inicial al cargar la página
window.addEventListener('DOMContentLoaded', () => {
    handlePeriodChange(); // Asegurar que el estado inicial sea correcto
});
