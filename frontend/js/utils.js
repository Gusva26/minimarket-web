const Utils = {
  escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  },

  /**
   * Obtiene un elemento del DOM y retorna null si no existe (en lugar de lanzar error).
   * Usar para evitar errores cuando se navega entre páginas antes de que terminen de cargar.
   */
  el(id) { return document.getElementById(id); },
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
    if (!container || !data) return;

    const current = currentPage || data.current_page || 1;
    if (data.next && data.results && data.results.length) {
      this._pageSize = data.results.length;
    }
    const pageSize = this._pageSize || 25;
    const total = data.total_pages || data.num_pages || (data.count != null && data.count > 0 ? Math.ceil(data.count / pageSize) : 1);

    if (total <= 1) { container.innerHTML = ''; return; }

    const hasPrev = !!(data.previous || data.has_previous || current > 1);
    const hasNext = !!(data.next || data.has_next || current < total);

    let html = '<div class="pagination-modern">';
    html += `<button class="page-btn" data-page="${current - 1}" ${hasPrev ? '' : 'disabled'}><i class="fas fa-chevron-left"></i></button>`;

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

    html += `<button class="page-btn" data-page="${current + 1}" ${hasNext ? '' : 'disabled'}><i class="fas fa-chevron-right"></i></button>`;
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

  initGlobalValidations() {
    if (this._validationsInitialized) return;
    this._validationsInitialized = true;

    const getRestrictionType = (input) => {
      if (!input || input.tagName !== 'INPUT') return null;
      const type = input.type ? input.type.toLowerCase() : '';
      if (['password', 'file', 'checkbox', 'radio', 'date', 'time', 'color'].includes(type)) return null;

      const dType = (input.dataset.type || '').toLowerCase();
      const name = (input.name || '').toLowerCase();
      const id = (input.id || '').toLowerCase();

      if (dType === 'dni' || name === 'dni' || id.includes('dni')) return 'dni';
      if (dType === 'ruc' || name === 'ruc' || id.includes('ruc')) return 'ruc';
      if (dType === 'phone' || dType === 'celular' || name === 'telefono' || name === 'celular' || id.includes('telefono') || id.includes('celular')) return 'phone';

      if (name === 'num_documento' || id.includes('documento')) {
        const form = input.closest('form') || input.closest('.modal-card') || document;
        const tipoDoc = form.querySelector('[name="tipo_documento"], #cliente_tipo_doc, select[name*="tipo_doc"]');
        if (tipoDoc && (tipoDoc.value === 'RUC' || tipoDoc.value === '6')) return 'ruc';
        if (input.maxLength === 11) return 'ruc';
        return 'dni';
      }
      return null;
    };

    const applyRestriction = (input) => {
      const rType = getRestrictionType(input);
      if (!rType) return;

      let maxLen = 8;
      if (rType === 'dni') maxLen = 8;
      else if (rType === 'ruc') maxLen = 11;
      else if (rType === 'phone') maxLen = 9;

      input.setAttribute('maxlength', maxLen);
      input.setAttribute('inputmode', 'numeric');

      const digits = input.value.replace(/\D/g, '').slice(0, maxLen);
      if (input.value !== digits) {
        input.value = digits;
      }
    };

    document.addEventListener('input', (e) => applyRestriction(e.target));
    document.addEventListener('focusin', (e) => applyRestriction(e.target));

    document.addEventListener('paste', (e) => {
      const input = e.target;
      const rType = getRestrictionType(input);
      if (!rType) return;

      e.preventDefault();
      const pastedText = (e.clipboardData || window.clipboardData).getData('text') || '';
      let digits = pastedText.replace(/\D/g, '');
      let maxLen = 8;
      if (rType === 'dni') maxLen = 8;
      else if (rType === 'ruc') maxLen = 11;
      else if (rType === 'phone') maxLen = 9;

      input.setAttribute('maxlength', maxLen);
      input.value = digits.slice(0, maxLen);
      input.dispatchEvent(new Event('input', { bubbles: true }));
    });
  },

  debounce(func, wait) {

    let timeout;
    return function(...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  },

  imprimirGuiaTransferencia(t) {
    const origNombre = t.mercado_origen_nombre || t.mercado_origen?.nombre || 'Listo! Express - Origen';
    const destNombre = t.mercado_destino_nombre || t.mercado_destino?.nombre || 'Listo! Express - Destino';
    const envUser = t.usuario_envio_nombre || t.usuario_envio?.username || 'Administrador Origen';
    const recUser = t.usuario_recepcion_nombre || t.usuario_recepcion?.username || 'Pendiente de Recepción';
    const fechaEnvio = Utils.formatDateTime(t.fecha_envio);
    const fechaRec = t.fecha_recepcion ? Utils.formatDateTime(t.fecha_recepcion) : 'Pendiente de recepción';

    const detallesHtml = (t.detalles || []).map((d, i) => `
      <tr>
        <td style="text-align:center;padding:10px;border-bottom:1px solid #e2e8f0;font-size:12px;">${i + 1}</td>
        <td style="padding:10px;border-bottom:1px solid #e2e8f0;font-size:12px;font-weight:600;">${Utils.escapeHtml(d.producto_origen_nombre || d.producto_origen?.nombre || '')}</td>
        <td style="text-align:center;padding:10px;border-bottom:1px solid #e2e8f0;font-size:12px;">${d.fecha_vencimiento ? Utils.formatDate(d.fecha_vencimiento) : '---'}</td>
        <td style="text-align:center;padding:10px;border-bottom:1px solid #e2e8f0;font-size:13px;font-weight:700;color:#0f172a;">${d.cantidad} und</td>
      </tr>
    `).join('');

    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <title>Guía de Recepción y Transferencia #${t.id}</title>
        <style>
          @page { size: A4 portrait; margin: 15mm; }
          body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; color: #0f172a; margin: 0; padding: 24px; background: #ffffff; line-height: 1.5; }
          .header-box { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 3px solid #0f172a; padding-bottom: 16px; margin-bottom: 24px; }
          .logo-title { font-size: 22px; font-weight: 800; color: #0f172a; text-transform: uppercase; letter-spacing: 0.5px; }
          .sub-title { font-size: 12px; color: #64748b; margin-top: 4px; font-weight: 500; }
          .doc-box { border: 2px solid #0f172a; padding: 10px 20px; text-align: center; border-radius: 8px; background: #f8fafc; min-width: 220px; }
          .doc-type { font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; }
          .doc-number { font-size: 20px; font-weight: 800; color: #4f46e5; margin-top: 2px; }
          .route-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
          .route-card { border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px; background: #f8fafc; }
          .route-label { font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
          .route-value { font-size: 14px; font-weight: 700; color: #0f172a; }
          .route-user { font-size: 11px; color: #475569; margin-top: 4px; }
          .badge-status { display: inline-block; padding: 4px 12px; font-size: 11px; font-weight: 700; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.03em; }
          .status-completada { background: #dcfce7; color: #15803d; }
          .status-transito { background: #fef3c7; color: #b45309; }
          .status-cancelada { background: #fee2e2; color: #b91c1c; }
          table { width: 100%; border-collapse: collapse; margin-bottom: 28px; }
          th { background: #0f172a; color: #ffffff; padding: 10px 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }
          .signature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 60px; margin-top: 70px; page-break-inside: avoid; }
          .signature-box { text-align: center; border-top: 1.5px dashed #475569; padding-top: 10px; }
          .signature-label { font-size: 11px; font-weight: 700; color: #1e293b; }
          .footer-note { margin-top: 40px; text-align: center; font-size: 10px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 12px; }
        </style>
      </head>
      <body>
        <div class="header-box">
          <div>
            <div class="logo-title">Listo! Convenience Stores</div>
            <div class="sub-title">Comercializadora Minimarket S.A.C. | RUC: 20601234567<br>Guía Interna de Control y Transferencia de Inventario</div>
          </div>
          <div class="doc-box">
            <div class="doc-type">Guía de Recepción</div>
            <div class="doc-number">GT-${String(t.id).padStart(6, '0')}</div>
          </div>
        </div>

        <div class="route-grid">
          <div class="route-card">
            <div class="route-label">📍 Sucursal de Origen (Despacho)</div>
            <div class="route-value">${Utils.escapeHtml(origNombre)}</div>
            <div class="route-user">Despachado por: <strong>${Utils.escapeHtml(envUser)}</strong></div>
            <div class="route-user">Fecha de Envío: ${fechaEnvio}</div>
          </div>
          <div class="route-card">
            <div class="route-label">🏁 Sucursal de Destino (Recepción)</div>
            <div class="route-value">${Utils.escapeHtml(destNombre)}</div>
            <div class="route-user">Recibido por: <strong>${Utils.escapeHtml(recUser)}</strong></div>
            <div class="route-user">Fecha de Recepción: ${fechaRec}</div>
          </div>
        </div>

        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
          <div><strong>Estado de Traslado:</strong> <span class="badge-status ${t.estado === 'COMPLETADA' ? 'status-completada' : (t.estado === 'CANCELADA' ? 'status-cancelada' : 'status-transito')}">${t.estado}</span></div>
          <div style="font-size:11px;color:#64748b;">Total Items: <strong>${(t.detalles || []).length} productos</strong></div>
        </div>

        <table>
          <thead>
            <tr>
              <th style="width:40px;text-align:center;">#</th>
              <th style="text-align:left;">Descripción del Producto</th>
              <th style="width:130px;text-align:center;">Vencimiento Lote</th>
              <th style="width:110px;text-align:center;">Cantidad Transferida</th>
            </tr>
          </thead>
          <tbody>
            ${detallesHtml}
          </tbody>
        </table>

        ${t.observaciones ? `
          <div style="border:1px solid #cbd5e1;padding:12px;border-radius:6px;margin-bottom:24px;background:#f8fafc;font-size:11px;">
            <strong>Observaciones de la Recepción:</strong> ${Utils.escapeHtml(t.observaciones)}
          </div>
        ` : ''}

        <div class="signature-grid">
          <div class="signature-box">
            <div class="signature-label">Firma Responsable Despacho (Origen)</div>
            <div style="font-size:10px;color:#64748b;margin-top:2px;">${Utils.escapeHtml(envUser)}</div>
          </div>
          <div class="signature-box">
            <div class="signature-label">Firma Responsable Recepción (Destino)</div>
            <div style="font-size:10px;color:#64748b;margin-top:2px;">${Utils.escapeHtml(recUser)}</div>
          </div>
        </div>

        <div class="footer-note">
          Documento Oficial Impreso desde Minimarket Web POS | Fecha impresión: ${new Date().toLocaleString('es-PE')}
        </div>

        <script>
          window.onload = function() { window.print(); };
        </script>
      </body>
      </html>
    `;

    const win = window.open('', '_blank', 'width=850,height=950');
    win.document.write(html);
    win.document.close();
  },

  imprimirComprobante(v) {
    const itemsHtml = (v.detalles || []).map((d) => `
      <tr>
        <td style="padding:4px 0;font-size:11px;text-align:center;vertical-align:top;">${d.cantidad}</td>
        <td style="padding:4px 0;font-size:11px;font-weight:600;vertical-align:top;">${Utils.escapeHtml(d.producto_nombre || d.producto?.nombre || '')}</td>
        <td style="padding:4px 0;font-size:11px;text-align:right;vertical-align:top;">${parseFloat(d.precio_unitario || 0).toFixed(2)}</td>
        <td style="padding:4px 0;font-size:11px;text-align:right;font-weight:700;vertical-align:top;">${parseFloat(d.subtotal || 0).toFixed(2)}</td>
      </tr>
    `).join('');

    const totalVal = parseFloat(v.total || 0);
    const subtotalCalc = totalVal / 1.18;
    const igvCalc = totalVal - subtotalCalc;

    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <title>Comprobante ${v.serie}-${v.numero}</title>
        <style>
          @page { size: 80mm auto; margin: 0; }
          body { font-family: 'Courier New', monospace; width: 72mm; margin: 0 auto; padding: 10px 0; color: #000; background: #fff; font-size: 11px; line-height: 1.3; }
          .text-center { text-align: center; }
          .text-right { text-align: right; }
          .bold { font-weight: bold; }
          .logo { font-size: 15px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.5px; }
          .store-info { font-size: 10px; margin-top: 2px; }
          .divider { border-top: 1px dashed #000; margin: 8px 0; }
          .doc-title { font-size: 13px; font-weight: bold; text-transform: uppercase; margin: 4px 0 2px 0; }
          .client-info { font-size: 10px; line-height: 1.4; }
          table { width: 100%; border-collapse: collapse; margin: 4px 0; }
          th { font-size: 10px; border-bottom: 1px solid #000; padding: 3px 0; text-transform: uppercase; }
          .totals { font-size: 11px; line-height: 1.4; }
          .footer-msg { font-size: 9px; margin-top: 12px; text-align: center; font-style: italic; }
        </style>
      </head>
      <body>
        <div class="text-center">
          <div class="logo">Listo! Express</div>
          <div class="store-info">
            Comercializadora Minimarket S.A.C.<br>
            RUC: 20601234567<br>
            ${Utils.escapeHtml(v.mercado_nombre || 'Sucursal Principal')}
          </div>
          <div class="divider"></div>
          <div class="doc-title">${v.tipo_comprobante || 'BOLETA DE VENTA'}</div>
          <div class="bold" style="font-size:14px;">${v.serie}-${String(v.numero).padStart(6, '0')}</div>
        </div>

        <div class="divider"></div>
        <div class="client-info">
          <div><strong>Fecha:</strong> ${Utils.formatDateTime(v.fecha_hora)}</div>
          <div><strong>Cliente:</strong> ${Utils.escapeHtml(v.cliente_nombre || 'Cliente Genérico')}</div>
          <div><strong>DNI/RUC:</strong> ${v.cliente_num_documento || '11111111'}</div>
          <div><strong>Cajero:</strong> ${Utils.escapeHtml(v.usuario_nombre || 'Vendedor')}</div>
        </div>

        <div class="divider"></div>
        <table>
          <thead>
            <tr>
              <th style="width:12%;text-align:center;">Cant</th>
              <th style="text-align:left;width:48%;">Producto</th>
              <th style="text-align:right;width:20%;">P.U.</th>
              <th style="text-align:right;width:20%;">Total</th>
            </tr>
          </thead>
          <tbody>
            ${itemsHtml}
          </tbody>
        </table>

        <div class="divider"></div>
        <div class="totals">
          <div style="display:flex;justify-content:space-between;"><span>OP. GRAVADA:</span> <span>S/ ${subtotalCalc.toFixed(2)}</span></div>
          <div style="display:flex;justify-content:space-between;"><span>IGV (18%):</span> <span>S/ ${igvCalc.toFixed(2)}</span></div>
          <div style="display:flex;justify-content:space-between;font-size:12px;font-weight:bold;margin-top:3px;"><span>TOTAL A PAGAR:</span> <span>S/ ${totalVal.toFixed(2)}</span></div>
          <div style="display:flex;justify-content:space-between;margin-top:3px;"><span>Método de Pago:</span> <span>${v.metodo_pago}</span></div>
          ${v.monto_recibido ? `<div style="display:flex;justify-content:space-between;"><span>Efectivo Recibido:</span> <span>S/ ${parseFloat(v.monto_recibido).toFixed(2)}</span></div>` : ''}
          ${v.vuelto ? `<div style="display:flex;justify-content:space-between;"><span>Vuelto:</span> <span>S/ ${parseFloat(v.vuelto).toFixed(2)}</span></div>` : ''}
        </div>

        <div class="divider"></div>
        <div class="footer-msg">
          ¡Gracias por su preferencia!<br>
          Comprobante Electrónico emitido en Sistema POS
        </div>

        <script>
          window.onload = function() { window.print(); };
        </script>
      </body>
      </html>
    `;

    const win = window.open('', '_blank', 'width=450,height=700');
    win.document.write(html);
    win.document.close();
  }
};

