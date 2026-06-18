const ValoracionPage = {
  currentPage: 1,
  _chartInstance: null,
  _productosData: [],
  _categoriasData: [],

  render: async function (container) {
    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-chart-line text-gradient"></i>Valoración de Inventario</h3>
      </div>

      <div class="kpi-grid" style="grid-template-columns:repeat(2,1fr)" id="valoracionCards"></div>

      <div class="row g-4" style="margin-top:0.5rem">
        <div class="col-xl-4">
          <div class="table-container" style="margin-bottom:1.5rem">
            <div class="table-toolbar">
              <h6 class="toolbar-title"><i class="fas fa-chart-pie" style="color:var(--accent)"></i>Distribución de Capital</h6>
            </div>
            <div style="padding:1rem;display:flex;justify-content:center">
              <canvas id="chartCapitalCategoria" style="max-height:280px"></canvas>
            </div>
          </div>
          <div class="table-container">
            <div class="table-toolbar">
              <h6 class="toolbar-title"><i class="fas fa-tag" style="color:var(--primary)"></i>Resumen por Categoría</h6>
            </div>
            <div class="table-responsive">
              <table class="table">
                <thead><tr><th>Categoría</th><th class="text-center">Items</th><th class="text-end">Valor Total</th></tr></thead>
                <tbody id="tbodyCategoriasValor">
                  <tr><td colspan="3" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="col-xl-8">
          <div class="table-container">
            <div class="table-toolbar">
              <h6 class="toolbar-title"><i class="fas fa-box" style="color:var(--primary)"></i>Detalle por Producto</h6>
            </div>
            <div class="filters-container" style="display:flex;gap:1rem;padding:0 1rem 1rem;flex-wrap:wrap;align-items:flex-end">
              <div class="filter-group" style="flex:1;min-width:200px">
                <label class="form-label small fw-bold text-muted">Buscar Producto</label>
                <div class="search-box" style="margin-top:0">
                  <i class="fas fa-search"></i>
                  <input type="text" id="filterValoracionQ" placeholder="Escriba nombre del producto...">
                </div>
              </div>
              <div class="filter-group" style="width:220px">
                <label class="form-label small fw-bold text-muted">Categoría</label>
                <select id="filterValoracionCategoria" class="form-select" style="border-radius:50px;padding:0.55rem 1rem">
                  <option value="">Todas las categorías</option>
                </select>
              </div>
            </div>
            <div class="table-responsive">
              <table class="table">
                <thead>
                  <tr><th>Producto</th><th class="text-center">Stock</th><th class="text-end">Costo Unit.</th><th class="text-end">Valor Total</th></tr>
                </thead>
                <tbody id="tbodyProductosValor">
                  <tr><td colspan="4" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>
                </tbody>
              </table>
            </div>
          </div>
          <div id="valoracionPagination" class="py-3"></div>
        </div>
      </div>
    `;
    this.currentPage = 1;
    await this.cargarValoracion();
  },

  cargarValoracion: async function (page = 1) {
    this.currentPage = page;
    try {
      const data = await API.get(`inventario/valoracion/?page=${page}`);
      this.renderCards(data);
      this.renderCategorias(data.categorias_valor || []);
      this.renderProductos(data.productos || []);
      this.renderChart(data.categorias_valor || []);

      // Attach filter event listeners
      const inputQ = document.getElementById('filterValoracionQ');
      const selectCat = document.getElementById('filterValoracionCategoria');
      if (inputQ) {
        inputQ.addEventListener('input', () => this.filterProductos());
      }
      if (selectCat) {
        selectCat.addEventListener('change', () => this.filterProductos());
      }

      if (data.pagination) {
        Utils.renderPagination(data.pagination, 'valoracionPagination', this.currentPage, (p) => {
          this.cargarValoracion(p);
        });
      }
    } catch (e) {
      document.getElementById('tbodyCategoriasValor').innerHTML = `<tr><td colspan="3" class="text-center py-4" style="color:var(--danger)">Error: ${e.message}</td></tr>`;
      document.getElementById('tbodyProductosValor').innerHTML = `<tr><td colspan="4" class="text-center py-4" style="color:var(--danger)">Error: ${e.message}</td></tr>`;
    }
  },

  renderCards: function (data) {
    document.getElementById('valoracionCards').innerHTML = `
      <div class="kpi-card kpi-primary">
        <div class="kpi-icon"><i class="fas fa-coins"></i></div>
        <div class="kpi-label">Valor Total del Inventario</div>
        <div class="kpi-value">${Utils.formatMoney(data.gran_total || 0)}</div>
        <div style="font-size:.75rem;color:var(--text-muted)">A costo de adquisición</div>
      </div>
      <div class="kpi-card kpi-info">
        <div class="kpi-icon"><i class="fas fa-boxes"></i></div>
        <div class="kpi-label">Unidades Totales</div>
        <div class="kpi-value">${data.total_unidades || 0}</div>
        <div style="font-size:.75rem;color:var(--text-muted)">Items en inventario</div>
      </div>
    `;
  },

  renderCategorias: function (categorias) {
    this._categoriasData = categorias;

    const tbody = document.getElementById('tbodyCategoriasValor');
    if (!categorias.length) {
      tbody.innerHTML = '<tr><td colspan="3"><div class="empty-state py-3"><div class="empty-title">No hay categorías con productos</div></div></td></tr>';
      return;
    }

    tbody.innerHTML = categorias.map(c => `
      <tr>
        <td data-label="Categoría" style="font-weight:600">${c.nombre}</td>
        <td data-label="Items" class="text-center">${c.total_items}</td>
        <td data-label="Valor" class="text-end fw-bold" style="color:var(--primary)">${Utils.formatMoney(c.valor_categoria)}</td>
      </tr>
    `).join('');

    // Populate the category filter dropdown
    const select = document.getElementById('filterValoracionCategoria');
    if (select) {
      select.innerHTML = '<option value="">Todas las categorías</option>' +
        categorias.map(c => `<option value="${c.nombre}">${c.nombre}</option>`).join('');
    }
  },

  renderProductos: function (productos) {
    this._productosData = productos;
    this._renderProductosRows(productos);
  },

  _renderProductosRows: function (productos) {
    const tbody = document.getElementById('tbodyProductosValor');
    if (!productos.length) {
      tbody.innerHTML = '<tr><td colspan="4"><div class="empty-state py-3"><div class="empty-title">No hay productos registrados</div></div></td></tr>';
      return;
    }

    tbody.innerHTML = productos.map(p => {
      return `
        <tr>
          <td data-label="Producto">
            <div style="font-weight:600">${p.nombre}</div>
            <small style="color:var(--text-muted)">${p.categoria?.nombre || 'Sin categoría'}</small>
          </td>
          <td data-label="Stock" class="text-center"><span class="badge badge-info">${p.stock}</span></td>
          <td data-label="Costo Unit." class="text-end">${Utils.formatMoney(p.costo)}</td>
          <td data-label="Valor Total" class="text-end fw-bold" style="color:var(--primary)">${Utils.formatMoney(p.valor_total)}</td>
        </tr>
      `;
    }).join('');
  },

  filterProductos: function () {
    const query = (document.getElementById('filterValoracionQ')?.value || '').toLowerCase();
    const catFilter = document.getElementById('filterValoracionCategoria')?.value || '';

    const filtered = this._productosData.filter(p => {
      const matchName = !query || p.nombre.toLowerCase().includes(query);
      const matchCat = !catFilter || (p.categoria?.nombre || '') === catFilter;
      return matchName && matchCat;
    });

    this._renderProductosRows(filtered);
  },

  renderChart: function (categorias) {
    const canvas = document.getElementById('chartCapitalCategoria');
    if (!canvas) return;

    if (this._chartInstance) {
      this._chartInstance.destroy();
    }

    if (!categorias.length) return;

    const ctx = canvas.getContext('2d');
    const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text').trim();
    const labels = categorias.map(c => c.nombre);
    const valores = categorias.map(c => c.valor_categoria);
    const colors = categorias.map((_, i) => `hsl(${(i * 360 / categorias.length + 200) % 360}, 70%, 55%)`);

    const config = {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: valores,
          backgroundColor: colors,
          borderWidth: 2,
          borderColor: getComputedStyle(document.documentElement).getPropertyValue('--card-bg').trim() || '#1a1a2e'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: textColor,
              padding: 15,
              usePointStyle: true
            }
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const value = context.parsed;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const pct = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                return ` ${context.label}: ${Utils.formatMoney(value)} (${pct}%)`;
              }
            }
          }
        }
      }
    };

    this._chartInstance = new Chart(ctx, config);
  }
};
