const KardexPage = {
  currentPage: 1,
  filtros: { producto: '', fecha_desde: '', fecha_hasta: '' },
  _productos: [],

  render: async function (container) {
    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-book text-gradient"></i>Kardex</h3>
        <div class="page-actions">
          <button class="btn btn-success btn-sm btn-pill" id="btnExportExcel"><i class="fas fa-file-excel"></i>Exportar Excel</button>
        </div>
      </div>

      <div class="filters-bar">
        <div class="filter-group" style="flex:1;min-width:200px">
          <label>Producto</label>
          <div class="search-box" style="margin-top:0">
            <i class="fas fa-search"></i>
            <input type="text" id="filtroProducto" placeholder="Escriba nombre del producto..." autocomplete="off" list="productoList">
            <datalist id="productoList"></datalist>
          </div>
        </div>
        <div class="filter-group">
          <label>Desde</label>
          <input type="date" class="form-control" id="filtroFechaDesde">
        </div>
        <div class="filter-group">
          <label>Hasta</label>
          <input type="date" class="form-control" id="filtroFechaHasta">
        </div>
        <div class="filter-group" style="align-self:flex-end">
          <button class="btn btn-ghost" id="btnLimpiar"><i class="fas fa-undo"></i>Limpiar</button>
        </div>
      </div>

      <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin-top:1rem" id="resumenCards"></div>

      <div class="table-container" style="margin-top:1rem">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Producto</th>
                <th>Tipo</th>
                <th class="text-end">Cantidad</th>
                <th class="text-end">Saldo Anterior</th>
                <th class="text-end">Saldo Nuevo</th>
                <th>Usuario</th>
                <th class="text-end">Documento / Origen del Movimiento</th>
              </tr>
            </thead>
            <tbody id="tbodyKardex">
              <tr><td colspan="8" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>
            </tbody>
          </table>
        </div>
      </div>
      <div id="paginationKardex" class="d-flex justify-content-center mt-3"></div>
    `;

    this.bindEvents();
    await this.cargarProductos();
    await this.cargarKardex();
  },


  bindEvents: function () {
    const inputProducto = document.getElementById('filtroProducto');
    const inputFechaDesde = document.getElementById('filtroFechaDesde');
    const inputFechaHasta = document.getElementById('filtroFechaHasta');
    const btnLimpiar = document.getElementById('btnLimpiar');

    const doFilter = () => {
      const nombreBuscado = inputProducto ? inputProducto.value.trim() : '';
      const prod = this._productos.find(p => p.nombre.toLowerCase() === nombreBuscado.toLowerCase());
      this.filtros.producto = prod ? prod.id : '';
      this.filtros.fecha_desde = inputFechaDesde ? inputFechaDesde.value : '';
      this.filtros.fecha_hasta = inputFechaHasta ? inputFechaHasta.value : '';
      this.currentPage = 1;
      this.cargarKardex();
    };

    if (inputFechaDesde) inputFechaDesde.addEventListener('change', doFilter);
    if (inputFechaHasta) inputFechaHasta.addEventListener('change', doFilter);

    if (inputProducto) {
      let searchTimer;
      inputProducto.addEventListener('input', () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(doFilter, 300);
      });
    }

    if (btnLimpiar) {
      btnLimpiar.addEventListener('click', () => {
        if (inputProducto) inputProducto.value = '';
        if (inputFechaDesde) inputFechaDesde.value = '';
        if (inputFechaHasta) inputFechaHasta.value = '';
        this.filtros = { producto: '', fecha_desde: '', fecha_hasta: '' };
        this.currentPage = 1;
        this.cargarKardex();
      });
    }

    const btnExportExcel = document.getElementById('btnExportExcel');
    if (btnExportExcel) btnExportExcel.addEventListener('click', () => this.exportarExcel());
  },

  cargarProductos: async function () {
    try {
      const data = await API.get('productos/?page_size=1000');
      const datalist = document.getElementById('productoList');
      if (!datalist) return;
      this._productos = data.results || data || [];
      datalist.innerHTML = '';
      this._productos.forEach(p => {
        datalist.innerHTML += `<option value="${p.nombre}">`;
      });
    } catch (e) {
      console.error('Error cargando productos', e);
    }
  },

  cargarKardex: async function (page) {
    if (!this._debouncedCargar) {
      this._debouncedCargar = Utils.debounce(async (p) => {
        await this._doCargarKardex(p);
      }, 100);
    }
    this._debouncedCargar(page || this.currentPage);
  },

  _doCargarKardex: async function (p) {
    const tbody = document.getElementById('tbodyKardex');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>';

    try {
      let url = `kardex/?page=${p}`;
      if (this.filtros.producto) url += `&producto=${this.filtros.producto}`;
      if (this.filtros.fecha_desde) url += `&fecha_desde=${this.filtros.fecha_desde}`;
      if (this.filtros.fecha_hasta) url += `&fecha_hasta=${this.filtros.fecha_hasta}`;

      const data = await API.get(url);
      const movimientos = data.results || [];
      this.renderMovimientos(movimientos);

      const resumen = data.resumen || {};
      this.renderResumen(resumen, data);

      Utils.renderPagination(data, 'paginationKardex', p, (page) => {
        this.currentPage = page;
        this.cargarKardex(page);
      });
    } catch (e) {
      if (tbody) tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4" style="color:var(--danger)">Error: ${e.message}</td></tr>`;
    }
  },

  renderResumen: function (resumen, data) {
    const container = document.getElementById('resumenCards');
    container.innerHTML = `
      <div class="kpi-card kpi-primary">
        <div class="kpi-icon"><i class="fas fa-list"></i></div>
        <div class="kpi-label">Total Movimientos</div>
        <div class="kpi-value">${data.count ?? 0}</div>
      </div>
      <div class="kpi-card kpi-success">
        <div class="kpi-icon"><i class="fas fa-plus-circle"></i></div>
        <div class="kpi-label">Entradas</div>
        <div class="kpi-value">${resumen.entradas ?? 0}</div>
      </div>
      <div class="kpi-card kpi-danger">
        <div class="kpi-icon"><i class="fas fa-minus-circle"></i></div>
        <div class="kpi-label">Salidas</div>
        <div class="kpi-value">${resumen.salidas ?? 0}</div>
      </div>
      <div class="kpi-card kpi-info">
        <div class="kpi-icon"><i class="fas fa-adjust"></i></div>
        <div class="kpi-label">Ajustes</div>
        <div class="kpi-value">${resumen.ajustes ?? 0}</div>
      </div>
    `;
  },

  renderReferencia: function (m) {
    const refTipo = (m.referencia_tipo || '').toLowerCase();
    const refId = m.referencia_id ? `#${m.referencia_id}` : '';
    let detalle = m.referencia_detalle || '';

    let icon = 'fa-file-alt';
    let badgeStyle = 'background:rgba(100,116,139,0.15); color:#64748b; border:1px solid rgba(100,116,139,0.3);';
    let label = m.referencia_tipo || 'Movimiento';

    if (refTipo.includes('inicial') || refTipo.includes('carga')) {
      icon = 'fa-boxes-stacked';
      badgeStyle = 'background:rgba(71,85,105,0.15); color:#475569; border:1px solid rgba(71,85,105,0.3);';
      label = 'Inventario Inicial';
    } else if (refTipo === 'venta' || refTipo.startsWith('venta') || refTipo.includes('pos')) {
      icon = 'fa-receipt';
      badgeStyle = 'background:rgba(124,58,237,0.15); color:#7c3aed; border:1px solid rgba(124,58,237,0.3);';
      label = 'Venta POS';
    } else if (refTipo.includes('compra')) {
      icon = 'fa-truck';
      badgeStyle = 'background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3);';
      label = 'Compra Proveedor';
    } else if (refTipo.includes('transferencia')) {
      icon = 'fa-right-left';
      badgeStyle = 'background:rgba(2,132,199,0.15); color:#0284c7; border:1px solid rgba(2,132,199,0.3);';
      label = 'Transferencia';
    } else if (refTipo.includes('ajuste') || refTipo.includes('merma')) {
      icon = 'fa-triangle-exclamation';
      badgeStyle = 'background:rgba(245,158,11,0.15); color:#d97706; border:1px solid rgba(245,158,11,0.3);';
      label = 'Ajuste / Merma';
    }

    if (detalle.toLowerCase() === `venta #${m.referencia_id}` || detalle.toLowerCase() === 'venta pos' || detalle.toLowerCase() === 'venta') {
      detalle = '';
    }

    return `
      <div style="line-height:1.4">
        <span class="badge" style="${badgeStyle} font-size:0.8rem; font-weight:700; padding:5px 12px; border-radius:20px; display:inline-block;">
          <i class="fas ${icon} me-1"></i>${label} ${refId}
        </span>
        ${detalle ? `<div style="font-size:0.85rem; font-weight:600; color:var(--text-main, #0f172a); margin-top:4px; opacity:0.9">${Utils.escapeHtml(detalle)}</div>` : ''}
      </div>
    `;
  },

  renderMovimientos: function (movimientos) {
    const tbody = document.getElementById('tbodyKardex');
    if (!movimientos.length) {
      tbody.innerHTML = `<tr><td colspan="8"><div class="empty-state"><div class="empty-icon"><i class="fas fa-book"></i></div><div class="empty-title">No se encontraron movimientos</div><div class="empty-desc">Seleccione filtros o registre movimientos en el inventario</div></div></td></tr>`;
      return;
    }

    const tipoBadge = {
      ENTRADA: '<span class="badge" style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);font-weight:700;padding:5px 12px;border-radius:20px;"><i class="fas fa-plus-circle me-1"></i>Entrada</span>',
      SALIDA: '<span class="badge" style="background:rgba(239,68,68,0.15);color:#ef4444;border:1px solid rgba(239,68,68,0.3);font-weight:700;padding:5px 12px;border-radius:20px;"><i class="fas fa-minus-circle me-1"></i>Salida</span>',
      AJUSTE_POSITIVO: '<span class="badge" style="background:rgba(59,130,246,0.15);color:#3b82f6;border:1px solid rgba(59,130,246,0.3);font-weight:700;padding:5px 12px;border-radius:20px;"><i class="fas fa-plus-square me-1"></i>Ajuste +</span>',
      AJUSTE_NEGATIVO: '<span class="badge" style="background:rgba(245,158,11,0.15);color:#d97706;border:1px solid rgba(245,158,11,0.3);font-weight:700;padding:5px 12px;border-radius:20px;"><i class="fas fa-minus-square me-1"></i>Ajuste -</span>',
      ENTRADA_TRANSFERENCIA: '<span class="badge" style="background:rgba(2,132,199,0.15);color:#0284c7;border:1px solid rgba(2,132,199,0.3);font-weight:700;padding:5px 12px;border-radius:20px;"><i class="fas fa-arrow-down me-1"></i>Entrada Transf.</span>',
      SALIDA_TRANSFERENCIA: '<span class="badge" style="background:rgba(245,158,11,0.15);color:#d97706;border:1px solid rgba(245,158,11,0.3);font-weight:700;padding:5px 12px;border-radius:20px;"><i class="fas fa-arrow-up me-1"></i>Salida Transf.</span>',
    };


    tbody.innerHTML = movimientos.map(m => {
      const saldoCls = m.saldo_nuevo > m.saldo_anterior ? 'kpi-success' : m.saldo_nuevo < m.saldo_anterior ? 'kpi-danger' : '';
      const userDisplayName = m.usuario?.get_full_name || m.usuario?.username || 'N/A';
      return `<tr>
        <td data-label="Fecha" class="align-middle"><small style="color:var(--text-muted); font-size:0.82rem; font-weight:500">${Utils.formatDateTime(m.fecha)}</small></td>
        <td data-label="Producto" class="align-middle">
          <div style="font-weight:700; font-size:0.9rem; color:var(--text-main, #0f172a)">${Utils.escapeHtml(m.producto?.nombre || '---')}</div>
          <small style="color:var(--text-muted); font-size:0.78rem">ID: #${m.producto?.id || ''}</small>
        </td>
        <td data-label="Tipo" class="align-middle">${tipoBadge[m.tipo_movimiento] || `<span class="badge">${Utils.escapeHtml(m.tipo_movimiento)}</span>`}</td>
        <td data-label="Cantidad" class="text-end fw-bold align-middle" style="font-size:0.92rem">${m.cantidad}</td>
        <td data-label="Saldo Anterior" class="text-end align-middle" style="color:var(--text-muted); font-weight:500">${m.saldo_anterior}</td>
        <td data-label="Saldo Nuevo" class="text-end fw-bold align-middle" style="font-size:0.95rem; color:${saldoCls === 'kpi-success' ? 'var(--success)' : saldoCls === 'kpi-danger' ? 'var(--danger)' : 'var(--text)'}">${m.saldo_nuevo}</td>
        <td data-label="Usuario" class="align-middle"><span style="font-size:0.85rem; font-weight:600">${Utils.escapeHtml(userDisplayName)}</span></td>
        <td data-label="Documento / Origen" class="align-middle text-end">${this.renderReferencia(m)}</td>
      </tr>`;
    }).join('');
  },


  exportarExcel: function () {
    const table = document.querySelector('.table-container table');
    if (!table) { Utils.showToast('No hay datos para exportar', 'warning'); return; }
    const wb = XLSX.utils.table_to_book(table, { sheet: 'Kardex' });
    const date = new Date().toISOString().slice(0, 10);
    XLSX.writeFile(wb, `Kardex_Inventario_${date}.xlsx`);
    Utils.showToast('Excel exportado correctamente', 'success');
  }
};
