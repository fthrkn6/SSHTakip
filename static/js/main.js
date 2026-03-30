// Ana JavaScript dosyası

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function () {
    try {
        // Tooltip'leri başlat
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }

        // Popover'ları başlat
        if (typeof bootstrap !== 'undefined' && bootstrap.Popover) {
            var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
            popoverTriggerList.map(function (popoverTriggerEl) {
                return new bootstrap.Popover(popoverTriggerEl);
            });
        }

        // Auto-hide alerts (grafik uyarıları hariç)
        setTimeout(function () {
            var alerts = document.querySelectorAll('.alert:not(.alert-danger):not(.alert-warning)');
            alerts.forEach(function (alert) {
                try {
                    if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                        var bsAlert = new bootstrap.Alert(alert);
                        bsAlert.close();
                    }
                } catch(e) {}
            });
        }, 5000);
    } catch(e) {
        console.warn('Bootstrap init hatası:', e);
    }
});

// Grafik İndirme Fonksiyonu
function downloadChartAsImage(canvasId, chartTitle = 'grafik') {
    try {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas bulunamadı: ${canvasId}`);
            showToast('Hata', 'Grafik bulunamadı', 'danger');
            return;
        }

        // Canvas'ı PNG olarak indir
        const link = document.createElement('a');
        link.href = canvas.toDataURL('image/png');
        
        // Tarihi ekle
        const now = new Date();
        const dateStr = now.toISOString().split('T')[0];
        const timeStr = now.toTimeString().split(' ')[0].replace(/:/g, '-');
        
        link.download = `${chartTitle}_${dateStr}_${timeStr}.png`;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showToast('Başarılı', `"${chartTitle}" grafik indirildi`, 'success');
    } catch (error) {
        console.error('Grafik indirme hatası:', error);
        showToast('Hata', 'Grafik indirilmesi başarısız oldu', 'danger');
    }
}

// Tarih formatı
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR');
}

// Zaman farkı hesaplama
function timeAgo(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + " yıl önce";

    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + " ay önce";

    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + " gün önce";

    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + " saat önce";

    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + " dakika önce";

    return Math.floor(seconds) + " saniye önce";
}

// AJAX form submit with loading state
function submitForm(url, formData, successCallback, btn) {
    if (btn) setButtonLoading(btn, true);
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
        .then(response => response.json())
        .then(data => {
            if (btn) setButtonLoading(btn, false);
            if (data.success) {
                if (successCallback) successCallback(data);
            } else {
                showToast('Hata', data.error || 'İşlem başarısız', 'danger');
            }
        })
        .catch(error => {
            if (btn) setButtonLoading(btn, false);
            showToast('Hata', 'Sunucu hatası: ' + error, 'danger');
        });
}

// Toast notification - Enhanced
function showToast(title, message, type = 'info') {
    // Sanitize text content
    const div = document.createElement('div');
    div.textContent = title;
    const safeTitle = div.innerHTML;
    div.textContent = message;
    const safeMessage = div.innerHTML;
    
    const iconMap = {
        success: 'bi-check-circle-fill',
        danger: 'bi-exclamation-circle-fill',
        warning: 'bi-exclamation-triangle-fill',
        info: 'bi-info-circle-fill'
    };
    const icon = iconMap[type] || iconMap.info;
    
    const toastHtml = `
        <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="5000">
            <div class="toast-header bg-${type} text-white">
                <i class="bi ${icon} me-2"></i>
                <strong class="me-auto">${safeTitle}</strong>
                <small class="text-white-50">Şimdi</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Kapat"></button>
            </div>
            <div class="toast-body">
                ${safeMessage}
            </div>
        </div>
    `;

    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }

    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', function () {
        toastElement.remove();
    });
}

// Loading spinner - Enhanced
function showLoading(text) {
    const spinnerHtml = `
        <div class="spinner-overlay" id="globalSpinner">
            <div class="spinner-border text-light" role="status" style="width: 3rem; height: 3rem;">
                <span class="visually-hidden">Yükleniyor...</span>
            </div>
            ${text ? `<div class="spinner-text">${text}</div>` : ''}
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', spinnerHtml);
}

function hideLoading() {
    const spinner = document.getElementById('globalSpinner');
    if (spinner) spinner.remove();
}

// Button loading state
function setButtonLoading(btn, loading) {
    if (!btn) return;
    if (loading) {
        btn.dataset.originalText = btn.innerHTML;
        btn.innerHTML = `<span class="btn-text">${btn.textContent}</span>`;
        btn.classList.add('btn-loading');
        btn.disabled = true;
    } else {
        btn.innerHTML = btn.dataset.originalText || btn.innerHTML;
        btn.classList.remove('btn-loading');
        btn.disabled = false;
    }
}

// Confirm dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Export table to CSV
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    let csv = [];

    const rows = table.querySelectorAll('tr');

    for (let i = 0; i < rows.length; i++) {
        let row = [], cols = rows[i].querySelectorAll('td, th');

        for (let j = 0; j < cols.length; j++) {
            row.push(cols[j].innerText);
        }

        csv.push(row.join(','));
    }

    downloadCSV(csv.join('\n'), filename);
}

function downloadCSV(csv, filename) {
    const csvFile = new Blob([csv], { type: 'text/csv' });
    const downloadLink = document.createElement('a');
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = 'none';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

// Real-time updates için WebSocket (opsiyonel)
// function initWebSocket() {
//     const ws = new WebSocket('ws://localhost:5000/ws');
//     
//     ws.onmessage = function(event) {
//         const data = JSON.parse(event.data);
//         handleRealtimeUpdate(data);
//     };
// }
// Parça Kodu - Parça Adı Lookup (Autocomplete)
document.addEventListener('DOMContentLoaded', function () {
    const koduInput = document.getElementById('parca_kodu_input');
    const koduList = document.getElementById('parca_kodu_list');
    const adiInput = document.getElementById('parca_adi_input');
    const adiList = document.getElementById('parca_adi_list');

    if (!koduInput) return; // Sayfa bileşen bulmamazsa çık

    // Proje bilgisini al
    const form = document.getElementById('arizaBildirimForm');
    const project = form ? form.dataset.project || 'belgrad' : 'belgrad';

    // Helper: API'den veri çek
    async function fetchParts(query) {
        if (query.length < 2) return [];
        try {
            const response = await fetch(`/api/parts-lookup?q=${encodeURIComponent(query)}&project=${encodeURIComponent(project)}`);
            return await response.json();
        } catch (e) {
            console.error('Parça lookup hatası:', e);
            return [];
        }
    }

    // Bileşen Numarası input
    koduInput.addEventListener('input', async function (e) {
        const query = this.value.trim();
        koduList.innerHTML = '';

        if (query.length < 2) {
            koduList.style.display = 'none';
            return;
        }

        const parts = await fetchParts(query);
        if (parts.length === 0) {
            koduList.style.display = 'none';
            return;
        }

        parts.forEach(part => {
            const li = document.createElement('li');
            li.className = 'list-group-item list-group-item-action';
            li.style.cursor = 'pointer';
            li.innerHTML = `<strong>${part.bilesen_no}</strong> - ${part.nesne_metni}`;
            li.addEventListener('click', function () {
                koduInput.value = part.bilesen_no;
                adiInput.value = part.nesne_metni;
                koduList.style.display = 'none';
                adiList.style.display = 'none';
            });
            koduList.appendChild(li);
        });

        koduList.style.display = 'block';
    });

    // Nesne Kısa Metni input
    adiInput.addEventListener('input', async function (e) {
        const query = this.value.trim();
        adiList.innerHTML = '';

        if (query.length < 2) {
            adiList.style.display = 'none';
            return;
        }

        const parts = await fetchParts(query);
        if (parts.length === 0) {
            adiList.style.display = 'none';
            return;
        }

        parts.forEach(part => {
            const li = document.createElement('li');
            li.className = 'list-group-item list-group-item-action';
            li.style.cursor = 'pointer';
            li.innerHTML = `<strong>${part.nesne_metni}</strong> - ${part.bilesen_no}`;
            li.addEventListener('click', function () {
                adiInput.value = part.nesne_metni;
                koduInput.value = part.bilesen_no;
                adiList.style.display = 'none';
                koduList.style.display = 'none';
            });
            adiList.appendChild(li);
        });

        adiList.style.display = 'block';
    });

    // Dış tıklama - dropdown kapatma
    document.addEventListener('click', function (e) {
        if (e.target !== koduInput && e.target !== adiInput) {
            koduList.style.display = 'none';
            adiList.style.display = 'none';
        }
    });
});

// ===== FORM VALIDATION =====
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        removeFieldError(field);
        
        if (!field.value.trim()) {
            showFieldError(field, 'Bu alan zorunludur');
            isValid = false;
        } else if (field.type === 'email' && !isValidEmail(field.value)) {
            showFieldError(field, 'Geçerli bir e-posta adresi girin');
            isValid = false;
        } else if (field.type === 'number' && field.min && parseFloat(field.value) < parseFloat(field.min)) {
            showFieldError(field, `Minimum değer: ${field.min}`);
            isValid = false;
        } else {
            field.classList.add('is-valid');
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    
    let feedback = field.parentElement.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        field.parentElement.appendChild(feedback);
    }
    feedback.textContent = message;
    feedback.style.display = 'block';
}

function removeFieldError(field) {
    field.classList.remove('is-invalid', 'is-valid');
    const feedback = field.parentElement.querySelector('.invalid-feedback');
    if (feedback) feedback.style.display = 'none';
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Auto-attach form validation
document.addEventListener('DOMContentLoaded', function() {
    // Add validation on form submit
    document.querySelectorAll('form[data-validate]').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                e.stopPropagation();
                showToast('Uyarı', 'Lütfen zorunlu alanları doldurun', 'warning');
            }
        });
    });
    
    // Real-time validation on blur
    document.querySelectorAll('form [required]').forEach(field => {
        field.addEventListener('blur', function() {
            if (this.value.trim()) {
                removeFieldError(this);
                this.classList.add('is-valid');
            }
        });
        
        field.addEventListener('input', function() {
            if (this.classList.contains('is-invalid') && this.value.trim()) {
                removeFieldError(this);
            }
        });
    });
    
    // Add loading state to all forms with data-loading attribute
    document.querySelectorAll('form[data-loading]').forEach(form => {
        form.addEventListener('submit', function() {
            const btn = this.querySelector('[type="submit"]');
            if (btn && !this.querySelector('.is-invalid')) {
                setButtonLoading(btn, true);
            }
        });
    });
});

// ===== TABLE SORTING =====
function initSortableTables() {
    document.querySelectorAll('.table-sortable').forEach(table => {
        const headers = table.querySelectorAll('thead th');
        const tbody = table.querySelector('tbody');
        if (!tbody) return;
        
        headers.forEach((header, index) => {
            if (header.dataset.noSort) return;
            
            header.addEventListener('click', function() {
                const isAsc = this.classList.contains('sort-asc');
                
                // Reset all headers
                headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
                
                // Set current sort
                this.classList.add(isAsc ? 'sort-desc' : 'sort-asc');
                
                // Sort rows
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const direction = isAsc ? -1 : 1;
                
                rows.sort((a, b) => {
                    const aVal = a.cells[index]?.textContent.trim() || '';
                    const bVal = b.cells[index]?.textContent.trim() || '';
                    
                    // Try numeric comparison
                    const aNum = parseFloat(aVal.replace(/[^0-9.-]/g, ''));
                    const bNum = parseFloat(bVal.replace(/[^0-9.-]/g, ''));
                    
                    if (!isNaN(aNum) && !isNaN(bNum)) {
                        return (aNum - bNum) * direction;
                    }
                    
                    return aVal.localeCompare(bVal, 'tr') * direction;
                });
                
                rows.forEach(row => tbody.appendChild(row));
            });
        });
    });
}

// ===== TABLE PAGINATION =====
function initTablePagination() {
    document.querySelectorAll('[data-paginate]').forEach(wrapper => {
        const table = wrapper.querySelector('table');
        if (!table) return;
        
        const tbody = table.querySelector('tbody');
        if (!tbody) return;
        
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const perPage = parseInt(wrapper.dataset.paginate) || 20;
        let currentPage = 1;
        const totalPages = Math.ceil(rows.length / perPage);
        
        if (totalPages <= 1) return;
        
        // Create pagination UI
        const paginationDiv = document.createElement('div');
        paginationDiv.className = 'table-pagination';
        paginationDiv.innerHTML = `
            <span class="pagination-info"></span>
            <nav>
                <ul class="pagination pagination-sm">
                    <li class="page-item"><a class="page-link" data-page="prev" href="#">&laquo;</a></li>
                    <li class="page-item"><a class="page-link" data-page="next" href="#">&raquo;</a></li>
                </ul>
            </nav>
        `;
        wrapper.appendChild(paginationDiv);
        
        const pageList = paginationDiv.querySelector('.pagination');
        const nextBtn = pageList.querySelector('[data-page="next"]').parentElement;
        
        // Create page buttons
        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement('li');
            li.className = 'page-item';
            li.innerHTML = `<a class="page-link" data-page="${i}" href="#">${i}</a>`;
            pageList.insertBefore(li, nextBtn);
        }
        
        function showPage(page) {
            currentPage = page;
            const start = (page - 1) * perPage;
            const end = start + perPage;
            
            rows.forEach((row, i) => {
                row.style.display = (i >= start && i < end) ? '' : 'none';
            });
            
            // Update pagination info
            const info = paginationDiv.querySelector('.pagination-info');
            info.textContent = `${start + 1}-${Math.min(end, rows.length)} / ${rows.length} kayıt`;
            
            // Update active state
            paginationDiv.querySelectorAll('.page-item').forEach(item => {
                const link = item.querySelector('.page-link');
                const p = link.dataset.page;
                item.classList.toggle('active', p == page);
                
                if (p === 'prev') item.classList.toggle('disabled', page === 1);
                if (p === 'next') item.classList.toggle('disabled', page === totalPages);
            });
        }
        
        // Event delegation for pagination
        paginationDiv.addEventListener('click', function(e) {
            e.preventDefault();
            const link = e.target.closest('.page-link');
            if (!link) return;
            
            const page = link.dataset.page;
            if (page === 'prev' && currentPage > 1) showPage(currentPage - 1);
            else if (page === 'next' && currentPage < totalPages) showPage(currentPage + 1);
            else if (page !== 'prev' && page !== 'next') showPage(parseInt(page));
        });
        
        showPage(1);
    });
}

// ===== TABLE SEARCH =====
function initTableSearch() {
    document.querySelectorAll('[data-table-search]').forEach(input => {
        const tableId = input.dataset.tableSearch;
        const table = document.getElementById(tableId);
        if (!table) return;
        
        const tbody = table.querySelector('tbody');
        if (!tbody) return;
        
        input.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            const rows = tbody.querySelectorAll('tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    });
}

// Initialize all table features (auto-detect)
document.addEventListener('DOMContentLoaded', function() {
    // Auto-add sortable to all table-hover tables
    document.querySelectorAll('.table-hover').forEach(table => {
        if (!table.classList.contains('table-sortable') && table.querySelector('thead')) {
            table.classList.add('table-sortable');
        }
    });
    
    // Auto-paginate tables with more than 25 rows
    document.querySelectorAll('.table-hover').forEach(table => {
        const tbody = table.querySelector('tbody');
        if (tbody && tbody.querySelectorAll('tr').length > 25) {
            let wrapper = table.closest('[data-paginate]');
            if (!wrapper) {
                wrapper = table.closest('.table-responsive') || table.parentElement;
                wrapper.dataset.paginate = '25';
            }
        }
    });
    
    initSortableTables();
    initTablePagination();
    initTableSearch();
});