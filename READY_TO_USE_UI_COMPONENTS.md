# 🎨 READY-TO-USE UI/UX COMPONENTS

## COMPONENT 1: Toast Notification System

**Dosya:** `templates/components/toast_system.html` OLUŞTUR

```html
<!-- Toast Container -->
<div id="toast-container" class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 2000;"></div>

<script>
// Toast Manager
window.ToastManager = {
    show: function(message, type = 'info', duration = 3000) {
        const container = document.getElementById('toast-container');
        const toastId = 'toast-' + Date.now();
        
        const html = `
            <div id="${toastId}" class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <span class="toast-icon">${this.getIcon(type)}</span>
                    <strong class="me-auto">${this.getTitle(type)}</strong>
                    <button type="button" class="btn-close" onclick="document.getElementById('${toastId}').remove();"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', html);
        
        const toast = document.getElementById(toastId);
        setTimeout(() => toast.remove(), duration);
    },
    
    getIcon: function(type) {
        const icons = {
            'success': '✓',
            'error': '✕',
            'warning': '⚠',
            'info': 'ℹ'
        };
        return icons[type] || icons.info;
    },
    
    getTitle: function(type) {
        const titles = {
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            'info': 'Info'
        };
        return titles[type] || titles.info;
    },
    
    success: function(message) { this.show(message, 'success'); },
    error: function(message) { this.show(message, 'error'); },
    warning: function(message) { this.show(message, 'warning'); },
    info: function(message) { this.show(message, 'info'); }
};
</script>

<style>
#toast-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.toast {
    border-radius: 12px;
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    animation: slideIn 0.3s ease;
    background: white;
}

@keyframes slideIn {
    from {
        transform: translateX(400px);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.toast.success {
    border-left: 4px solid #10b981;
}

.toast.error {
    border-left: 4px solid #ef4444;
}

.toast.warning {
    border-left: 4px solid #f59e0b;
}

.toast.info {
    border-left: 4px solid #2563eb;
}

.toast-header {
    background: transparent;
    border-bottom: 1px solid #f1f5f9;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.toast-icon {
    font-size: 16px;
    font-weight: bold;
}

.toast.success .toast-icon { color: #10b981; }
.toast.error .toast-icon { color: #ef4444; }
.toast.warning .toast-icon { color: #f59e0b; }
.toast.info .toast-icon { color: #2563eb; }

.toast-body {
    padding: 12px 16px;
    font-size: 14px;
    color: #1e293b;
}

.btn-close {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 20px;
    color: #64748b;
}

.btn-close:hover {
    color: #1e293b;
}

/* Mobile adaptations */
@media (max-width: 576px) {
    #toast-container {
        left: 12px;
        right: 12px;
        bottom: 12px;
    }
    
    .toast {
        width: 100%;
    }
}
</style>
```

**Kullanım:**
```html
<!-- base.html'ye ekle -->
{% include 'components/toast_system.html' %}

<!-- JS'den kullan -->
<script>
// Form submit sonrası
document.getElementById('equipment-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        const response = await fetch('/api/equipment', { method: 'POST', body: new FormData(this) });
        const data = await response.json();
        if (response.ok) {
            ToastManager.success('Equipment created successfully!');
        } else {
            ToastManager.error(data.error || 'Failed to create equipment');
        }
    } catch (error) {
        ToastManager.error(error.message);
    }
});
</script>
```

---

## COMPONENT 2: Form Validation Helper

**Dosya:** `templates/components/form_validation_helper.html` OLUŞTUR

```html
<script>
// Form Validation Helper Class
class FormValidator {
    constructor(formSelector) {
        this.form = document.querySelector(formSelector);
        if (!this.form) return;
        
        // Real-time validation
        this.form.querySelectorAll('input, textarea, select').forEach(field => {
            field.addEventListener('blur', () => this.validateField(field));
            field.addEventListener('change', () => this.validateField(field));
        });
        
        // Form submit
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }
    
    validateField(field) {
        const isValid = this.checkValidity(field);
        
        // Update visual feedback
        field.classList.toggle('is-invalid', !isValid);
        field.classList.toggle('is-valid', isValid && field.value);
        
        // Show/hide feedback message
        const feedback = field.parentElement.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.style.display = isValid ? 'none' : 'block';
        }
    }
    
    checkValidity(field) {
        // Required
        if (field.hasAttribute('required') && !field.value.trim()) {
            return false;
        }
        
        // Pattern
        if (field.pattern && field.value) {
            const regex = new RegExp(`^${field.pattern}$`);
            if (!regex.test(field.value)) {
                return false;
            }
        }
        
        // Email
        if (field.type === 'email' && field.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(field.value)) {
                return false;
            }
        }
        
        // Min/Max length
        if (field.minLength && field.value.length < field.minLength) {
            return false;
        }
        if (field.maxLength && field.value.length > field.maxLength) {
            return false;
        }
        
        return true;
    }
    
    handleSubmit(e) {
        let isFormValid = true;
        
        this.form.querySelectorAll('input, textarea, select').forEach(field => {
            this.validateField(field);
            if (!this.checkValidity(field)) {
                isFormValid = false;
            }
        });
        
        if (!isFormValid) {
            e.preventDefault();
            ToastManager.error('Please fix validation errors');
            
            // Focus first invalid field
            const firstInvalid = this.form.querySelector('.is-invalid');
            if (firstInvalid) firstInvalid.focus();
        }
    }
}
</script>

<style>
/* Form styling */
.form-group {
    margin-bottom: 20px;
}

.form-label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #1e293b;
}

.form-control, .form-select {
    border: 2px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 14px;
    transition: all 0.2s;
}

.form-control:focus, .form-select:focus {
    border-color: #2563eb;
    background-color: #f0f7ff;
    outline: none;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

/* Validation states */
.form-control.is-valid {
    border-color: #10b981;
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 8'%3e%3cpath fill='%2310b981' d='M2.3 6.73L.6 4.53c-.4-1.04.46-1.4 1.1-.8l1.1 1.4 3.4-3.8c.6-.63 1.6-.27 1.2.7l-4 4.6c-.43.5-.8.4-1.1.1z'/%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right 10px center;
    background-size: 16px 12px;
    padding-right: 38px;
}

.form-control.is-invalid {
    border-color: #ef4444;
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12'%3e%3ccircle cx='6' cy='6' r='4.5' fill='%23ef4444'/%3e%3cpath fill='%23fff' d='M8 4H4v4h4V4z'/%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right 10px center;
    background-size: 16px 16px;
    padding-right: 38px;
}

.valid-feedback {
    display: block;
    margin-top: 4px;
    font-size: 12px;
    color: #10b981;
}

.invalid-feedback {
    display: none;
    margin-top: 4px;
    font-size: 12px;
    color: #ef4444;
}

.form-text {
    display: block;
    margin-top: 4px;
    font-size: 12px;
    color: #64748b;
}

/* Button states */
.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
</style>
```

**Kullanım:**
```html
<!-- Form HTML -->
<form id="equipment-form">
    <div class="form-group">
        <label for="equipment_code" class="form-label">Equipment Code *</label>
        <input 
            type="text" 
            id="equipment_code"
            name="equipment_code"
            class="form-control"
            placeholder="EQ-001"
            pattern="^[A-Z]{2}-\d{3}$"
            required
        >
        <small class="form-text">Format: XX-000 (e.g., EQ-001)</small>
        <div class="invalid-feedback">Invalid format. Use: XX-000</div>
        <div class="valid-feedback">✓ Format correct!</div>
    </div>
    
    <button type="submit" class="btn btn-primary">Save</button>
</form>

<!-- JS -->
<script>
document.addEventListener('DOMContentLoaded', () => {
    new FormValidator('#equipment-form');
});
</script>
```

---

## COMPONENT 3: Empty State Component

**Dosya:** `templates/components/empty_state.html` OLUŞTUR

```html
<div class="empty-state">
    <div class="empty-state-icon">{{ icon }}</div>
    <h3 class="empty-state-title">{{ title }}</h3>
    <p class="empty-state-description">{{ description }}</p>
    {% if action_url %}
    <a href="{{ action_url }}" class="btn btn-primary">
        {{ action_label | default('Add New') }}
    </a>
    {% endif %}
</div>

<style>
.empty-state {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border: 2px dashed #cbd5e1;
    border-radius: 16px;
    padding: 60px 40px;
    text-align: center;
    margin: 40px 0;
}

.empty-state-icon {
    font-size: 4em;
    margin-bottom: 20px;
    opacity: 0.8;
}

.empty-state-title {
    font-size: 20px;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 8px;
}

.empty-state-description {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 24px;
    max-width: 400px;
    margin-left: auto;
    margin-right: auto;
}

.empty-state .btn {
    transition: all 0.3s;
}

.empty-state .btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

@media (max-width: 768px) {
    .empty-state {
        padding: 40px 20px;
    }
    
    .empty-state-icon {
        font-size: 3em;
    }
    
    .empty-state-title {
        font-size: 18px;
    }
}
</style>
```

**Kullanım:**
```html
<!-- Equipment listesinde -->
{% if equipments %}
    <table class="table">
        <!-- Equipment items -->
    </table>
{% else %}
    {% include 'components/empty_state.html' with 
        icon='📦'
        title='No Equipment Yet'
        description='You don\'t have any equipment registered yet. Add your first equipment to get started.'
        action_url='/equipment/add'
        action_label='Add Equipment'
    %}
{% endif %}
```

---

## COMPONENT 4: Skeleton Loader

**Dosya:** `templates/components/skeleton_loader.html` OLUŞTUR

```html
<!-- Skeleton Loader for Tables -->
<div class="skeleton-loader">
    {% for i in range(5) %}
    <div class="skeleton-row">
        <div class="skeleton-cell" style="width: 20%;"></div>
        <div class="skeleton-cell" style="width: 30%;"></div>
        <div class="skeleton-cell" style="width: 25%;"></div>
        <div class="skeleton-cell" style="width: 25%;"></div>
    </div>
    {% endfor %}
</div>

<script>
// Show skeleton while loading
function showSkeleton(containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <div class="skeleton-loader">
            ${Array(5).fill(`
                <div class="skeleton-row">
                    <div class="skeleton-cell" style="width: 20%;"></div>
                    <div class="skeleton-cell" style="width: 30%;"></div>
                    <div class="skeleton-cell" style="width: 25%;"></div>
                    <div class="skeleton-cell" style="width: 25%;"></div>
                </div>
            `).join('')}
        </div>
    `;
}

function hideSkeleton(containerId) {
    const skeleton = document.querySelector(`#${containerId} .skeleton-loader`);
    if (skeleton) skeleton.remove();
}
</script>

<style>
.skeleton-loader {
    animation: fadeIn 0.3s;
}

.skeleton-row {
    display: flex;
    gap: 16px;
    margin-bottom: 12px;
    padding: 16px;
    background: white;
    border-radius: 8px;
}

.skeleton-cell {
    height: 20px;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    border-radius: 4px;
    animation: loading 1.5s infinite;
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@media (max-width: 768px) {
    .skeleton-row {
        gap: 8px;
        padding: 12px;
    }
}
</style>
```

**Kullanım:**
```html
<div id="equipment-list">
    {% include 'components/skeleton_loader.html' %}
</div>

<script>
document.addEventListener('DOMContentLoaded', async () => {
    showSkeleton('equipment-list');
    
    try {
        const response = await fetch('/api/equipment');
        const data = await response.json();
        
        hideSkeleton('equipment-list');
        
        // Render actual data
        document.getElementById('equipment-list').innerHTML = 
            data.map(e => `<div>${e.code}</div>`).join('');
    } catch (error) {
        hideSkeleton('equipment-list');
        ToastManager.error(error.message);
    }
});
</script>
```

---

## COMPONENT 5: Enhanced Table with Row Selection

**Dosya:** `templates/components/enhanced_table.html` OLUŞTUR

```html
<!-- Enhanced Table Component -->
<div class="table-container">
    <div class="table-header">
        <div class="table-select-info" style="display: none;">
            <span id="selected-count">0</span> selected
            <a href="#" onclick="deleteSelected(event)" class="text-danger">Delete</a>
        </div>
    </div>
    
    <table class="table table-hover enhanced-table">
        <thead>
            <tr>
                <th style="width: 40px;">
                    <input type="checkbox" id="select-all" class="form-check-input">
                </th>
                <th>Code</th>
                <th>Status</th>
                <th>Last Maintenance</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody id="table-body">
            <!-- Rows will be inserted here -->
        </tbody>
    </table>
</div>

<script>
class EnhancedTable {
    constructor(tableSelector) {
        this.table = document.querySelector(tableSelector);
        this.selectAll = this.table.querySelector('#select-all');
        this.tableBody = this.table.querySelector('#table-body');
        
        this.selectAll.addEventListener('change', (e) => this.selectAllRows(e.target.checked));
    }
    
    addRow(data) {
        const row = document.createElement('tr');
        row.classList.add('table-row');
        row.dataset.id = data.id;
        row.innerHTML = `
            <td>
                <input type="checkbox" class="form-check-input row-select">
            </td>
            <td><strong>${data.code}</strong></td>
            <td><span class="badge badge-${data.status_class}">${data.status}</span></td>
            <td>${data.last_maintenance}</td>
            <td>
                <a href="/equipment/${data.id}/edit" class="btn btn-sm btn-outline-primary">Edit</a>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteRow(${data.id})">Delete</button>
            </td>
        `;
        
        // Row click handler
        row.addEventListener('click', (e) => {
            if (e.target.tagName !== 'BUTTON' && !e.target.classList.contains('row-select')) {
                window.location.href = `/equipment/${data.id}/edit`;
            }
        });
        
        // Checkbox handler
        row.querySelector('.row-select').addEventListener('change', () => this.updateSelectAll());
        
        this.tableBody.appendChild(row);
    }
    
    selectAllRows(checked) {
        this.tableBody.querySelectorAll('.row-select').forEach(checkbox => {
            checkbox.checked = checked;
        });
        this.updateSelectAll();
    }
    
    updateSelectAll() {
        const total = this.tableBody.querySelectorAll('.row-select').length;
        const checked = this.tableBody.querySelectorAll('.row-select:checked').length;
        
        this.selectAll.checked = checked === total && total > 0;
        this.selectAll.indeterminate = checked > 0 && checked < total;
        
        const info = this.table.querySelector('.table-select-info');
        if (checked > 0) {
            info.style.display = 'block';
            document.getElementById('selected-count').textContent = checked;
        } else {
            info.style.display = 'none';
        }
    }
    
    getSelected() {
        const selected = [];
        this.tableBody.querySelectorAll('.row-select:checked').forEach(checkbox => {
            selected.push(checkbox.closest('.table-row').dataset.id);
        });
        return selected;
    }
}
</script>

<style>
.table-container {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.table-header {
    padding: 16px;
    border-bottom: 1px solid #f1f5f9;
}

.table-select-info {
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 14px;
    color: #64748b;
}

.enhanced-table {
    margin-bottom: 0;
}

.enhanced-table thead th {
    background: #f8fafc;
    border-color: #f1f5f9;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    font-size: 12px;
    letter-spacing: 0.5px;
}

.table-row {
    transition: background-color 0.2s;
}

.table-row:hover {
    background-color: #f8fafc;
    cursor: pointer;
}

.table-row.selected {
    background-color: #dbeafe;
    border-left: 4px solid #2563eb;
}

@media (max-width: 768px) {
    .enhanced-table {
        font-size: 13px;
    }
    
    .enhanced-table th,
    .enhanced-table td {
        padding: 12px 10px;
    }
}
</style>
```

---

## ✅ INSTALLATION CHECKLIST

**Hafta 1 (HEMEN):**
- [ ] Toast system ekle (base.html'ye include et)
- [ ] Form validation ekle (tüm form'lara)
- [ ] Empty states ekle (tüm list'lere)

**Hafta 2:**
- [ ] Skeleton loader ekle (equipment, failures)
- [ ] Enhanced table ekle (main lists)
- [ ] Breadcrumbs ekle (detail pages)

---

**Hepsi:** Copy-paste yapılabilir, production-ready kod

