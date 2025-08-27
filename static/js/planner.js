// Planner/Kanban Board JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeDragAndDrop();
    initializeModals();
});

// Global variables
let currentListId = null;
let currentTaskId = null;
let draggedTask = null;

// Initialize drag and drop functionality
function initializeDragAndDrop() {
    const taskCards = document.querySelectorAll('.task-card');
    const taskContainers = document.querySelectorAll('.task-container');

    taskCards.forEach(card => {
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
    });

    taskContainers.forEach(container => {
        container.addEventListener('dragover', handleDragOver);
        container.addEventListener('drop', handleDrop);
        container.addEventListener('dragenter', handleDragEnter);
        container.addEventListener('dragleave', handleDragLeave);
    });
}

// Drag event handlers
function handleDragStart(e) {
    draggedTask = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.outerHTML);
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    draggedTask = null;
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDragEnter(e) {
    this.classList.add('drag-over');
}

function handleDragLeave(e) {
    this.classList.remove('drag-over');
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }

    this.classList.remove('drag-over');

    if (draggedTask && draggedTask !== this) {
        const taskId = draggedTask.dataset.taskId;
        const newListId = this.dataset.listId;
        const currentListId = draggedTask.closest('.task-container').dataset.listId;

        if (newListId !== currentListId) {
            // Move task to new list
            moveTask(taskId, newListId, this.children.length);
            this.appendChild(draggedTask);
            showSuccessMessage('Tarefa movida com sucesso!');
        }
    }

    return false;
}

// Modal functions
function initializeModals() {
    // Initialize Bootstrap modals
    window.newListModal = new bootstrap.Modal(document.getElementById('newListModal'));
    window.newTaskModal = new bootstrap.Modal(document.getElementById('newTaskModal'));
    window.editTaskModal = new bootstrap.Modal(document.getElementById('editTaskModal'));
}

function showNewListModal() {
    document.getElementById('newListForm').reset();
    newListModal.show();
}

function showNewTaskModal(listId) {
    currentListId = listId;
    document.getElementById('taskListId').value = listId;
    document.getElementById('newTaskForm').reset();
    newTaskModal.show();
}

function showEditTaskModal(taskId) {
    currentTaskId = taskId;
    // Load task data and populate form
    loadTaskData(taskId);
    editTaskModal.show();
}

// API functions
function createList() {
    const form = document.getElementById('newListForm');
    const formData = new FormData(form);

    fetch('/planner/list/new', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload(); // Reload to show new list
            showSuccessMessage('Lista criada com sucesso!');
        } else {
            showErrorMessage('Erro ao criar lista: ' + JSON.stringify(data.errors));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Erro de conexão ao criar lista');
    });

    newListModal.hide();
}

function createTask() {
    const form = document.getElementById('newTaskForm');
    const formData = new FormData(form);

    fetch('/planner/task/new', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addTaskToDOM(data.task);
            showSuccessMessage('Tarefa criada com sucesso!');
        } else {
            showErrorMessage('Erro ao criar tarefa: ' + JSON.stringify(data.errors));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Erro de conexão ao criar tarefa');
    });

    newTaskModal.hide();
}

function editTask(taskId) {
    showEditTaskModal(taskId);
}

function updateTask() {
    const taskId = currentTaskId;
    const form = document.getElementById('editTaskForm');
    const formData = new FormData(form);
    
    const data = {
        title: formData.get('title'),
        description: formData.get('description'),
        priority: formData.get('priority'),
        due_date: formData.get('due_date')
    };

    fetch(`/planner/task/${taskId}/edit`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateTaskInDOM(data.task);
            showSuccessMessage('Tarefa atualizada com sucesso!');
        } else {
            showErrorMessage('Erro ao atualizar tarefa');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Erro de conexão ao atualizar tarefa');
    });

    editTaskModal.hide();
}

function deleteTask(taskId) {
    if (confirm('Tem certeza que deseja excluir esta tarefa?')) {
        fetch(`/planner/task/${taskId}/delete`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector(`[data-task-id="${taskId}"]`).remove();
                showSuccessMessage('Tarefa excluída com sucesso!');
            } else {
                showErrorMessage('Erro ao excluir tarefa');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage('Erro de conexão ao excluir tarefa');
        });
    }
}

function deleteList(listId) {
    if (confirm('Tem certeza que deseja excluir esta lista e todas as suas tarefas?')) {
        fetch(`/planner/list/${listId}/delete`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector(`[data-list-id="${listId}"]`).remove();
                showSuccessMessage('Lista excluída com sucesso!');
            } else {
                showErrorMessage('Erro ao excluir lista');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage('Erro de conexão ao excluir lista');
        });
    }
}

function moveTask(taskId, newListId, position) {
    fetch(`/planner/task/${taskId}/move`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            list_id: parseInt(newListId),
            position: position
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.error('Failed to move task:', data.error);
        }
    })
    .catch(error => {
        console.error('Error moving task:', error);
    });
}

// Helper functions
function addTaskToDOM(task) {
    const container = document.querySelector(`[data-list-id="${task.list_id}"]`);
    if (container) {
        const taskCard = createTaskCardHTML(task);
        container.insertAdjacentHTML('beforeend', taskCard);
        
        // Re-initialize drag and drop for new task
        const newCard = container.lastElementChild;
        newCard.addEventListener('dragstart', handleDragStart);
        newCard.addEventListener('dragend', handleDragEnd);
        newCard.classList.add('new-item');
    }
}

function updateTaskInDOM(task) {
    const taskCard = document.querySelector(`[data-task-id="${task.id}"]`);
    if (taskCard) {
        taskCard.outerHTML = createTaskCardHTML(task);
        
        // Re-initialize drag and drop for updated task
        const updatedCard = document.querySelector(`[data-task-id="${task.id}"]`);
        updatedCard.addEventListener('dragstart', handleDragStart);
        updatedCard.addEventListener('dragend', handleDragEnd);
    }
}

function createTaskCardHTML(task) {
    const dueDateHTML = task.due_date ? 
        `<small class="due-date ${task.is_overdue ? 'overdue' : ''}">
            <i class="fas fa-calendar-alt me-1"></i>
            ${task.due_date}
        </small>` : '';
    
    const descriptionHTML = task.description ? 
        `<p class="task-description">${task.description}</p>` : '';

    return `
        <div class="task-card" data-task-id="${task.id}" draggable="true">
            <div class="task-header">
                <h6 class="task-title">${task.title}</h6>
                <span class="priority-badge" style="background-color: ${task.priority_color}">
                    ${task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                </span>
            </div>
            
            ${descriptionHTML}
            
            <div class="task-footer">
                ${dueDateHTML}
                
                <div class="task-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="editTask(${task.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteTask(${task.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
}

function loadTaskData(taskId) {
    const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
    if (taskCard) {
        const title = taskCard.querySelector('.task-title').textContent;
        const description = taskCard.querySelector('.task-description')?.textContent || '';
        
        document.getElementById('editTaskId').value = taskId;
        document.getElementById('editTaskTitle').value = title;
        document.getElementById('editTaskDescription').value = description;
        
        // Note: For a complete implementation, you might want to fetch full task data from the server
    }
}

function getCSRFToken() {
    // Since CSRF is disabled in the app config, return empty string
    return '';
}

function showSuccessMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'success-feedback';
    messageDiv.textContent = message;
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

function showErrorMessage(message) {
    // Create a toast or alert for error messages
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '1060';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}