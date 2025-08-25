// Dashboard specific JavaScript functions
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-refresh dashboard data every 5 minutes
    setInterval(function() {
        if (document.hidden === false) {
            // Only refresh if page is visible
            window.location.reload();
        }
    }, 300000); // 5 minutes

    // Add animation to KPI cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// Function to format currency values
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Function to update dashboard stats via AJAX (if needed)
function updateDashboardStats() {
    fetch('/api/dashboard-stats')
        .then(response => response.json())
        .then(data => {
            // Update KPI cards with new data
            document.querySelector('#total-equipment').textContent = data.total;
            document.querySelector('#equipment-in-use').textContent = data.em_uso;
            document.querySelector('#equipment-no-antivirus').textContent = data.sem_antivirus;
            document.querySelector('#equipment-no-term').textContent = data.sem_termo;
            document.querySelector('#total-value').textContent = formatCurrency(data.valor_total);
        })
        .catch(error => {
            console.error('Error updating dashboard stats:', error);
        });
}
