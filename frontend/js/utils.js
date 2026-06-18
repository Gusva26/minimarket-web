const Utils = {
  formatMoney(n) { return 'S/ ' + parseFloat(n || 0).toFixed(2); },
  formatDate(d) { return new Date(d).toLocaleDateString('es-PE', {year:'numeric',month:'2-digit',day:'2-digit'}); },
  formatDateTime(d) { return new Date(d).toLocaleString('es-PE'); },

  showToast(msg, type = 'success', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle', danger: 'fa-exclamation-circle' };
    const toast = document.createElement('div');
    toast.className = `toast-custom toast-${type === 'danger' ? 'error' : type}`;
    toast.innerHTML = `
      <i class="fas ${icons[type] || icons.info} toast-icon"></i>
      <div class="toast-body">${msg}</div>
      <button class="toast-close" onclick="this.closest('.toast-custom').remove()"><i class="fas fa-times"></i></button>
      <div class="toast-progress" style="animation-duration:${duration}ms"></div>
    `;
    container.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('toast-out');
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },

  showConfirm(title, text, confirmText = 'Sí', cancelText = 'Cancelar') {
    return Swal.fire({
      title, text, icon: 'warning',
      showCancelButton: true,
      confirmButtonText: confirmText,
      cancelButtonText: cancelText,
      confirmButtonColor: '#ef4444',
      cancelButtonColor: '#64748b',
      reverseButtons: true,
      borderRadius: '12px',
    });
  },

  showLoading() {
    return Swal.fire({
      title: 'Cargando...',
      allowOutsideClick: false,
      didOpen: () => Swal.showLoading(),
      background: 'var(--surface)',
      color: 'var(--text)',
    });
  },

  showSkeleton(container, rows = 5) {
    let html = '';
    for (let i = 0; i < rows; i++) {
      html += '<div class="skeleton skeleton-table-row" style="width:' + (85 + Math.random() * 15) + '%"></div>';
    }
    container.innerHTML = `<div class="p-4">${html}</div>`;
  },

  renderPagination(data, containerId, currentPage, callback) {
    const container = document.getElementById(containerId);
    if (!container) return;
    if (!data.previous && !data.next) { container.innerHTML = ''; return; }

    const current = currentPage || 1;
    if (data.next && data.results && data.results.length) {
      this._pageSize = data.results.length;
    }
    const pageSize = this._pageSize || 25;
    const total = data.total_pages || (data.count != null && data.count > 0 ? Math.ceil(data.count / pageSize) : 1);

    let html = '<div class="pagination-modern">';
    html += `<button class="page-btn" data-page="${current - 1}" ${data.previous ? '' : 'disabled'}><i class="fas fa-chevron-left"></i></button>`;

    const start = Math.max(1, current - 2);
    const end = Math.min(total, current + 2);

    if (start > 1) {
      html += `<button class="page-btn" data-page="1">1</button>`;
      if (start > 2) html += `<span class="page-info">...</span>`;
    }

    for (let i = start; i <= end; i++) {
      html += `<button class="page-btn ${i === current ? 'active' : ''}" data-page="${i}">${i}</button>`;
    }

    if (end < total) {
      if (end < total - 1) html += `<span class="page-info">...</span>`;
      html += `<button class="page-btn" data-page="${total}">${total}</button>`;
    }

    html += `<button class="page-btn" data-page="${current + 1}" ${data.next ? '' : 'disabled'}><i class="fas fa-chevron-right"></i></button>`;
    html += '</div>';

    if (container._paginationListener) {
      container.removeEventListener('click', container._paginationListener);
    }
    container.innerHTML = html;
    container._cb = callback;
    container._paginationListener = (e) => {
      const btn = e.target.closest('.page-btn');
      if (!btn || btn.disabled) return;
      const page = parseInt(btn.dataset.page);
      if (isNaN(page)) return;
      if (container._cb) container._cb(page);
    };
    container.addEventListener('click', container._paginationListener);
  },

  renderSimpleTable(headers, rows, emptyMsg = 'No hay registros') {
    if (!rows || rows.length === 0) return `<div class="empty-state"><div class="empty-icon"><i class="fas fa-inbox"></i></div><div class="empty-title">${emptyMsg}</div></div>`;
    let html = '<div class="table-container"><div class="table-responsive"><table class="table"><thead><tr>';
    headers.forEach(h => { html += `<th>${h}</th>`; });
    html += '</tr></thead><tbody>';
    rows.forEach(r => { html += '<tr>'; r.forEach(c => { html += `<td>${c}</td>`; }); html += '</tr>'; });
    html += '</tbody></table></div></div>';
    return html;
  },

  showModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    const root = document.getElementById('modal-root');
    if (root && el.parentNode !== root) {
      root.appendChild(el);
    }
    el.classList.add('active');
    document.body.classList.add('modal-open');
  },

  hideModal(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('active');
    document.body.classList.remove('modal-open');
  },

  clearModals() {
    const root = document.getElementById('modal-root');
    if (root) root.innerHTML = '';
  },

  initFloatingSelects(container) {
    container.querySelectorAll('.form-select').forEach(sel => {
      const update = () => { if (sel.value) sel.classList.add('has-value'); else sel.classList.remove('has-value'); };
      sel.addEventListener('change', update);
      update();
    });
  },

  debounce(func, wait) {
    let timeout;
    return function(...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  },
};
