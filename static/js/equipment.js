// Equipment specific JavaScript functions
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-submit search form on input change
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        const searchInputs = searchForm.querySelectorAll('input, select');
        searchInputs.forEach(input => {
            if (input.type !== 'submit') {
                input.addEventListener('change', function() {
                    // Debounce for text inputs
                    if (this.type === 'text') {
                        clearTimeout(this.searchTimeout);
                        this.searchTimeout = setTimeout(() => {
                            searchForm.submit();
                        }, 500);
                    } else {
                        searchForm.submit();
                    }
                });
            }
        });
    }

    // Add sorting functionality to table headers
    const tableHeaders = document.querySelectorAll('th[data-sort]');
    tableHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const sortField = this.dataset.sort;
            const currentUrl = new URL(window.location);
            const currentSort = currentUrl.searchParams.get('sort');
            const currentOrder = currentUrl.searchParams.get('order');
            
            let newOrder = 'asc';
            if (currentSort === sortField && currentOrder === 'asc') {
                newOrder = 'desc';
            }
            
            currentUrl.searchParams.set('sort', sortField);
            currentUrl.searchParams.set('order', newOrder);
            window.location.href = currentUrl.toString();
        });
    });

    // Add row highlighting on hover
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(0, 123, 255, 0.1)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
});

// Function to confirm deletion
function confirmDelete(equipmentId, equipmentName) {
    if (confirm(`Tem certeza que deseja excluir o equipamento "${equipmentName}"?\n\nEsta ação não pode ser desfeita.`)) {
        // Create a form to submit the delete request
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/equipment/${equipmentId}/delete`;
        
        // Add CSRF token if available
        const csrfToken = document.querySelector('meta[name=csrf-token]');
        if (csrfToken) {
            const tokenInput = document.createElement('input');
            tokenInput.type = 'hidden';
            tokenInput.name = 'csrf_token';
            tokenInput.value = csrfToken.getAttribute('content');
            form.appendChild(tokenInput);
        }
        
        document.body.appendChild(form);
        form.submit();
    }
}

// Function to export data
function exportData(format) {
    const currentUrl = new URL(window.location);
    const params = currentUrl.searchParams;
    
    let exportUrl = `/export/${format}`;
    if (params.toString()) {
        exportUrl += `?${params.toString()}`;
    }
    
    window.location.href = exportUrl;
}

// Function to toggle advanced search
function toggleAdvancedSearch() {
    const advancedDiv = document.getElementById('advanced-search');
    const toggleBtn = document.getElementById('toggle-advanced');
    
    if (advancedDiv.style.display === 'none') {
        advancedDiv.style.display = 'block';
        toggleBtn.textContent = 'Ocultar Filtros Avançados';
    } else {
        advancedDiv.style.display = 'none';
        toggleBtn.textContent = 'Mostrar Filtros Avançados';
    }
}

// Function to clear all filters
function clearFilters() {
    const form = document.getElementById('search-form');
    const inputs = form.querySelectorAll('input, select');
    
    inputs.forEach(input => {
        if (input.type === 'text' || input.type === 'email' || input.type === 'tel') {
            input.value = '';
        } else if (input.type === 'select-one') {
            input.selectedIndex = 0;
        } else if (input.type === 'checkbox') {
            input.checked = false;
        }
    });
    
    // Remove URL parameters and reload
    window.location.href = window.location.pathname;
}

// Function to validate form before submission
function validateEquipmentForm() {
    const form = document.querySelector('form');
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Add form validation on submit
document.addEventListener('DOMContentLoaded', function() {
    const equipmentForm = document.querySelector('form[method="POST"]');
    if (equipmentForm) {
        equipmentForm.addEventListener('submit', function(e) {
            if (!validateEquipmentForm()) {
                e.preventDefault();
                alert('Por favor, preencha todos os campos obrigatórios.');
            }
        });
    }
});
