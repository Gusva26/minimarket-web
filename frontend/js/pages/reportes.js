const ReportesPage = {
  charts: {},

  render: async function(container) {
    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-chart-line text-gradient"></i>Reporte de Ventas</h3>
      </div>

      <div class="filters-bar">
        <div class="filter-group">
          <label>Período</label>
          <div class="btn-group" role="group" id="filtrosRapidos">
            <button class="btn btn-primary btn-sm active" data-filtro="hoy">Hoy</button>
            <button class="btn btn-ghost btn-sm" data-filtro="semana">Semana</button>
            <button class="btn btn-ghost btn-sm" data-filtro="mes">Mes</button>
            <button class="btn btn-ghost btn-sm" data-filtro="personalizado">
              <i class="fas fa-calendar"></i>
            </button>
          </div>
        </div>
        <div class="filter-group d-none" id="fechasPersonalizado">
          <label>Desde</label>
          <input type="date" id="rep_fecha_inicio" class="form-control form-control-sm">
          <label style="margin-top:4px">Hasta</label>
          <input type="date" id="rep_fecha_fin" class="form-control form-control-sm">
        </div>
        <div class="filter-group">
          <label>Método de Pago</label>
          <select id="rep_metodo_pago" class="form-select form-select-sm">
            <option value="">Todos</option>
            <option value="Efectivo">Efectivo</option>
            <option value="Yape">Yape</option>
            <option value="Plin">Plin</option>
          </select>
        </div>
        <div class="filter-group" style="align-self:flex-end">
          <div style="display:flex;gap:6px">
            <button class="btn btn-success btn-sm btn-pill" id="btnExportarExcel"><i class="fas fa-file-excel"></i>Excel</button>
            <button class="btn btn-danger btn-sm btn-pill" id="btnExportarPDF"><i class="fas fa-file-pdf"></i>PDF</button>
          </div>
        </div>
      </div>

      <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin:1rem 0" id="kpiCards"></div>

      <div class="chart-grid">
        <div class="chart-col chart-col-main">
          <div class="card"><div class="card-body" style="padding:0.75rem"><canvas id="chartEvolucion"></canvas></div></div>
        </div>
        <div class="chart-col chart-col-side">
          <div class="card"><div class="card-body" style="padding:0.75rem"><canvas id="chartMetodosPago"></canvas></div></div>
        </div>
      </div>

      <div class="charts-bottom">
        <div class="table-container">
          <div class="table-toolbar">
            <h6 class="toolbar-title"><i class="fas fa-star" style="color:var(--warning)"></i>Top 10 Productos Más Vendidos</h6>
          </div>
          <div id="topProductos" class="p-3"></div>
        </div>
        <div class="table-container">
          <div class="table-toolbar">
            <h6 class="toolbar-title"><i class="fas fa-clock" style="color:var(--danger)"></i>Productos de Baja Rotación</h6>
          </div>
          <div id="bajaRotacion" class="p-3"></div>
        </div>
      </div>`;
    this.bindEvents();
    await this.cargarReporte('hoy');
  },

  bindEvents: function() {
    document.querySelectorAll('#filtrosRapidos .btn').forEach(btn => {
      btn.addEventListener('click', function() {
        document.querySelectorAll('#filtrosRapidos .btn').forEach(b => { b.className = 'btn btn-ghost btn-sm'; });
        this.className = 'btn btn-primary btn-sm active';
        const fechas = document.getElementById('fechasPersonalizado');
        if (this.dataset.filtro === 'personalizado') {
          fechas.classList.remove('d-none');
        } else {
          fechas.classList.add('d-none');
          ReportesPage.cargarReporte(this.dataset.filtro);
        }
      });
    });
    const repFechaInicio = document.getElementById('rep_fecha_inicio');
    if (repFechaInicio) {
      repFechaInicio.addEventListener('change', () => {
        if (document.getElementById('rep_fecha_inicio').value && document.getElementById('rep_fecha_fin').value)
          ReportesPage.cargarReporte('personalizado');
      });
    }
    const repFechaFin = document.getElementById('rep_fecha_fin');
    if (repFechaFin) {
      repFechaFin.addEventListener('change', () => {
        if (document.getElementById('rep_fecha_inicio').value && document.getElementById('rep_fecha_fin').value)
          ReportesPage.cargarReporte('personalizado');
      });
    }
    const repMetodoPago = document.getElementById('rep_metodo_pago');
    if (repMetodoPago) {
      repMetodoPago.addEventListener('change', function() {
        const activo = document.querySelector('#filtrosRapidos .btn.active');
        if (activo) ReportesPage.cargarReporte(activo.dataset.filtro);
      });
    }
    const btnExportarExcel = document.getElementById('btnExportarExcel');
    if (btnExportarExcel) btnExportarExcel.addEventListener('click', () => this.exportar('excel'));
    const btnExportarPDF = document.getElementById('btnExportarPDF');
    if (btnExportarPDF) btnExportarPDF.addEventListener('click', () => this.exportar('pdf'));
  },

  exportar: function(formato) {
    const activo = document.querySelector('#filtrosRapidos .btn.active');
    const filtro = activo ? activo.dataset.filtro : 'hoy';
    let params = `filtro=${filtro}`;
    if (filtro === 'personalizado') {
      params += `&fecha_inicio=${document.getElementById('rep_fecha_inicio').value}`;
      params += `&fecha_fin=${document.getElementById('rep_fecha_fin').value}`;
    }
    const metodo = document.getElementById('rep_metodo_pago').value;
    if (metodo) params += `&metodo_pago=${metodo}`;
    window.open(API.baseURL + `reportes/ventas/${formato}/?${params}`, '_blank');
  },

  cargarReporte: async function(filtro) {
    const loading = Utils.showLoading();
    try {
      let params = `?filtro=${filtro}`;
      if (filtro === 'personalizado') {
        params += `&fecha_inicio=${document.getElementById('rep_fecha_inicio').value}`;
        params += `&fecha_fin=${document.getElementById('rep_fecha_fin').value}`;
      }
      const metodo = document.getElementById('rep_metodo_pago').value;
      if (metodo) params += `&metodo_pago=${metodo}`;

      const data = await API.get('reportes/ventas/' + params);
      this.renderKPIs(data);
      this.renderCharts(data);
      this.renderTopProductos(data.top_productos || []);
      this.renderBajaRotacion(data.baja_rotacion || []);
    } catch (e) {
      Utils.showToast('Error al cargar reporte: ' + e.message, 'danger');
    } finally {
      loading.close();
    }
  },

  renderKPIs: function(data) {
    const container = document.getElementById('kpiCards');
    container.innerHTML = `
      <div class="kpi-card kpi-primary">
        <div class="kpi-icon"><i class="fas fa-coins"></i></div>
        <div class="kpi-label">Ingresos Totales</div>
        <div class="kpi-value">${Utils.formatMoney(data.total_vendido || 0)}</div>
      </div>
      <div class="kpi-card kpi-success">
        <div class="kpi-icon"><i class="fas fa-chart-line"></i></div>
        <div class="kpi-label">Utilidad Bruta</div>
        <div class="kpi-value">${Utils.formatMoney(data.utilidad_total || 0)}</div>
      </div>
      <div class="kpi-card kpi-info">
        <div class="kpi-icon"><i class="fas fa-percentage"></i></div>
        <div class="kpi-label">Margen %</div>
        <div class="kpi-value">${(data.margen_porcentaje || 0).toFixed(2)}%</div>
      </div>
      <div class="kpi-card kpi-warning">
        <div class="kpi-icon"><i class="fas fa-shopping-cart"></i></div>
        <div class="kpi-label">Ventas Realizadas</div>
        <div class="kpi-value">${data.cantidad_ventas || 0}</div>
      </div>`;
  },

  getChartTheme: function() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
      color: isDark ? '#cbd5e1' : '#475569',
      grid: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'
    };
  },

  renderCharts: function(data) {
    if (this.charts.evolucion) this.charts.evolucion.destroy();
    if (this.charts.metodos) this.charts.metodos.destroy();

    const fechas = data.fechas_chart || [];
    const totales = data.totales_chart || [];
    const t = this.getChartTheme();

    const ctx1 = document.getElementById('chartEvolucion');
    if (ctx1) {
      this.charts.evolucion = new Chart(ctx1, {
        type: 'line',
        data: {
          labels: fechas,
          datasets: [{
            label: 'Ventas (S/)',
            data: totales,
            borderColor: '#0ea5e9',
            backgroundColor: 'rgba(14,165,233,0.1)',
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: t.color }, grid: { color: t.grid } },
            y: { beginAtZero: true, ticks: { color: t.color }, grid: { color: t.grid } }
          }
        }
      });
    }

    const metodosLabels = data.metodos_pago_chart || [];
    const metodosData = data.totales_metodos_chart || [];

    const ctx2 = document.getElementById('chartMetodosPago');
    if (ctx2) {
      this.charts.metodos = new Chart(ctx2, {
        type: 'doughnut',
        data: {
          labels: metodosLabels,
          datasets: [{
            data: metodosData,
            backgroundColor: ['#10b981', '#742581', '#00a3d2', '#94a3b8']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { color: t.color } }
          }
        }
      });
    }
  },

  renderTopProductos: function(productos) {
    const container = document.getElementById('topProductos');
    if (!productos || productos.length === 0) {
      container.innerHTML = '<div class="empty-state py-3"><div class="empty-title">No hay datos</div></div>';
      return;
    }
    let html = '<div class="table-responsive"><table class="table" style="font-size:.85rem"><thead><tr><th>#</th><th>Producto</th><th class="text-end">Cantidad</th><th class="text-end">Total</th></tr></thead><tbody>';
    productos.forEach((p, i) => {
      html += `<tr><td>${i + 1}</td><td>${p.producto__nombre || p.nombre || p.producto || ''}</td><td class="text-end">${p.total_cantidad || p.cantidad || 0}</td><td class="text-end">${Utils.formatMoney(p.total_venta || p.total || 0)}</td></tr>`;
    });
    html += '</tbody></table></div>';
    container.innerHTML = html;
  },

  renderBajaRotacion: function(productos) {
    const container = document.getElementById('bajaRotacion');
    if (!productos || productos.length === 0) {
      container.innerHTML = '<div class="empty-state py-3"><div class="empty-title">No hay datos</div></div>';
      return;
    }
    let html = '<div class="table-responsive"><table class="table" style="font-size:.85rem"><thead><tr><th>Producto</th><th class="text-end">Stock</th><th class="text-end">Ventas</th></tr></thead><tbody>';
    productos.forEach(p => {
      html += `<tr><td>${p.producto__nombre || p.nombre || p.producto || ''}</td><td class="text-end">${p.stock_actual || p.stock || 0}</td><td class="text-end">${p.total_vendido || p.vendido || 0}</td></tr>`;
    });
    html += '</tbody></table></div>';
    container.innerHTML = html;
  }
};
