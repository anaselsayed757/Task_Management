
let tasks = [];
let users = [];
let currentView = 'all';
let currentEditingTask = null;


document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ Dashboard initialized');
    loadUsers();
    loadTasks();
    loadStats();
    setupEventListeners();

    
    setInterval(() => {
        loadTasks();
        loadStats();
    }, 30000);
});


function setupEventListeners() {
    const newTaskBtn = document.getElementById('newTaskBtn');
    if (newTaskBtn)
        newTaskBtn.addEventListener('click', () => openTaskModal());

    const searchInput = document.getElementById('searchInput');
    if (searchInput)
        searchInput.addEventListener('input', filterTasks);

    const priorityFilter = document.getElementById('priorityFilter');
    if (priorityFilter)
        priorityFilter.addEventListener('change', filterTasks);

    const sortBy = document.getElementById('sortBy');
    if (sortBy)
        sortBy.addEventListener('change', filterTasks);

    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', e => {
            e.preventDefault();
            const view = item.getAttribute('data-view');
            switchView(view);
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
        });
    });

    const modal = document.getElementById('taskModal');
    if (modal)
        modal.addEventListener('click', e => {
            if (e.target === modal) closeTaskModal();
        });
}


async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        if (!response.ok) throw new Error('Failed to load tasks');
        tasks = await response.json();
        filterTasks();
        showDeadlineAlert();
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) return;
        const stats = await response.json();
        updateStatsDisplay(stats);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadUsers() {
    try {
        const response = await fetch('/api/users');
        if (!response.ok) return;
        users = await response.json();
        updateUserSelect();
    } catch (error) {
        console.error('Error loading users:', error);
    }
}


function updateStatsDisplay(stats) {
    document.getElementById('totalTasks').textContent = stats.total;
    document.getElementById('inProgressTasks').textContent = stats.in_progress;
    document.getElementById('completedTasks').textContent = stats.completed;
    document.getElementById('overdueTasks').textContent = stats.overdue;
}

function updateUserSelect() {
    const select = document.getElementById('taskAssignee');
    if (!select) return;
    select.innerHTML = '<option value="">Myself</option>';
    users.forEach(u => {
        const opt = document.createElement('option');
        opt.value = u.id;
        opt.textContent = u.username;
        select.appendChild(opt);
    });
}

function switchView(view) {
    currentView = view;
    const titles = {
        all: 'All Tasks',
        todo: 'To Do Tasks',
        in_progress: 'In Progress Tasks',
        completed: 'Completed Tasks',
        high: 'High Priority Tasks',
        overdue: 'Overdue Tasks'
    };
    document.getElementById('viewTitle').textContent = titles[view] || 'All Tasks';
    filterTasks();
}


function filterTasks() {
    let filtered = [...tasks];

    if (currentView === 'overdue') {
        const now = new Date();
        filtered = filtered.filter(t => t.deadline && new Date(t.deadline) < now && t.status !== 'completed');
    } else if (['todo', 'in_progress', 'completed'].includes(currentView)) {
        filtered = filtered.filter(t => t.status === currentView);
    } else if (currentView === 'high') {
        filtered = filtered.filter(t => t.priority === 'high');
    }

    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase();
    if (searchTerm)
        filtered = filtered.filter(t =>
            t.title.toLowerCase().includes(searchTerm) || t.description.toLowerCase().includes(searchTerm)
        );

    const priorityFilter = document.getElementById('priorityFilter')?.value;
    if (priorityFilter)
        filtered = filtered.filter(t => t.priority === priorityFilter);

    const sortBy = document.getElementById('sortBy')?.value || 'created_desc';
    const priorityOrder = { high: 3, medium: 2, low: 1 };

    filtered.sort((a, b) => {
        switch (sortBy) {
            case 'created_desc': return new Date(b.created_at) - new Date(a.created_at);
            case 'created_asc': return new Date(a.created_at) - new Date(b.created_at);
            case 'deadline_asc':
                if (!a.deadline) return 1;
                if (!b.deadline) return -1;
                return new Date(a.deadline) - new Date(b.deadline);
            case 'priority_desc': return priorityOrder[b.priority] - priorityOrder[a.priority];
            default: return 0;
        }
    });

    renderTasks(filtered);
}


function renderTasks(tasksToRender) {
    const container = document.getElementById('tasksContainer');
    const emptyState = document.getElementById('emptyState');
    if (!container) return;

    if (tasksToRender.length === 0) {
        container.style.display = 'none';
        if (emptyState) emptyState.style.display = 'block';
        return;
    }

    container.style.display = 'grid';
    if (emptyState) emptyState.style.display = 'none';
    container.innerHTML = tasksToRender.map(createTaskCard).join('');

    
    setTimeout(() => {
        tasksToRender.forEach(task => {
            document.getElementById(`edit-${task.id}`)?.addEventListener('click', () => openTaskModal(task));
            document.getElementById(`delete-${task.id}`)?.addEventListener('click', () => deleteTask(task.id));
            document.getElementById(`complete-${task.id}`)?.addEventListener('click', () => toggleComplete(task));
        });
    }, 100);
}

function createTaskCard(task) {
    const deadline = task.deadline ? new Date(task.deadline) : null;
    const now = new Date();
    const isOverdue = deadline && deadline < now && task.status !== 'completed';
    const deadlineText = deadline ? formatDate(deadline) : '';
    const deadlineClass = isOverdue ? 'overdue' : '';

    return `
        <div class="task-card priority-${task.priority}" id="task-${task.id}">
            <div class="task-header">
                <h3 class="task-title">${escapeHtml(task.title)}</h3>
                <div class="task-actions">
                    <button class="task-action-btn" id="complete-${task.id}" title="Mark as ${task.status === 'completed' ? 'incomplete' : 'complete'}">
                        ${task.status === 'completed' ? '↩️' : '✅'}
                    </button>
                    <button class="task-action-btn" id="edit-${task.id}" title="Edit">✏️</button>
                    <button class="task-action-btn" id="delete-${task.id}" title="Delete">🗑️</button>
                </div>
            </div>
            ${task.description ? `<p class="task-description">${escapeHtml(task.description)}</p>` : ''}
            <div class="task-meta">
                <span class="task-badge badge-status ${task.status}">${formatStatus(task.status)}</span>
                <span class="task-badge badge-priority ${task.priority}">${task.priority.toUpperCase()}</span>
            </div>
            ${deadline ? `<div class="task-deadline ${deadlineClass}">📅 ${deadlineText}</div>` : ''}
            ${task.assignee_name ? `
                <div class="task-assignee">
                    <div class="assignee-avatar">${task.assignee_name[0].toUpperCase()}</div>
                    <span>Assigned to ${task.assignee_name}</span>
                </div>
            ` : ''}
        </div>
    `;
}


function showDeadlineAlert() {
    const mainContent = document.querySelector('.main-content');
    if (!mainContent) return;
    document.getElementById('deadlineAlert')?.remove();

    const now = new Date();
    const soon = new Date(now.getTime() + 24 * 60 * 60 * 1000);
    const approaching = tasks.filter(t =>
        t.deadline && new Date(t.deadline) > now && new Date(t.deadline) <= soon && t.status !== 'completed'
    );

    if (approaching.length === 0) return;
    const alertDiv = document.createElement('div');
    alertDiv.id = 'deadlineAlert';
    alertDiv.className = 'deadline-warning';
    alertDiv.innerHTML = `<i>⏰</i><span>You have <strong>${approaching.length}</strong> task${approaching.length > 1 ? 's' : ''} due soon!</span>`;
    mainContent.prepend(alertDiv);
    setTimeout(() => {
        alertDiv.style.transition = 'opacity 1s';
        alertDiv.style.opacity = '0';
        setTimeout(() => alertDiv.remove(), 1000);
    }, 10000);
}

// ================== TASK CRUD ==================
async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
        const res = await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to delete task');
        document.getElementById(`task-${taskId}`)?.remove();
        await loadTasks();
        await loadStats();
    } catch (err) {
        console.error('Error deleting task:', err);
        alert('Could not delete task.');
    }
}

async function toggleComplete(task) {
    const newStatus = task.status === 'completed' ? 'todo' : 'completed';
    try {
        const res = await fetch(`/api/tasks/${task.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        if (!res.ok) throw new Error('Failed to update task');
        await loadTasks();
        await loadStats();
    } catch (err) {
        console.error('Error toggling task:', err);
        alert('Could not update task.');
    }
}

// ================== TASK MODAL MANAGEMENT ==================
function openTaskModal(task = null) {
    const modal = document.getElementById('taskModal');
    const modalTitle = document.getElementById('modalTitle');
    const form = document.getElementById('taskForm');

    if (!modal) return;

    // ✅ Always bind submit when modal opens
    form.onsubmit = handleTaskSubmit;

    if (task) {
        modalTitle.textContent = 'Edit Task';
        document.getElementById('taskId').value = task.id;
        document.getElementById('taskTitle').value = task.title;
        document.getElementById('taskDescription').value = task.description || '';
        document.getElementById('taskPriority').value = task.priority;
        document.getElementById('taskStatus').value = task.status;

        if (task.deadline) {
            const d = new Date(task.deadline);
            document.getElementById('taskDeadline').value = d.toISOString().slice(0, 16);
        } else {
            document.getElementById('taskDeadline').value = '';
        }

        document.getElementById('taskAssignee').value = task.assigned_to || '';
    } else {
        modalTitle.textContent = 'Create New Task';
        form.reset();
        document.getElementById('taskId').value = '';
    }

    modal.classList.add('active');
}

function closeTaskModal() {
    const modal = document.getElementById('taskModal');
    if (!modal) return;
    modal.classList.remove('active');
    document.getElementById('taskForm').reset();
    document.getElementById('taskId').value = '';
}

// ================== FORM SUBMIT ==================
async function handleTaskSubmit(e) {
    e.preventDefault();
    const taskId = document.getElementById('taskId').value;
    const taskData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        priority: document.getElementById('taskPriority').value,
        status: document.getElementById('taskStatus').value,
        deadline: document.getElementById('taskDeadline').value || null,
        assigned_to: document.getElementById('taskAssignee').value || null
    };

    try {
        const url = taskId ? `/api/tasks/${taskId}` : '/api/tasks';
        const method = taskId ? 'PUT' : 'POST';
        const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(taskData)
        });
        if (!res.ok) throw new Error('Failed to save task');
        closeTaskModal();
        await loadTasks();
        await loadStats();
    } catch (err) {
        console.error('Error saving task:', err);
        alert('An error occurred while saving the task.');
    }
}


function formatDate(date) {
    const now = new Date();
    const diff = date - now;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    if (days < 0) return `Overdue by ${Math.abs(days)} day(s)`;
    if (days === 0) return 'Due today';
    if (days === 1) return 'Due tomorrow';
    if (days < 7) return `Due in ${days} days`;
    return date.toLocaleDateString();
}

function formatStatus(status) {
    return { todo: 'To Do', in_progress: 'In Progress', completed: 'Completed' }[status] || status;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}


window.openTaskModal = openTaskModal;
window.closeTaskModal = closeTaskModal;
