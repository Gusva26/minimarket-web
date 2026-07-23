const VencimientosPage = {
  currentPage: 1,
  tomSelects: {},

  render: async function (container) {
    container.innerHTML = `
      <div class="page-header" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap">
        <h3><i class="fas fa-calendar-times text-gradient"></i>Control de Vencimientos</h3>
        <button class="btn btn-success btn-sm btn-pill" id="btnExportarVencimientos">
          <i class="fas fa-file-excel"></i>Exportar Excel
        </button>
      </div>

      <div class="kpi-grid" style="grid-template-columns:repeat(3,1fr)" id="vencimientosCards"></div>

      <div class="filters-container" style="margin-top:1.5rem; display: flex; gap: 1rem; align-items: flex-end; flex-wrap: wrap;">
        <div class="filter-group" style="flex: 1; min-width: 250px;">
          <label class="form-label small fw-bold text-muted">Buscar Producto</label>
          <div class="search-box" style="margin-top:0">
            <i class="fas fa-search"></i>
            <input type="text" id="filterVencimientoQ" placeholder="Escriba nombre del producto...">
          </div>
        </div>
        <div class="filter-group" style="width: 220px;">
          <label class="form-label small fw-bold text-muted">Categoría</label>
          <select class="form-select form-select-sm" id="filterVencimientoCategoria">
            <option value="">Todas las Categorías</option>
          </select>
        </div>
        <div class="filter-group" style="width: 220px;">
          <label class="form-label small fw-bold text-muted">Estado de Vencimiento</label>
          <select class="form-select form-select-sm" id="filterVencimientoEstado">
            <option value="">Todos los Estados</option>
            <option value="vencido">Vencidos</option>
            <option value="critico">Críticos (&lt; 7 días)</option>
            <option value="advertencia">Advertencia (7-30 días)</option>
            <option value="seguro">Seguros (&gt; 30 días)</option>
          </select>
        </div>
      </div>

      <div class="table-container" style="margin-top:1.5rem">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Producto</th>
                <th>Categoría</th>
                <th class="text-center">Cantidad</th>
                <th>Fecha Vencimiento</th>
                <th class="text-center">Días Restantes</th>
                <th class="text-center">Estado</th>
              </tr>
            </thead>
            <tbody id="tbodyVencimientos">
              <tr><td colspan="6" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>
            </tbody>
          </table>
        </div>
        <div id="paginationVencimientos" class="d-flex justify-content-center mt-3"></div>
      </div>
    `;
    this.currentPage = 1;

    await this.cargarFiltros();
    await this.cargarVencimientos();
    this.setupListeners();
  },

  cargarFiltros: async function () {
    try {
      const sel = document.getElementById('filterVencimientoCategoria');
      if (!sel) return;
      const cats = await API.get('categorias/');
      const list = cats.results || cats || [];
      sel.innerHTML = '<option value="">Todas las Categorías</option>' +
        list.map(c => `<option value="${c.id}">${Utils.escapeHtml(c.nombre)}</option>`).join('');
    } catch (e) { console.error('Error cargando categorías', e); }
  },

  setupListeners: function() {
    const q = document.getElementById('filterVencimientoQ');
    if (q) q.addEventListener('input', () => this.cargarVencimientos(1));

    const filterCat = document.getElementById('filterVencimientoCategoria');
    if (filterCat) filterCat.addEventListener('change', () => this.cargarVencimientos(1));

    const filterEst = document.getElementById('filterVencimientoEstado');
    if (filterEst) filterEst.addEventListener('change', () => this.cargarVencimientos(1));

    const btnExportar = document.getElementById('btnExportarVencimientos');
    if (btnExportar) btnExportar.addEventListener('click', () => this.exportarExcel());
  },

  cargarVencimientos: async function (page = 1) {
    if (!this._debouncedCargar) {
      this._debouncedCargar = Utils.debounce(async (p) => {
        await this._doCargarVencimientos(p);
      }, 100);
    }
    this._debouncedCargar(page);
  },

  _doCargarVencimientos: async function (page = 1) {
    this.currentPage = page;
    const tbody = document.getElementById('tbodyVencimientos');
    if (!tbody) return; // Guard for async timing
    
    tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>';

    const q = document.getElementById('filterVencimientoQ')?.value || '';
    const cat = document.getElementById('filterVencimientoCategoria')?.value || '';
    const est = document.getElementById('filterVencimientoEstado')?.value || '';


    try {
      const data = await API.get(`inventario/vencimientos/?page=${page}&q=${q}&categoria=${cat}&estado=${est}`);
      const unidades = data.unidades || [];
      const resumen = data.resumen || { criticos: 0, advertencia: 0, total: 0 };
      const pagination = data.pagination;

      this.renderCards(resumen);
      this.renderUnidades(unidades);
      
      if (pagination) {
        Utils.renderPagination(pagination, 'paginationVencimientos', this.currentPage, (p) => {
          this._doCargarVencimientos(p);
        });
      }

    } catch (e) {
      if (tbody) tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4" style="color:var(--danger)">Error: ${e.message}</td></tr>`;
    }
  },

  renderCards: function (resumen) {
    const cards = document.getElementById('vencimientosCards');
    if (!cards) return;
    cards.innerHTML = `
      <div class="kpi-card kpi-danger">
        <div class="kpi-icon"><i class="fas fa-exclamation-circle"></i></div>
        <div class="kpi-label">Lotes Críticos</div>
        <div class="kpi-value">${resumen.criticos}</div>
        <div style="font-size:.75rem;color:var(--danger)">Vencen en menos de 7 días</div>
      </div>
      <div class="kpi-card kpi-warning">
        <div class="kpi-icon"><i class="fas fa-hourglass-half"></i></div>
        <div class="kpi-label">Lotes Advertencia</div>
        <div class="kpi-value">${resumen.advertencia}</div>
        <div style="font-size:.75rem;color:var(--warning)">Vencen en 7 - 30 días</div>
      </div>
      <div class="kpi-card kpi-info">
        <div class="kpi-icon"><i class="fas fa-boxes"></i></div>
        <div class="kpi-label">Total Lotes</div>
        <div class="kpi-value">${resumen.total}</div>
        <div style="font-size:.75rem;color:var(--text-muted)">Agrupados por producto/fecha</div>
      </div>
    `;
  },

  renderUnidades: function (unidades) {
    const tbody = document.getElementById('tbodyVencimientos');
    if (!tbody) return;
    
    if (!unidades.length) {
      tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><div class="empty-icon"><i class="fas fa-calendar-times"></i></div><div class="empty-title">No hay unidades que coincidan con los filtros</div></div></td></tr>`;
      return;
    }

    const now = new Date();

    tbody.innerHTML = unidades.map(u => {
      const fv = new Date(u.fecha_vencimiento);
      const diffTime = fv - now;
      const diasRestantes = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

      let badgeClass = '';
      let estadoLabel = '';

      if (diasRestantes < 0) {
        badgeClass = 'badge-danger';
        estadoLabel = 'Vencido';
      } else if (diasRestantes < 7) {
        badgeClass = 'badge-danger';
        estadoLabel = 'Crítico';
      } else if (diasRestantes <= 30) {
        badgeClass = 'badge-warning';
        estadoLabel = 'Advertencia';
      } else {
        badgeClass = 'badge-success';
        estadoLabel = 'Seguro';
      }

      return `
        <tr>
          <td data-label="Producto">
            <div style="font-weight:600">${u.producto?.nombre || '---'}</div>
          </td>
          <td data-label="Categoría"><small style="color:var(--text-muted)">${u.producto?.categoria?.nombre || 'N/A'}</small></td>
          <td data-label="Cantidad" class="text-center"><span style="font-size:1.1rem;font-weight:700">${u.cantidad}</span></td>
          <td data-label="Vencimiento"><span style="font-weight:600">${Utils.formatDate(u.fecha_vencimiento)}</span></td>
          <td data-label="Días" class="text-center">${diasRestantes < 0 ? `<span style="color:var(--danger);font-weight:700">VENCIDO (hace ${Math.abs(diasRestantes)} días)</span>` : diasRestantes < 7 ? `<span style="color:var(--danger);font-weight:700"><i class="fas fa-exclamation-triangle"></i> ${diasRestantes} días</span>` : diasRestantes <= 30 ? `<span style="color:var(--warning);font-weight:600">${diasRestantes} días</span>` : `<span style="color:var(--success);font-weight:500">${diasRestantes} días</span>`}</td>
          <td data-label="Estado" class="text-center"><span class="badge ${badgeClass}">${estadoLabel}</span></td>
        </tr>
      `;
    }).join('');
  },

  exportarExcel: async function () {
    try {
      const q = document.getElementById('filterVencimientoQ')?.value || '';
      const cat = this.tomSelects['categoria']?.getValue() || '';
      const est = this.tomSelects['estado']?.getValue() || '';

      const data = await API.get(`inventario/vencimientos/?page_size=10000&q=${q}&categoria=${cat}&estado=${est}`);
      const unidades = data.unidades || [];

      if (!unidades.length) {
        Utils.showToast('No hay datos para exportar', 'warning');
        return;
      }

      const now = new Date();
      const rows = unidades.map(u => {
        const fv = new Date(u.fecha_vencimiento);
        const diffTime = fv - now;
        const diasRestantes = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        let estado = 'Seguro';
        if (diasRestantes < 0) estado = 'Vencido';
        else if (diasRestantes < 7) estado = 'Crítico';
        else if (diasRestantes <= 30) estado = 'Advertencia';

        return {
          'Producto': u.producto?.nombre || '---',
          'Categoría': u.producto?.categoria?.nombre || 'N/A',
          'Cantidad': u.cantidad,
          'Fecha Vencimiento': Utils.formatDate(u.fecha_vencimiento),
          'Días Restantes': diasRestantes,
          'Estado': estado
        };
      });

      const ws = XLSX.utils.json_to_sheet(rows);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Vencimientos');

      const today = new Date().toISOString().slice(0, 10);
      XLSX.writeFile(wb, `vencimientos_${today}.xlsx`);

      Utils.showToast('Excel exportado correctamente', 'success');
    } catch (e) {
      console.error('Error exportando Excel:', e);
      Utils.showToast('Error al exportar Excel', 'error');
    }
  }
};
