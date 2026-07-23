const ReportesPage = {
  charts: {},

  render: async function(container) {
    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-chart-line text-gradient"></i>Reporte Analítico de Ventas e Inteligencia de Negocios</h3>
      </div>

      <div class="filters-bar" style="row-gap: 12px">
        <div class="filter-group">
          <label>Período Rápido</label>
          <div class="btn-group" role="group" id="filtrosRapidos">
            <button class="btn btn-primary btn-sm active" data-filtro="hoy">Hoy</button>
            <button class="btn btn-ghost btn-sm" data-filtro="ayer">Ayer</button>
            <button class="btn btn-ghost btn-sm" data-filtro="semana">Esta Semana</button>
            <button class="btn btn-ghost btn-sm" data-filtro="mes">Este Mes</button>
            <button class="btn btn-ghost btn-sm" data-filtro="mes_anterior">Mes Anterior</button>
            <button class="btn btn-ghost btn-sm" data-filtro="personalizado" title="Rango Personalizado">
              <i class="fas fa-calendar-alt me-1"></i>Personalizado
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
            <option value="">Todos los Métodos</option>
            <option value="Efectivo">💵 Efectivo</option>
            <option value="Yape">📱 Yape</option>
            <option value="Plin">📱 Plin</option>
            <option value="Tarjeta">💳 Tarjeta</option>
          </select>
        </div>

        <div class="filter-group" style="align-self:flex-end">
          <div style="display:flex;gap:6px">
            <button class="btn btn-success btn-sm btn-pill" id="btnExportarExcel"><i class="fas fa-file-excel me-1"></i>Exportar Excel</button>
            <button class="btn btn-danger btn-sm btn-pill" id="btnExportarPDF"><i class="fas fa-file-pdf me-1"></i>Exportar PDF</button>
          </div>
        </div>
      </div>

      <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin:1.25rem 0" id="kpiCards"></div>

      <div class="row g-3" style="margin-bottom:1.5rem">
        <div class="col-lg-8">
          <div class="card h-100">
            <div class="card-header bg-transparent border-0 pt-3 ps-3">
              <h6 class="fw-bold m-0"><i class="fas fa-chart-area text-primary me-2"></i>Evolución de Ventas</h6>
            </div>
            <div class="card-body" style="padding:0.75rem; min-height: 280px">
              <canvas id="chartEvolucion"></canvas>
            </div>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="card h-100">
            <div class="card-header bg-transparent border-0 pt-3 ps-3">
              <h6 class="fw-bold m-0"><i class="fas fa-pie-chart text-success me-2"></i>Métodos de Pago</h6>
            </div>
            <div class="card-body" style="padding:0.75rem; min-height: 280px">
              <canvas id="chartMetodosPago"></canvas>
            </div>
          </div>
        </div>
      </div>

      <div class="row g-3" style="margin-bottom:1.5rem">
        <div class="col-lg-6">
          <div class="card h-100">
            <div class="card-header bg-transparent border-0 pt-3 ps-3">
              <h6 class="fw-bold m-0"><i class="fas fa-tags text-warning me-2"></i>Ventas por Categoría</h6>
            </div>
            <div class="card-body" style="padding:0.75rem; min-height: 260px">
              <canvas id="chartCategorias"></canvas>
            </div>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="table-container h-100">
            <div class="table-toolbar">
              <h6 class="toolbar-title"><i class="fas fa-user-tie text-info me-2"></i>Rendimiento de Ventas por Cajero</h6>
            </div>
            <div id="cajerosStats" class="p-3"></div>
          </div>
        </div>
      </div>

      <div class="charts-bottom">
        <div class="table-container">
          <div class="table-toolbar">
            <h6 class="toolbar-title"><i class="fas fa-trophy text-warning me-2"></i>Top 10 Productos Más Vendidos</h6>
          </div>
          <div id="topProductos" class="p-3"></div>
        </div>
        <div class="table-container">
          <div class="table-toolbar">
            <h6 class="toolbar-title"><i class="fas fa-exclamation-triangle text-danger me-2"></i>Productos Sin Venta / Baja Rotación</h6>
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
        document.querySelectorAll('#filtrosRapidos .btn').forEach(b => { 
          b.className = 'btn btn-ghost btn-sm'; 
        });
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
    const repFechaFin = document.getElementById('rep_fecha_fin');
    const doFechaChange = () => {
      if (repFechaInicio.value && repFechaFin.value) {
        ReportesPage.cargarReporte('personalizado');
      }
    };
    if (repFechaInicio) repFechaInicio.addEventListener('change', doFechaChange);
    if (repFechaFin) repFechaFin.addEventListener('change', doFechaChange);

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

  exportar: async function(formato) {
    const loading = Utils.showLoading();
    try {
      const activo = document.querySelector('#filtrosRapidos .btn.active');
      const filtro = activo ? activo.dataset.filtro : 'hoy';
      let params = `filtro=${filtro}`;
      if (filtro === 'personalizado') {
        const fi = document.getElementById('rep_fecha_inicio')?.value;
        const ff = document.getElementById('rep_fecha_fin')?.value;
        if (fi) params += `&fecha_inicio=${fi}`;
        if (ff) params += `&fecha_fin=${ff}`;
      }
      const metodo = document.getElementById('rep_metodo_pago')?.value;
      if (metodo) params += `&metodo_pago=${metodo}`;

      const url = API.baseURL + `reportes/ventas/${formato}/?${params}`;
      const response = await fetch(url, { credentials: 'include' });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const blob = await response.blob();
      const downloadUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      const ext = formato === 'excel' ? 'xlsx' : 'pdf';
      a.download = `reporte_ventas_${filtro}_${new Date().toISOString().split('T')[0]}.${ext}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(downloadUrl);
      Utils.showToast(`Reporte ${formato.toUpperCase()} descargado correctamente`, 'success');
    } catch (e) {
      Utils.showToast('Error al exportar reporte: ' + e.message, 'danger');
    } finally {
      loading.close();
    }
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
      this.renderCajerosStats(data.cajeros_stats || []);
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
        <div class="kpi-label">Utilidad Neta Total</div>
        <div class="kpi-value">${Utils.formatMoney(data.utilidad_total || 0)}</div>
        <small class="text-success fw-bold mt-1" style="font-size:0.75rem">Margen: ${(data.margen_porcentaje || 0).toFixed(1)}%</small>
      </div>
      <div class="kpi-card kpi-info">
        <div class="kpi-icon"><i class="fas fa-receipt"></i></div>
        <div class="kpi-label">Ticket Promedio</div>
        <div class="kpi-value">${Utils.formatMoney(data.ticket_promedio || 0)}</div>
      </div>
      <div class="kpi-card kpi-warning">
        <div class="kpi-icon"><i class="fas fa-shopping-bag"></i></div>
        <div class="kpi-label">Total Transacciones</div>
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
    if (this.charts.categorias) this.charts.categorias.destroy();

    const t = this.getChartTheme();

    // 1. Evolución
    const ctx1 = document.getElementById('chartEvolucion');
    if (ctx1) {
      this.charts.evolucion = new Chart(ctx1, {
        type: 'line',
        data: {
          labels: data.fechas_chart || [],
          datasets: [{
            label: 'Ventas (S/)',
            data: data.totales_chart || [],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.12)',
            fill: true,
            tension: 0.4,
            borderWidth: 2.5,
            pointRadius: 4,
            pointBackgroundColor: '#3b82f6'
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

    // 2. Métodos de Pago
    const ctx2 = document.getElementById('chartMetodosPago');
    if (ctx2) {
      this.charts.metodos = new Chart(ctx2, {
        type: 'doughnut',
        data: {
          labels: data.metodos_pago_chart || [],
          datasets: [{
            data: data.totales_metodos_chart || [],
            backgroundColor: ['#10b981', '#8b5cf6', '#06b6d4', '#f59e0b', '#64748b']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { color: t.color, font: { size: 11 } } }
          }
        }
      });
    }

    // 3. Ventas por Categoría
    const ctx3 = document.getElementById('chartCategorias');
    if (ctx3) {
      this.charts.categorias = new Chart(ctx3, {
        type: 'bar',
        data: {
          labels: data.categorias_chart || [],
          datasets: [{
            label: 'Ventas por Categoría (S/)',
            data: data.totales_categorias_chart || [],
            backgroundColor: 'rgba(245, 158, 11, 0.75)',
            borderColor: '#f59e0b',
            borderWidth: 1,
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: t.color, font: { size: 10 } }, grid: { display: false } },
            y: { beginAtZero: true, ticks: { color: t.color }, grid: { color: t.grid } }
          }
        }
      });
    }
  },

  renderTopProductos: function(productos) {
    const container = document.getElementById('topProductos');
    if (!productos || productos.length === 0) {
      container.innerHTML = '<div class="empty-state py-3"><div class="empty-title">No hay datos registrados</div></div>';
      return;
    }

    const maxRev = Math.max(...productos.map(p => p.total_revenue || 0)) || 1;

    let html = '<div class="table-responsive"><table class="table align-middle" style="font-size:.85rem"><thead><tr><th>#</th><th>Producto</th><th class="text-end">Unidades</th><th class="text-end">Total Recaudado</th></tr></thead><tbody>';
    productos.forEach((p, i) => {
      const rev = p.total_revenue || 0;
      const pct = Math.min(100, Math.round((rev / maxRev) * 100));
      html += `<tr>
        <td class="fw-bold">${i + 1}</td>
        <td>
          <div class="fw-bold">${Utils.escapeHtml(p.producto__nombre || p.nombre || '')}</div>
          <div class="progress mt-1" style="height: 4px;">
            <div class="progress-bar bg-success" role="progressbar" style="width: ${pct}%"></div>
          </div>
        </td>
        <td class="text-end fw-bold">${p.total_qty || 0}</td>
        <td class="text-end text-success fw-bold">${Utils.formatMoney(rev)}</td>
      </tr>`;
    });
    html += '</tbody></table></div>';
    container.innerHTML = html;
  },

  renderBajaRotacion: function(productos) {
    const container = document.getElementById('bajaRotacion');
    if (!productos || productos.length === 0) {
      container.innerHTML = '<div class="empty-state py-3"><div class="empty-title">Todos los productos tienen movimiento activo</div></div>';
      return;
    }
    let html = '<div class="table-responsive"><table class="table align-middle" style="font-size:.85rem"><thead><tr><th>Producto</th><th class="text-end">Stock Actual</th><th class="text-end">Capital Inmovilizado</th></tr></thead><tbody>';
    productos.forEach(p => {
      const stock = parseFloat(p.stock) || 0;
      const precio = parseFloat(p.precio) || 0;
      const capital = stock * precio;
      const badgeStyle = stock <= 0 
        ? 'background:rgba(239,68,68,0.15);color:#ef4444;border:1px solid rgba(239,68,68,0.3);' 
        : 'background:rgba(59,130,246,0.15);color:#3b82f6;border:1px solid rgba(59,130,246,0.3);';
      html += `<tr>
        <td class="fw-bold">${Utils.escapeHtml(p.nombre || '')}</td>
        <td class="text-end"><span class="badge" style="${badgeStyle}font-weight:700;font-size:0.8rem;padding:5px 12px;border-radius:20px;">${stock} und</span></td>
        <td class="text-end text-danger fw-bold">${Utils.formatMoney(capital)}</td>
      </tr>`;
    });
    html += '</tbody></table></div>';
    container.innerHTML = html;
  },

  renderCajerosStats: function(cajeros) {
    const container = document.getElementById('cajerosStats');
    if (!cajeros || cajeros.length === 0) {
      container.innerHTML = '<div class="empty-state py-3"><div class="empty-title">Sin ventas en el período</div></div>';
      return;
    }
    let html = '<div class="table-responsive"><table class="table align-middle" style="font-size:.85rem"><thead><tr><th>Cajero / Usuario</th><th class="text-center">Transacciones</th><th class="text-end">Monto Total</th></tr></thead><tbody>';
    cajeros.forEach(c => {
      html += `<tr>
        <td class="fw-bold"><i class="fas fa-user-circle me-1 text-primary"></i>${Utils.escapeHtml(c.nombre)}</td>
        <td class="text-center"><span class="badge" style="background:rgba(79,70,229,0.15);color:#6366f1;border:1px solid rgba(79,70,229,0.3);font-weight:700;font-size:0.82rem;padding:5px 12px;border-radius:20px;"><i class="fas fa-shopping-cart me-1"></i>${c.ventas} ventas</span></td>
        <td class="text-end text-primary fw-bold">${Utils.formatMoney(c.monto)}</td>
      </tr>`;
    });
    html += '</tbody></table></div>';
    container.innerHTML = html;
  }
};


