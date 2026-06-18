const CajasPage = {
  render: async function(container) {
    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-cash-register text-gradient"></i>Gestión de Cajas</h3>
        <div class="page-actions">
          <button class="btn btn-primary btn-sm btn-pill" id="btnAbrirCaja"><i class="fas fa-plus"></i>Abrir Caja</button>
        </div>
      </div>

      <div class="table-container">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Fecha Apertura</th>
                <th>Fecha Cierre</th>
                <th>Monto Inicial</th>
                <th class="text-center">Estado</th>
                <th class="text-center" style="width:120px">Acciones</th>
              </tr>
            </thead>
            <tbody id="cajasTableBody">
              <tr><td colspan="6" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>
            </tbody>
          </table>
        </div>
        <div id="cajasPagination" class="py-3"></div>
      </div>

      ${this.modalAperturaHTML()}
      ${this.modalCierreHTML()}
    `;
    this.bindEvents();
    await this.cargarCajas(1);
  },

  modalAperturaHTML: function() {
    return `
    <div class="modal-overlay" id="aperturaModal">
      <div class="modal-card" style="max-width:420px">
        <div class="modal-card-header">
          <h5><i class="fas fa-cash-register me-2"></i>Abrir Caja</h5>
          <button class="modal-close" onclick="Utils.hideModal('aperturaModal')"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-card-body">
          <div class="form-group">
            <label class="form-label">Monto Inicial (S/)</label>
            <input type="number" step="0.01" class="form-control" id="monto_inicial" placeholder="Ej: 200.00" value="0">
          </div>
        </div>
        <div class="modal-card-footer">
          <button class="btn btn-ghost" onclick="Utils.hideModal('aperturaModal')">Cancelar</button>
          <button class="btn btn-primary" id="btnConfirmarApertura">Abrir Caja</button>
        </div>
      </div>
    </div>`;
  },

  modalCierreHTML: function() {
    return `
    <div class="modal-overlay" id="cierreModal">
      <div class="modal-card" style="max-width:520px">
        <div class="modal-card-header">
          <h5><i class="fas fa-lock me-2"></i>Cerrar Caja</h5>
          <button class="modal-close" onclick="Utils.hideModal('cierreModal')"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-card-body">
          <div id="cierreEsperados" class="mb-3"></div>
          <hr>
          <h6 style="font-weight:600;margin-bottom:12px">Montos Reales</h6>
          <div class="form-group">
            <label class="form-label">Efectivo Real (S/)</label>
            <input type="number" step="0.01" class="form-control" id="cierre_efectivo_real" placeholder="Ej: 1250.50">
          </div>
          <div class="form-group">
            <label class="form-label">Yape Real (S/)</label>
            <input type="number" step="0.01" class="form-control" id="cierre_yape_real" placeholder="Ej: 320.00">
          </div>
          <div class="form-group">
            <label class="form-label">Plin Real (S/)</label>
            <input type="number" step="0.01" class="form-control" id="cierre_plin_real" placeholder="Ej: 150.00">
          </div>
          <div class="form-group">
            <label class="form-label">Observaciones</label>
            <textarea class="form-control" id="cierre_observaciones" placeholder="Ej: Faltaron S/ 5.00 en efectivo, se descontará al cajero" style="min-height:80px"></textarea>
          </div>
        </div>
        <div class="modal-card-footer">
          <button class="btn btn-ghost" onclick="Utils.hideModal('cierreModal')">Cancelar</button>
          <button class="btn btn-warning" id="btnConfirmarCierre">Cerrar Caja</button>
        </div>
      </div>
    </div>`;
  },

  bindEvents: function() {
    const btnAbrirCaja = document.getElementById('btnAbrirCaja');
    if (btnAbrirCaja) btnAbrirCaja.addEventListener('click', () => { Utils.showModal('aperturaModal'); });
    const btnConfirmarApertura = document.getElementById('btnConfirmarApertura');
    if (btnConfirmarApertura) btnConfirmarApertura.addEventListener('click', () => this.abrirCaja());
    const btnConfirmarCierre = document.getElementById('btnConfirmarCierre');
    if (btnConfirmarCierre) btnConfirmarCierre.addEventListener('click', () => this.cerrarCaja());
  },

  cargarCajas: async function(page = 1) {
    const tbody = document.getElementById('cajasTableBody');
    try {
      const data = await API.get(`cajas/?page=${page}`);
      this.renderTabla(data.results || []);
      Utils.renderPagination(data, 'cajasPagination', page, (p) => this.cargarCajas(p));
      const abiertas = (data.results || []).filter(c => c.estado === 'ABIERTA');
      const user = Auth.getUser();
      const tieneAbierta = abiertas.some(c => c.usuario && c.usuario.id === user.id);
      const btnAbrir = document.getElementById('btnAbrirCaja');
      if (btnAbrir) btnAbrir.style.display = tieneAbierta ? 'none' : '';
    } catch (e) {
      if (tbody) tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4" style="color:var(--danger)">Error: ${e.message}</td></tr>`;
    }
  },

  renderTabla: function(cajas) {
    const tbody = document.getElementById('cajasTableBody');
    if (!cajas || cajas.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><div class="empty-icon"><i class="fas fa-cash-register"></i></div><div class="empty-title">No hay registros de cajas</div></div></td></tr>`;
      return;
    }
    let html = '';
    cajas.forEach(c => {
      const badge = c.estado === 'ABIERTA'
        ? '<span class="badge badge-success"><i class="fas fa-check"></i>Abierta</span>'
        : '<span class="badge"><i class="fas fa-times"></i>Cerrada</span>';
      const user = Auth.getUser();
      const puedeCerrar = c.estado === 'ABIERTA' && c.usuario && c.usuario.id === user.id;
      html += `
      <tr>
        <td data-label="Usuario" style="font-weight:500">${c.usuario ? (c.usuario.first_name || c.usuario.username) : '-'}</td>
        <td data-label="Apertura">${Utils.formatDateTime(c.fecha_apertura)}</td>
        <td data-label="Cierre">${c.fecha_cierre ? Utils.formatDateTime(c.fecha_cierre) : '-'}</td>
        <td data-label="Monto Inicial">${Utils.formatMoney(c.monto_inicial)}</td>
        <td data-label="Estado" class="text-center">${badge}</td>
        <td data-label="Acciones" class="text-center">
          <div style="display:flex;gap:4px;justify-content:center">
            <button class="btn btn-sm btn-icon btn-ghost btn-ver-caja" data-id="${c.id}" title="Ver Detalle" style="color:var(--accent)"><i class="fas fa-eye"></i></button>
            ${puedeCerrar ? `<button class="btn btn-sm btn-icon btn-ghost btn-cerrar-caja" data-id="${c.id}" title="Cerrar Caja" style="color:var(--warning)"><i class="fas fa-lock"></i></button>` : ''}
          </div>
        </td>
      </tr>`;
    });
    tbody.innerHTML = html;

    tbody.querySelectorAll('.btn-ver-caja').forEach(btn => {
      btn.addEventListener('click', async () => {
        await this.mostrarDetalle(btn.dataset.id);
      });
    });
    tbody.querySelectorAll('.btn-cerrar-caja').forEach(btn => {
      btn.addEventListener('click', async () => {
        await this.mostrarCierre(btn.dataset.id);
      });
    });
  },

  abrirCaja: async function() {
    const monto_inicial = parseFloat(document.getElementById('monto_inicial').value) || 0;
    if (monto_inicial < 0) { Utils.showToast('El monto inicial no puede ser negativo', 'warning'); return; }
    try {
      await API.post('cajas/apertura/', { monto_inicial });
      Utils.showToast('Caja abierta correctamente', 'success');
      Utils.hideModal('aperturaModal');
      window.location.hash = '#/ventas';
    } catch (e) {
      Utils.showToast('Error al abrir caja: ' + e.message, 'danger');
    }
  },

  mostrarCierre: async function(id) {
    try {
      const caja = await API.get(`cajas/${id}/`);
      document.getElementById('btnConfirmarCierre').dataset.id = id;

      const esperados = caja.montos_esperados || caja;
      const html = `
        <h6 style="font-weight:600;margin-bottom:8px">Montos Esperados</h6>
        <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span>Efectivo:</span><span style="font-weight:600">${Utils.formatMoney(esperados.total_efectivo || 0)}</span></div>
        <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span>Yape:</span><span style="font-weight:600">${Utils.formatMoney(esperados.total_yape || 0)}</span></div>
        <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span>Plin:</span><span style="font-weight:600">${Utils.formatMoney(esperados.total_plin || 0)}</span></div>
        <div style="display:flex;justify-content:space-between;font-weight:700;border-top:1px solid var(--border);padding-top:8px;margin-top:4px"><span>Total Esperado:</span><span>${Utils.formatMoney(esperados.total_general || 0)}</span></div>
      `;
      document.getElementById('cierreEsperados').innerHTML = html;
      document.getElementById('cierre_efectivo_real').value = esperados.total_efectivo || 0;
      document.getElementById('cierre_yape_real').value = esperados.total_yape || 0;
      document.getElementById('cierre_plin_real').value = esperados.total_plin || 0;
      document.getElementById('cierre_observaciones').value = '';

      Utils.showModal('cierreModal');
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'danger');
    }
  },

  cerrarCaja: async function() {
    const id = document.getElementById('btnConfirmarCierre').dataset.id;
    const efectivo = parseFloat(document.getElementById('cierre_efectivo_real').value) || 0;
    const yape = parseFloat(document.getElementById('cierre_yape_real').value) || 0;
    const plin = parseFloat(document.getElementById('cierre_plin_real').value) || 0;

    if (efectivo < 0) { Utils.showToast('El monto de efectivo no puede ser negativo', 'warning'); return; }
    if (yape < 0) { Utils.showToast('El monto de Yape no puede ser negativo', 'warning'); return; }
    if (plin < 0) { Utils.showToast('El monto de Plin no puede ser negativo', 'warning'); return; }

    const data = {
      efectivo_real: efectivo,
      yape_real: yape,
      plin_real: plin,
      observaciones: document.getElementById('cierre_observaciones').value
    };
    try {
      await API.post(`cajas/${id}/cierre/`, data);
      Utils.showToast('Caja cerrada correctamente', 'success');
      Utils.hideModal('cierreModal');
      this.cargarCajas();
    } catch (e) {
      Utils.showToast('Error al cerrar caja: ' + e.message, 'danger');
    }
  },

  mostrarDetalle: async function(id) {
    const loading = Utils.showLoading();
    try {
      const caja = await API.get(`cajas/${id}/`);
      Swal.fire({
        title: 'Detalle de Caja',
        html: this.detalleHTML(caja),
        width: '600px',
        showCloseButton: true,
        showConfirmButton: false,
        background: 'var(--surface)',
        color: 'var(--text)',
      });
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'danger');
    } finally {
      loading.close();
    }
  },

  detalleHTML: function(caja) {
    const esperados = caja.montos_esperados || {};
    const reales = caja.montos_reales || {};
    const difEfectivo = (reales.efectivo_real || 0) - (esperados.total_efectivo || 0);
    const difYape = (reales.yape_real || 0) - (esperados.total_yape || 0);
    const difPlin = (reales.plin_real || 0) - (esperados.total_plin || 0);
    const cuadra = difEfectivo === 0 && difYape === 0 && difPlin === 0;

    const diffClass = (val) => val === 0 ? 'text-success' : (val < 0 ? 'text-danger' : 'text-warning');

    return `
    <div style="text-align:left">
      <div style="display:flex;justify-content:space-between;margin-bottom:8px"><span style="font-weight:600">Usuario:</span><span>${caja.usuario ? (caja.usuario.first_name || caja.usuario.username) : '-'}</span></div>
      <div style="display:flex;justify-content:space-between;margin-bottom:8px"><span style="font-weight:600">Apertura:</span><span>${Utils.formatDateTime(caja.fecha_apertura)}</span></div>
      <div style="display:flex;justify-content:space-between;margin-bottom:8px"><span style="font-weight:600">Cierre:</span><span>${caja.fecha_cierre ? Utils.formatDateTime(caja.fecha_cierre) : '-'}</span></div>
      <div style="display:flex;justify-content:space-between;margin-bottom:8px"><span style="font-weight:600">Monto Inicial:</span><span>${Utils.formatMoney(caja.monto_inicial)}</span></div>
      <hr>
      <h6 style="font-weight:700;color:${cuadra ? 'var(--success)' : 'var(--danger)'}">${cuadra ? '✓ CUADRA' : '✗ DESCUADRE'}</h6>
      <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span>Efectivo Esperado:</span><span>${Utils.formatMoney(esperados.total_efectivo || 0)}</span></div>
      <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span>Efectivo Real:</span><span>${Utils.formatMoney(reales.efectivo_real || 0)}</span></div>
      <div style="display:flex;justify-content:space-between;margin-bottom:4px;color:${diffClass(difEfectivo)}"><span>Diferencia:</span><span>${Utils.formatMoney(difEfectivo)}</span></div>
      <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span>Yape Esperado:</span><span>${Utils.formatMoney(esperados.total_yape || 0)}</span></div>
      <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span>Yape Real:</span><span>${Utils.formatMoney(reales.yape_real || 0)}</span></div>
      <div style="display:flex;justify-content:space-between;margin-bottom:4px;color:${diffClass(difYape)}"><span>Diferencia:</span><span>${Utils.formatMoney(difYape)}</span></div>
      <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span>Plin Esperado:</span><span>${Utils.formatMoney(esperados.total_plin || 0)}</span></div>
      <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span>Plin Real:</span><span>${Utils.formatMoney(reales.plin_real || 0)}</span></div>
      <div style="display:flex;justify-content:space-between;margin-bottom:4px;color:${diffClass(difPlin)}"><span>Diferencia:</span><span>${Utils.formatMoney(difPlin)}</span></div>
      ${caja.observaciones ? `<hr><div style="font-weight:600">Observaciones:</div><p>${caja.observaciones}</p>` : ''}
      <hr>
      <button class="btn btn-primary w-100" onclick="window.print()"><i class="fas fa-print me-2"></i>Imprimir</button>
    </div>`;
  }
};
