/**
 * Admin Management - Shared JavaScript Utilities
 * Provides reusable functions for AJAX operations, modals, tables, and more
 */

// CSRF Token handling
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Toast Notification System
class Toast {
    static show(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="bi bi-${this.getIcon(type)} me-2"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    static getIcon(type) {
        const icons = {
            success: 'check-circle-fill',
            error: 'exclamation-circle-fill',
            warning: 'exclamation-triangle-fill',
            info: 'info-circle-fill'
        };
        return icons[type] || icons.info;
    }
}

// Modal Management
class Modal {
    constructor(modalId) {
        this.modal = document.getElementById(modalId);
        this.bsModal = new bootstrap.Modal(this.modal);
    }
    
    show() {
        this.bsModal.show();
    }
    
    hide() {
        this.bsModal.hide();
    }
    
    setTitle(title) {
        const titleEl = this.modal.querySelector('.modal-title');
        if (titleEl) titleEl.textContent = title;
    }
    
    setContent(content) {
        const bodyEl = this.modal.querySelector('.modal-body');
        if (bodyEl) bodyEl.innerHTML = content;
    }
    
    onSave(callback) {
        const saveBtn = this.modal.querySelector('.btn-save');
        if (saveBtn) {
            saveBtn.onclick = callback;
        }
    }
}

// AJAX Form Handler
class AjaxForm {
    constructor(formId, options = {}) {
        this.form = document.getElementById(formId);
        this.submitBtn = options.submitBtn;
        this.onSuccess = options.onSuccess;
        this.onError = options.onError;
        
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(this.form);
        const url = this.form.action;
        const method = this.form.method || 'POST';
        
        // Disable submit button
        if (this.submitBtn) {
            this.submitBtn.disabled = true;
            this.submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Yuklanmoqda...';
        }
        
        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                Toast.show(data.message || 'Muvaffaqiyatli saqlandi!', 'success');
                if (this.onSuccess) this.onSuccess(data);
            } else {
                Toast.show(data.message || 'Xatolik yuz berdi!', 'error');
                if (this.onError) this.onError(data);
            }
        } catch (error) {
            console.error('Form submission error:', error);
            Toast.show('Tarmoq xatosi!', 'error');
            if (this.onError) this.onError(error);
        } finally {
            // Re-enable submit button
            if (this.submitBtn) {
                this.submitBtn.disabled = false;
                this.submitBtn.innerHTML = this.submitBtn.dataset.originalText || 'Saqlash';
            }
        }
    }
    
    reset() {
        if (this.form) this.form.reset();
    }
    
    setValues(data) {
        if (!this.form) return;
        
        for (const [key, value] of Object.entries(data)) {
            const input = this.form.querySelector(`[name="${key}"]`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = value;
                } else {
                    input.value = value;
                }
            }
        }
    }
}

// Table Management
class DataTable {
    constructor(tableId, options = {}) {
        this.table = document.getElementById(tableId);
        this.searchInput = options.searchInput;
        this.filterSelects = options.filterSelects || [];
        this.paginationContainer = options.paginationContainer;
        this.currentPage = 1;
        this.itemsPerPage = options.itemsPerPage || 20;
        
        this.init();
    }
    
    init() {
        if (this.searchInput) {
            document.getElementById(this.searchInput).addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }
        
        this.filterSelects.forEach(selectId => {
            document.getElementById(selectId)?.addEventListener('change', () => {
                this.handleFilter();
            });
        });
    }
    
    handleSearch(query) {
        // Implement search logic
        this.reload({ search: query });
    }
    
    handleFilter() {
        const filters = {};
        this.filterSelects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select && select.value) {
                filters[select.name] = select.value;
            }
        });
        this.reload({ filters });
    }
    
    async reload(params = {}) {
        // To be implemented with actual AJAX call
        console.log('Reloading table with params:', params);
    }
}

// Bulk Actions Handler
class BulkActions {
    constructor(options = {}) {
        this.checkboxSelector = options.checkboxSelector || '.item-checkbox';
        this.selectAllCheckbox = options.selectAllCheckbox;
        this.bulkActionsContainer = options.bulkActionsContainer;
        this.selectedItems = new Set();
        
        this.init();
    }
    
    init() {
        // Select all checkbox
        if (this.selectAllCheckbox) {
            document.getElementById(this.selectAllCheckbox)?.addEventListener('change', (e) => {
                this.toggleSelectAll(e.target.checked);
            });
        }
        
        // Individual checkboxes
        document.querySelectorAll(this.checkboxSelector).forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.toggleItem(e.target.value, e.target.checked);
            });
        });
    }
    
    toggleSelectAll(checked) {
        document.querySelectorAll(this.checkboxSelector).forEach(checkbox => {
            checkbox.checked = checked;
            this.toggleItem(checkbox.value, checked);
        });
        this.updateUI();
    }
    
    toggleItem(itemId, selected) {
        if (selected) {
            this.selectedItems.add(itemId);
        } else {
            this.selectedItems.delete(itemId);
        }
        this.updateUI();
    }
    
    updateUI() {
        const count = this.selectedItems.size;
        const container = document.getElementById(this.bulkActionsContainer);
        
        if (container) {
            if (count > 0) {
                container.classList.remove('d-none');
                container.querySelector('.selected-count')?.textContent = count;
            } else {
                container.classList.add('d-none');
            }
        }
    }
    
    getSelectedItems() {
        return Array.from(this.selectedItems);
    }
    
    clearSelection() {
        this.selectedItems.clear();
        document.querySelectorAll(this.checkboxSelector).forEach(checkbox => {
            checkbox.checked = false;
        });
        this.updateUI();
    }
    
    async executeAction(action, url) {
        const items = this.getSelectedItems();
        if (items.length === 0) {
            Toast.show('Hech narsa tanlanmagan!', 'warning');
            return;
        }
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ action, items })
            });
            
            const data = await response.json();
            
            if (data.success) {
                Toast.show(data.message, 'success');
                this.clearSelection();
                // Reload table or update UI
                return true;
            } else {
                Toast.show(data.message || 'Xatolik yuz berdi!', 'error');
                return false;
            }
        } catch (error) {
            console.error('Bulk action error:', error);
            Toast.show('Tarmoq xatosi!', 'error');
            return false;
        }
    }
}

// Confirmation Dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Delete with confirmation
async function deleteItem(url, itemName, onSuccess) {
    if (!confirm(`${itemName}ni o'chirishga ishonchingiz komilmi?`)) {
        return;
    }
    
    try {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            Toast.show(data.message || 'Muvaffaqiyatli o\'chirildi!', 'success');
            if (onSuccess) onSuccess(data);
        } else {
            Toast.show(data.message || 'Xatolik yuz berdi!', 'error');
        }
    } catch (error) {
        console.error('Delete error:', error);
        Toast.show('Tarmoq xatosi!', 'error');
    }
}

// Export global utilities
window.AdminUtils = {
    Toast,
    Modal,
    AjaxForm,
    DataTable,
    BulkActions,
    confirmAction,
    deleteItem,
    csrftoken
};
