const HistorialPage = {
  currentPage: 1,
  filtros: {},

  render: async function(container) {
    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-history text-gradient"></i>Historial de Ventas</h3>
        <p style="color:var(--text-muted);font-size:.85rem;margin:0">Gestiona, filtra y anula ventas del sistema.</p>
      </div>

      <div class="filters-bar">
        <div class="filter-group">
          <label>Desde</label>
          <input type="date" id="filtro_fecha_inicio" class="form-control form-control-sm">
        </div>
        <div class="filter-group">
          <label>Hasta</label>
          <input type="date" id="filtro_fecha_fin" class="form-control form-control-sm">
        </div>
        <div class="filter-group">
          <label>Método</label>
          <select id="filtro_metodo_pago" class="form-select form-select-sm">
            <option value="">Todos</option>
            <option value="Efectivo">Efectivo</option>
            <option value="Yape">Yape</option>
            <option value="Plin">Plin</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Tipo</label>
          <select id="filtro_tipo_comprobante" class="form-select form-select-sm">
            <option value="">Todos</option>
            <option value="TICKET">Ticket</option>
            <option value="BOLETA">Boleta</option>
            <option value="FACTURA">Factura</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Estado</label>
          <select id="filtro_estado" class="form-select form-select-sm">
            <option value="">Todos</option>
            <option value="COMPLETADA">Completada</option>
            <option value="ANULADA">Anulada</option>
          </select>
        </div>
        <div class="filter-group" style="flex:1;min-width:150px">
          <label>Buscar</label>
          <input type="text" id="filtro_q" class="form-control form-control-sm" placeholder="ID, producto o N° Operación">
        </div>
        <div class="filter-group" style="align-self:flex-end">
          <button class="btn btn-ghost btn-sm" id="btnLimpiarFiltros"><i class="fas fa-undo"></i>Limpiar</button>
        </div>
      </div>

      <div class="table-container" style="margin-top:1rem">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Comprobante</th>
                <th>Fecha y Hora</th>
                <th>Cliente</th>
                <th class="text-center">Método</th>
                <th class="text-center">Estado</th>
                <th class="text-center">Total</th>
                <th class="text-center" style="width:120px">Acciones</th>
              </tr>
            </thead>
            <tbody id="historialTableBody">
              <tr><td colspan="7" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>
            </tbody>
          </table>
        </div>
        <div id="historialPagination" class="py-3"></div>
      </div>`;
    this.bindEvents();
    await this.cargarVentas();
  },

  bindEvents: function() {
    const filterIds = [
      'filtro_fecha_inicio', 'filtro_fecha_fin', 'filtro_metodo_pago',
      'filtro_tipo_comprobante', 'filtro_estado'
    ];
    filterIds.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('change', () => {
        this.currentPage = 1;
        this.cargarVentas();
      });
    });

    const searchInput = document.getElementById('filtro_q');
    const debouncedSearch = Utils.debounce(() => {
      this.currentPage = 1;
      this.cargarVentas();
    }, 400);

    if (searchInput) searchInput.addEventListener('input', debouncedSearch);

    const btnLimpiarFiltros = document.getElementById('btnLimpiarFiltros');
    if (btnLimpiarFiltros) {
      btnLimpiarFiltros.addEventListener('click', () => {
      document.getElementById('filtro_fecha_inicio').value = '';
      document.getElementById('filtro_fecha_fin').value = '';
      document.getElementById('filtro_metodo_pago').value = '';
      document.getElementById('filtro_tipo_comprobante').value = '';
      document.getElementById('filtro_estado').value = '';
      document.getElementById('filtro_q').value = '';
      this.currentPage = 1;
      this.cargarVentas();
    });
    }
  },

  cargarVentas: async function(page = 1) {
    if (!this._debouncedCargar) {
      this._debouncedCargar = Utils.debounce(async (p) => {
        await this._doCargarVentas(p);
      }, 100);
    }
    this._debouncedCargar(page);
  },

  _doCargarVentas: async function(page) {
    this.currentPage = page;
    const fecha_inicio = document.getElementById('filtro_fecha_inicio')?.value || '';
    const fecha_fin = document.getElementById('filtro_fecha_fin')?.value || '';
    const metodo_pago = document.getElementById('filtro_metodo_pago')?.value || '';
    const tipo_comprobante = document.getElementById('filtro_tipo_comprobante')?.value || '';
    const estado = document.getElementById('filtro_estado')?.value || '';
    const q = document.getElementById('filtro_q')?.value || '';

    let params = `?page=${this.currentPage}`;
    if (fecha_inicio) params += `&fecha_inicio=${fecha_inicio}`;
    if (fecha_fin) params += `&fecha_fin=${fecha_fin}`;
    if (metodo_pago) params += `&metodo_pago=${metodo_pago}`;
    if (tipo_comprobante) params += `&tipo_comprobante=${tipo_comprobante}`;
    if (estado) params += `&estado=${estado}`;
    if (q) params += `&q=${encodeURIComponent(q)}`;

    const tbody = document.getElementById('historialTableBody');
    if (!tbody) return;
    try {
      const data = await API.get('ventas/' + params);
      this.renderTabla(data.results || []);
      Utils.renderPagination(data, 'historialPagination', this.currentPage, (p) => this.cargarVentas(p));
    } catch (e) {
      if (tbody) tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4" style="color:var(--danger)">Error: ${e.message}</td></tr>`;
    }
  },

  renderTabla: function(ventas) {
    const tbody = document.getElementById('historialTableBody');
    if (!ventas || ventas.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><div class="empty-icon"><i class="fas fa-search"></i></div><div class="empty-title">No se encontraron ventas</div></div></td></tr>`;
      return;
    }
    let html = '';
    ventas.forEach(v => {
      const estadoBadge = v.estado === 'COMPLETADA'
        ? '<span class="badge badge-success"><i class="fas fa-check"></i>Completada</span>'
        : '<span class="badge badge-danger"><i class="fas fa-times"></i>Anulada</span>';

      const metodoBadge = v.metodo_pago === 'Efectivo'
        ? '<span class="badge badge-success">Efectivo</span>'
        : v.metodo_pago === 'Yape'
        ? '<span class="badge badge-yape">Yape</span>'
        : '<span class="badge badge-plin">Plin</span>';

      const clienteText = v.cliente 
        ? `${Utils.escapeHtml(v.cliente.nombre)}<br><small style="color:var(--text-muted)">${Utils.escapeHtml(v.cliente.num_documento || '')}</small>` 
        : '<span style="color:var(--text-muted);font-style:italic">Cliente Genérico</span>';

      const hoy = new Date().toISOString().split('T')[0];
      const fechaVenta = new Date(v.fecha_hora).toISOString().split('T')[0];
      const puedeAnular = v.estado === 'COMPLETADA' && fechaVenta === hoy;

      const comprobanteNumStr = `${v.serie || ''}-${String(v.numero || '').padStart(6, '0')}`;

      html += `
      <tr${v.estado === 'ANULADA' ? ' style="opacity:.6"' : ''}>
        <td data-label="Comprobante">
          <div style="font-weight:600">${Utils.escapeHtml(v.tipo_comprobante)}</div>
          <small style="color:var(--accent);font-weight:500">${Utils.escapeHtml(comprobanteNumStr)}</small>
          ${v.num_operacion ? `<br><span class="badge" style="font-size:.65rem;background:var(--surface-hover);color:var(--text)">OP: ${Utils.escapeHtml(v.num_operacion)}</span>` : ''}
        </td>
        <td data-label="Fecha" style="font-size:.85rem">
          ${Utils.formatDate(v.fecha_hora)}<br>
          <span style="color:var(--text-muted)">${new Date(v.fecha_hora).toLocaleTimeString('es-PE', {hour:'2-digit',minute:'2-digit'})}</span>
        </td>
        <td data-label="Cliente" style="font-size:.85rem">${clienteText}</td>
        <td data-label="Método" class="text-center">${metodoBadge}</td>
        <td data-label="Estado" class="text-center">${estadoBadge}</td>
        <td data-label="Total" class="text-center fw-bold">${Utils.formatMoney(v.total)}</td>
        <td data-label="Acciones" class="text-center">
          <div style="display:flex;gap:4px;justify-content:center">
            <button class="btn btn-sm btn-icon btn-ghost btn-ver-venta" data-id="${v.id}" title="Ver Detalle" style="color:var(--accent)"><i class="fas fa-eye"></i></button>
            ${puedeAnular ? `<button class="btn btn-sm btn-icon btn-ghost btn-anular-venta" data-id="${v.id}" data-numero="${Utils.escapeHtml(comprobanteNumStr)}" title="Anular Venta" style="color:var(--danger)"><i class="fas fa-ban"></i></button>` : ''}
          </div>
        </td>
      </tr>`;
    });
    tbody.innerHTML = html;

    tbody.querySelectorAll('.btn-ver-venta').forEach(btn => {
      btn.addEventListener('click', () => window.location.hash = `#/ventas-detalle/${btn.dataset.id}`);
    });
    tbody.querySelectorAll('.btn-anular-venta').forEach(btn => {
      btn.addEventListener('click', async () => {
        const result = await Utils.showConfirm('¿Anular venta?', `¿Está seguro de ANULAR la venta ${btn.dataset.numero}? Esta acción devolverá el stock al inventario.`, 'Sí, anular');
        if (result.isConfirmed) {
          await this.anularVenta(btn.dataset.id);
        }
      });
    });
  },

  anularVenta: async function(id) {
    try {
      await API.post(`ventas/${id}/anular/`);
      Utils.showToast('Venta anulada correctamente', 'success');
      this.cargarVentas();
    } catch (e) {
      Utils.showToast('Error al anular venta: ' + e.message, 'danger');
    }
  }
};
