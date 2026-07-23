const ComprasPage = {
  tomSelects: {},
  currentPage: 1,
  filtroProveedor: '',
  filtroFechaDesde: '',
  filtroFechaHasta: '',
  filtroQ: '',

  render: async function(container) {
    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-truck text-gradient"></i>Gestión y Reabastecimiento de Compras</h3>
        <div class="page-actions">
          <button class="btn btn-primary btn-sm btn-pill" id="btnNuevaCompra"><i class="fas fa-plus me-1"></i>Nueva Compra</button>
        </div>
      </div>

      <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:1.25rem" id="comprasCards">
        <div class="kpi-card kpi-primary">
          <div class="kpi-icon"><i class="fas fa-file-invoice-dollar"></i></div>
          <div class="kpi-label">Compras Acumuladas</div>
          <div class="kpi-value" id="kpiComprasTotal">S/ 0.00</div>
        </div>
        <div class="kpi-card kpi-success">
          <div class="kpi-icon"><i class="fas fa-shopping-bag"></i></div>
          <div class="kpi-label">Órdenes Registradas</div>
          <div class="kpi-value" id="kpiComprasNum">0</div>
        </div>
        <div class="kpi-card kpi-info">
          <div class="kpi-icon"><i class="fas fa-boxes"></i></div>
          <div class="kpi-label">Unidades Ingresadas</div>
          <div class="kpi-value" id="kpiComprasQty">0</div>
        </div>
        <div class="kpi-card kpi-warning">
          <div class="kpi-icon"><i class="fas fa-truck-ramp-box"></i></div>
          <div class="kpi-label">Proveedores Atendidos</div>
          <div class="kpi-value" id="kpiComprasProv">0</div>
        </div>
      </div>

      <div class="filters-bar">
        <div class="filter-group">
          <label>Proveedor</label>
          <select id="filterCompraProveedor" class="form-select form-select-sm" style="min-width:180px">
            <option value="">Todos los proveedores</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Desde</label>
          <input type="date" id="filterCompraFechaDesde" class="form-control form-control-sm">
        </div>
        <div class="filter-group">
          <label>Hasta</label>
          <input type="date" id="filterCompraFechaHasta" class="form-control form-control-sm">
        </div>
        <div class="filter-group" style="flex:1;min-width:150px">
          <label>Buscar</label>
          <input type="text" id="filterCompraQ" class="form-control form-control-sm" placeholder="N° Comprobante, proveedor o producto...">
        </div>
        <div class="filter-group" style="align-self:flex-end">
          <button class="btn btn-ghost btn-sm" id="btnLimpiarFiltrosCompra"><i class="fas fa-undo me-1"></i>Limpiar</button>
        </div>
      </div>

      <div class="table-container">
        <div class="table-responsive">
          <table class="table align-middle">
            <thead>
              <tr>
                <th># Compra / Documento</th>
                <th>Proveedor</th>
                <th>Fecha Recepción</th>
                <th>Registrado Por</th>
                <th class="text-end">Total Compra</th>
                <th class="text-center" style="width:100px">Acción</th>
              </tr>
            </thead>
            <tbody id="comprasTableBody">
              <tr><td colspan="6" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>
            </tbody>
          </table>
        </div>
        <div id="comprasPagination" class="py-3"></div>
      </div>

      ${this.modalCompraHTML()}
      ${this.modalDetalleHTML()}`;
    this.bindEvents();
    await this.cargarProveedoresFiltro();
    await this.cargarCompras();
  },

  modalCompraHTML: function() {
    return `
    <div class="modal-overlay" id="compraModal">
      <div class="modal-card" style="max-width:860px">
        <div class="modal-card-header">
          <h5><i class="fas fa-truck me-2 text-primary"></i>Nueva Compra / Reabastecimiento de Almacén</h5>
          <button class="modal-close" onclick="Utils.hideModal('compraModal')"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-card-body">
          <div class="row g-3 mb-3">
            <div class="col-md-5">
              <div class="form-group">
                <label class="form-label">Proveedor <span class="text-danger">*</span></label>
                <select id="compra_proveedor" placeholder="Buscar proveedor..."></select>
              </div>
            </div>
            <div class="col-md-3">
              <div class="form-group">
                <label class="form-label">Tipo Comprobante</label>
                <select id="compra_tipo_doc" class="form-select">
                  <option value="FACTURA">🧾 Factura Electrónica</option>
                  <option value="BOLETA">📜 Boleta de Venta</option>
                  <option value="GUIA_REMISION">🚚 Guía de Remisión</option>
                  <option value="TICKET">🎫 Ticket de Entrada</option>
                </select>
              </div>
            </div>
            <div class="col-md-2">
              <div class="form-group">
                <label class="form-label">Serie</label>
                <input type="text" class="form-control text-uppercase" id="compra_serie" placeholder="Ej: F001">
              </div>
            </div>
            <div class="col-md-2">
              <div class="form-group">
                <label class="form-label">Número</label>
                <input type="text" class="form-control" id="compra_numero" placeholder="Ej: 00492">
              </div>
            </div>
            <div class="col-md-4">
              <div class="form-group">
                <label class="form-label">Fecha de Compra <span class="text-danger">*</span></label>
                <input type="date" class="form-control" id="compra_fecha">
              </div>
            </div>
            <div class="col-md-8">
              <div class="form-group">
                <label class="form-label">Observaciones / Guía</label>
                <input type="text" class="form-control" id="compra_obs" placeholder="Ej: Factura a 30 días, lote de promoción">
              </div>
            </div>
          </div>

          <h6 style="font-weight:600;margin-bottom:12px"><i class="fas fa-boxes me-2 text-warning"></i>Detalle de Productos e Ingreso de Lotes</h6>
          <div id="compraProductos"></div>
          <button class="btn btn-ghost btn-sm" id="btnAgregarProducto" style="margin-top:8px"><i class="fas fa-plus me-1"></i>Agregar Producto</button>
          
          <hr>
          <div class="d-flex justify-content-between align-items-center" style="font-size:1.25rem;font-weight:700">
            <span>Total Inversión Compra:</span>
            <span id="compraTotal" class="text-success">S/ 0.00</span>
          </div>
        </div>
        <div class="modal-card-footer">
          <button class="btn btn-ghost" onclick="Utils.hideModal('compraModal')">Cancelar</button>
          <button class="btn btn-primary" id="btnGuardarCompra"><i class="fas fa-check-circle me-1"></i>Registrar Compra e Ingresar a Kardex</button>
        </div>
      </div>
    </div>`;
  },


  modalDetalleHTML: function() {
    return `
    <div class="modal-overlay" id="detalleCompraModal">
      <div class="modal-card" style="max-width:680px">
        <div class="modal-card-header">
          <h5><i class="fas fa-receipt me-2"></i>Detalle de Compra</h5>
          <button class="modal-close" onclick="Utils.hideModal('detalleCompraModal')"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-card-body" id="detalleCompraBody"></div>
      </div>
    </div>`;
  },

  bindEvents: function() {
    const btnNuevaCompra = document.getElementById('btnNuevaCompra');
    if (btnNuevaCompra) btnNuevaCompra.addEventListener('click', () => this.abrirNuevaCompra());
    const btnAgregarProducto = document.getElementById('btnAgregarProducto');
    if (btnAgregarProducto) btnAgregarProducto.addEventListener('click', () => this.agregarFilaProducto());
    const btnGuardarCompra = document.getElementById('btnGuardarCompra');
    if (btnGuardarCompra) btnGuardarCompra.addEventListener('click', () => this.guardarCompra());

    const filterProveedor = document.getElementById('filterCompraProveedor');
    const filterFechaDesde = document.getElementById('filterCompraFechaDesde');
    const filterFechaHasta = document.getElementById('filterCompraFechaHasta');
    const filterQ = document.getElementById('filterCompraQ');
    const btnLimpiar = document.getElementById('btnLimpiarFiltrosCompra');

    const doFilter = () => {
      this.filtroProveedor = filterProveedor ? filterProveedor.value : '';
      this.filtroFechaDesde = filterFechaDesde ? filterFechaDesde.value : '';
      this.filtroFechaHasta = filterFechaHasta ? filterFechaHasta.value : '';
      this.filtroQ = filterQ ? filterQ.value.trim() : '';
      this.currentPage = 1;
      this.cargarCompras();
    };

    if (filterProveedor) filterProveedor.addEventListener('change', doFilter);
    if (filterFechaDesde) filterFechaDesde.addEventListener('change', doFilter);
    if (filterFechaHasta) filterFechaHasta.addEventListener('change', doFilter);

    let searchTimer;
    if (filterQ) {
      filterQ.addEventListener('input', () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(doFilter, 400);
      });
    }
    if (btnLimpiar) {
      btnLimpiar.addEventListener('click', () => {
        if (filterProveedor) filterProveedor.value = '';
        if (filterFechaDesde) filterFechaDesde.value = '';
        if (filterFechaHasta) filterFechaHasta.value = '';
        if (filterQ) filterQ.value = '';
        this.filtroProveedor = '';
        this.filtroFechaDesde = '';
        this.filtroFechaHasta = '';
        this.filtroQ = '';
        this.currentPage = 1;
        this.cargarCompras();
      });
    }
  },

  cargarProveedoresFiltro: async function() {
    try {
      const data = await API.get('proveedores/');
      const proveedores = data.results || data || [];
      const select = document.getElementById('filterCompraProveedor');
      if (!select) return;
      select.innerHTML = '<option value="">Todos</option>';
      proveedores.forEach(p => {
        select.innerHTML += `<option value="${p.id}">${p.nombre}</option>`;
      });
    } catch (e) {
      console.error('Error cargando proveedores para filtro', e);
    }
  },

  cargarCompras: async function(page = 1) {
    this.currentPage = page;
    const tbody = document.getElementById('comprasTableBody');
    try {
      let url = `compras/?page=${page}`;
      if (this.filtroProveedor) url += `&proveedor_id=${this.filtroProveedor}`;
      if (this.filtroFechaDesde) url += `&fecha_desde=${this.filtroFechaDesde}`;
      if (this.filtroFechaHasta) url += `&fecha_hasta=${this.filtroFechaHasta}`;
      if (this.filtroQ) url += `&q=${encodeURIComponent(this.filtroQ)}`;
      const data = await API.get(url);

      const compras = data.results || [];
      const totalSum = compras.reduce((acc, curr) => acc + parseFloat(curr.total || 0), 0);
      let totalQty = 0;
      const provSet = new Set();

      compras.forEach(c => {
        if (c.proveedor?.nombre) provSet.add(c.proveedor.nombre);
        (c.detalles || []).forEach(d => totalQty += parseFloat(d.cantidad || 0));
      });

      document.getElementById('kpiComprasTotal').textContent = Utils.formatMoney(totalSum);
      document.getElementById('kpiComprasNum').textContent = data.count || compras.length;
      document.getElementById('kpiComprasQty').textContent = Math.round(totalQty);
      document.getElementById('kpiComprasProv').textContent = provSet.size || '-';

      this.renderTabla(compras);
      Utils.renderPagination(data, 'comprasPagination', this.currentPage, (p) => this.cargarCompras(p));
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4" style="color:var(--danger)">Error: ${e.message}</td></tr>`;
    }
  },

  renderTabla: function(compras) {
    const tbody = document.getElementById('comprasTableBody');
    if (!compras || compras.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><div class="empty-icon"><i class="fas fa-truck"></i></div><div class="empty-title">No hay compras registradas</div></div></td></tr>`;
      return;
    }
    let html = '';
    compras.forEach(c => {
      const docStr = c.serie_comprobante ? `${c.serie_comprobante}-${c.numero_comprobante || ''}` : `N° ${c.id}`;
      const badgeDoc = c.tipo_comprobante ? `<span class="badge bg-primary-subtle text-primary">${c.tipo_comprobante}</span>` : '';
      html += `
      <tr>
        <td data-label="Documento">
          <div class="fw-bold text-primary"># ${c.id}</div>
          <small class="text-muted">${badgeDoc} ${Utils.escapeHtml(docStr)}</small>
        </td>
        <td data-label="Proveedor">
          <div class="fw-bold">${Utils.escapeHtml(c.proveedor ? (c.proveedor.nombre || c.proveedor) : 'N/A')}</div>
          ${c.observaciones ? `<small class="text-muted">${Utils.escapeHtml(c.observaciones)}</small>` : ''}
        </td>
        <td data-label="Fecha">${Utils.formatDate(c.fecha)}</td>
        <td data-label="Registrado Por"><small class="text-muted"><i class="fas fa-user me-1"></i>${Utils.escapeHtml(c.usuario ? c.usuario.username : 'Sistema')}</small></td>
        <td data-label="Total" class="text-end fw-bold text-success" style="font-size:1.05rem">${Utils.formatMoney(c.total)}</td>
        <td data-label="Acción" class="text-center">
          <button class="btn btn-sm btn-icon btn-ghost btn-ver-compra" data-id="${c.id}" title="Ver Detalle / Imprimir" style="color:var(--accent)"><i class="fas fa-eye"></i></button>
        </td>
      </tr>`;
    });
    tbody.innerHTML = html;
    tbody.querySelectorAll('.btn-ver-compra').forEach(btn => {
      btn.addEventListener('click', () => this.verDetalle(btn.dataset.id));
    });
  },


  abrirNuevaCompra: function() {
    document.getElementById('compra_fecha').value = new Date().toISOString().split('T')[0];
    document.getElementById('compraTotal').textContent = 'S/ 0.00';
    document.getElementById('compraProductos').innerHTML = '';
    
    // Destroy previous TomSelects
    Object.values(this.tomSelects).forEach(ts => ts.destroy());
    this.tomSelects = {};

    // Initialize Provider TomSelect
    const proveedorSelect = new TomSelect('#compra_proveedor', {
      valueField: 'id',
      labelField: 'nombre',
      searchField: 'nombre',
      placeholder: 'Buscar proveedor...',
      create: false,
      load: async (query, callback) => {
        if (!query || query.length < 2) return callback();
        try {
          const data = await API.get(`proveedores/?search=${encodeURIComponent(query)}`);
          callback(data.results || data);
        } catch (e) { callback(); }
      }
    });
    this.tomSelects['proveedor'] = proveedorSelect;

    // Load all suppliers initially
    (async () => {
      try {
        const data = await API.get('proveedores/?page_size=500');
        const items = data.results || data || [];
        proveedorSelect.clearOptions();
        proveedorSelect.addOptions(items);
      } catch (e) {
        console.error('Error cargando proveedores', e);
      }
    })();

    this.agregarFilaProducto();
    Utils.showModal('compraModal');
  },

  filaProductoHTML: function(index) {
    return `
    <div class="compra-item mb-2" data-index="${index}">
      <div class="row g-2 align-items-end compra-main-row">
        <div class="col-md-5">
          <label class="form-label" style="font-size:.75rem;margin-bottom:2px">Producto <span class="text-danger">*</span></label>
          <select class="producto-select" id="prod_select_${index}" data-index="${index}" placeholder="Buscar producto..."></select>
        </div>
        <div class="col-md-2">
          <label class="form-label" style="font-size:.75rem;margin-bottom:2px">Precio Costo <span class="text-danger">*</span></label>
          <input type="number" step="0.01" class="form-control form-control-sm precio-input" data-index="${index}" placeholder="P. Costo" value="0" min="0">
        </div>
        <div class="col-md-1">
          <button class="btn btn-sm btn-icon btn-ghost btn-quitar-producto" data-index="${index}" style="color:var(--danger)"><i class="fas fa-times"></i></button>
        </div>
      </div>
      <div class="vencimiento-grupos" data-index="${index}">
        <div class="vencimiento-grupo row g-2 align-items-center mt-1" data-grupo="0">
          <div class="col-md-4 offset-md-3">
            <input type="number" step="0.01" class="form-control form-control-sm cantidad-grupo-input" data-index="${index}" data-grupo="0" placeholder="Cant" value="1" min="0.01">
          </div>
          <div class="col-md-4">
            <input type="date" class="form-control form-control-sm vencimiento-grupo-input" data-index="${index}" data-grupo="0">
          </div>
          <div class="col-md-1">
            <button class="btn btn-sm btn-icon btn-ghost btn-quitar-grupo" data-index="${index}" data-grupo="0" style="color:var(--danger)"><i class="fas fa-times"></i></button>
          </div>
        </div>
      </div>
      <button class="btn btn-ghost btn-xs btn-agregar-grupo" data-index="${index}" style="margin-top:4px;font-size:.75rem"><i class="fas fa-plus"></i>Agregar vencimiento</button>
    </div>`;
  },

  agregarFilaProducto: function() {
    const container = document.getElementById('compraProductos');
    const index = Date.now();
    container.insertAdjacentHTML('beforeend', this.filaProductoHTML(index));
    
    // Initialize Product TomSelect
    const ts = new TomSelect(`#prod_select_${index}`, {
      valueField: 'id',
      labelField: 'nombre',
      searchField: 'nombre',
      placeholder: 'Buscar producto...',
      create: false,
      load: async (query, callback) => {
        if (!query || query.length < 2) return callback();
        try {
          const data = await API.get(`productos/?search=${encodeURIComponent(query)}`);
          callback(data.results || data);
        } catch (e) { callback(); }
      },
      onChange: async (val) => {
        if (!val) return;
        const item = document.querySelector(`.compra-item[data-index="${index}"]`);
        const precioInput = item.querySelector('.precio-input');
        try {
          const p = await API.get(`productos/${val}/detalle/`);
          if (precioInput) precioInput.value = p.costo || 0;
          this.calcularTotal();
        } catch (e) {}
      }
    });

    this.tomSelects[`prod_${index}`] = ts;

    // Load all products initially
    (async () => {
      try {
        const data = await API.get('productos/?page_size=500');
        const items = data.results || data || [];
        ts.clearOptions();
        ts.addOptions(items);
      } catch (e) {
        console.error('Error cargando productos', e);
      }
    })();

    this.bindFilaEventos(index);
    this.calcularTotal();
  },

  bindFilaEventos: function(index) {
    const item = document.querySelector(`.compra-item[data-index="${index}"]`);
    if (!item) return;

    item.querySelector('.precio-input').addEventListener('input', () => this.calcularTotal());

    item.querySelectorAll('.cantidad-grupo-input').forEach(inp => {
      inp.addEventListener('input', () => this.calcularTotal());
    });

    item.querySelector('.btn-quitar-producto').addEventListener('click', () => {
      if (this.tomSelects[`prod_${index}`]) {
        this.tomSelects[`prod_${index}`].destroy();
        delete this.tomSelects[`prod_${index}`];
      }
      item.remove();
      this.calcularTotal();
    });

    item.querySelector('.btn-agregar-grupo').addEventListener('click', () => {
      this.agregarGrupoVencimiento(index);
    });

    item.querySelectorAll('.btn-quitar-grupo').forEach(btn => {
      btn.addEventListener('click', function() {
        const grupo = this.closest('.vencimiento-grupo');
        if (grupo && grupo.parentElement.querySelectorAll('.vencimiento-grupo').length > 1) {
          grupo.remove();
          ComprasPage.calcularTotal();
        } else {
          Utils.showToast('Debe haber al menos un vencimiento', 'warning');
        }
      });
    });
  },

  agregarGrupoVencimiento: function(index) {
    const gruposContainer = document.querySelector(`.vencimiento-grupos[data-index="${index}"]`);
    if (!gruposContainer) return;
    const grupoCount = gruposContainer.children.length;
    const html = `
      <div class="vencimiento-grupo row g-2 align-items-center mt-1" data-grupo="${grupoCount}">
        <div class="col-md-4 offset-md-3">
          <input type="number" step="0.01" class="form-control form-control-sm cantidad-grupo-input" data-index="${index}" data-grupo="${grupoCount}" placeholder="Cant" value="0" min="0.01">
        </div>
        <div class="col-md-4">
          <input type="date" class="form-control form-control-sm vencimiento-grupo-input" data-index="${index}" data-grupo="${grupoCount}">
        </div>
        <div class="col-md-1">
          <button class="btn btn-sm btn-icon btn-ghost btn-quitar-grupo" data-index="${index}" data-grupo="${grupoCount}" style="color:var(--danger)"><i class="fas fa-times"></i></button>
        </div>
      </div>`;
    gruposContainer.insertAdjacentHTML('beforeend', html);

    const newGrupo = gruposContainer.lastElementChild;
    newGrupo.querySelector('.cantidad-grupo-input').addEventListener('input', () => this.calcularTotal());
    newGrupo.querySelector('.btn-quitar-grupo').addEventListener('click', function() {
      const grupo = this.closest('.vencimiento-grupo');
      if (grupo && grupo.parentElement.querySelectorAll('.vencimiento-grupo').length > 1) {
        grupo.remove();
        ComprasPage.calcularTotal();
      } else {
        Utils.showToast('Debe haber al menos un vencimiento', 'warning');
      }
    });
  },

  calcularTotal: function() {
    let total = 0;
    document.querySelectorAll('.compra-item').forEach(item => {
      const precio = parseFloat(item.querySelector('.precio-input').value) || 0;
      item.querySelectorAll('.cantidad-grupo-input').forEach(inp => {
        const cant = parseFloat(inp.value) || 0;
        total += cant * precio;
      });
    });
    document.getElementById('compraTotal').textContent = Utils.formatMoney(total);
  },

  guardarCompra: async function() {
    const proveedor_id = this.tomSelects['proveedor']?.getValue();
    const fecha = document.getElementById('compra_fecha').value;
    const tipo_comprobante = document.getElementById('compra_tipo_doc')?.value || 'FACTURA';
    const serie_comprobante = (document.getElementById('compra_serie')?.value || '').trim().toUpperCase();
    const numero_comprobante = (document.getElementById('compra_numero')?.value || '').trim();
    const observaciones = (document.getElementById('compra_obs')?.value || '').trim();

    if (!proveedor_id) { Utils.showToast('Seleccione un proveedor', 'warning'); return; }
    if (!fecha) { Utils.showToast('Seleccione una fecha', 'warning'); return; }

    const detalles = [];
    let hasError = false;
    document.querySelectorAll('.compra-item').forEach(item => {
      const idx = item.dataset.index;
      const producto_id = parseInt(this.tomSelects[`prod_${idx}`]?.getValue()) || 0;
      const precio_costo_unitario = parseFloat(item.querySelector('.precio-input').value) || 0;
      
      if (!producto_id) { hasError = true; return; }
      if (!precio_costo_unitario || precio_costo_unitario <= 0) { hasError = true; return; }

      item.querySelectorAll('.vencimiento-grupo').forEach(grupo => {
        const cantidad = parseFloat(grupo.querySelector('.cantidad-grupo-input').value) || 0;
        const fecha_vencimiento = grupo.querySelector('.vencimiento-grupo-input').value || null;
        if (cantidad > 0) {
          detalles.push({ producto_id, cantidad, precio_costo_unitario, fecha_vencimiento });
        }
      });
    });

    if (hasError) { Utils.showToast('Verifique que todos los productos tengan producto, precio y cantidad válidos', 'warning'); return; }
    if (detalles.length === 0) { Utils.showToast('Agregue al menos un producto con cantidad válida', 'warning'); return; }

    try {
      await API.post('compras/', {
        proveedor_id,
        tipo_comprobante,
        serie_comprobante,
        numero_comprobante,
        observaciones,
        fecha,
        detalles
      });
      Utils.showToast('Compra e Ingreso a Almacén registrado correctamente', 'success');
      Utils.hideModal('compraModal');
      this.cargarCompras();
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'danger');
    }
  },

  verDetalle: async function(id) {
    const loading = Utils.showLoading();
    try {
      const compra = await API.get(`compras/${id}/`);
      const body = document.getElementById('detalleCompraBody');
      const detalles = compra.detalles || [];
      const docStr = compra.serie_comprobante ? `${compra.serie_comprobante}-${compra.numero_comprobante || ''}` : `N° ${compra.id}`;
      let html = `
      <div class="card p-3 bg-light border-0 mb-3">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px">
          <span class="fw-bold">Documento:</span>
          <span><span class="badge bg-primary me-1">${compra.tipo_comprobante || 'FACTURA'}</span> ${Utils.escapeHtml(docStr)}</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:4px">
          <span class="fw-bold">Proveedor:</span>
          <span>${Utils.escapeHtml(compra.proveedor ? (compra.proveedor.nombre || compra.proveedor) : 'N/A')}</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:4px">
          <span class="fw-bold">Fecha Recepción:</span>
          <span>${Utils.formatDate(compra.fecha)}</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:4px">
          <span class="fw-bold">Registrado Por:</span>
          <span>${Utils.escapeHtml(compra.usuario ? compra.usuario.username : 'Sistema')}</span>
        </div>
        ${compra.observaciones ? `<div style="display:flex;justify-content:space-between;margin-bottom:4px"><span class="fw-bold">Notas:</span><span>${Utils.escapeHtml(compra.observaciones)}</span></div>` : ''}
        <div style="display:flex;justify-content:space-between;font-weight:700;font-size:1.25rem;margin-top:8px;padding-top:8px;border-top:1px solid var(--border)">
          <span>Total Inversión:</span>
          <span class="text-success">${Utils.formatMoney(compra.total)}</span>
        </div>
      </div>
      <h6 style="font-weight:600;margin-bottom:8px"><i class="fas fa-boxes me-2 text-warning"></i>Productos Reabastecidos</h6>
      <div class="table-container card-flush" style="border:1px solid var(--border)">
        <table class="table table-sm align-middle" style="font-size:.85rem">
          <thead><tr><th>Producto</th><th class="text-end">Cantidad</th><th class="text-end">P. Costo</th><th class="text-end">Vencimiento Lote</th><th class="text-end">Subtotal</th></tr></thead>
          <tbody>`;
      detalles.forEach(d => {
        html += `<tr>
          <td data-label="Producto" class="fw-bold">${Utils.escapeHtml(d.producto ? d.producto.nombre : d.producto_nombre || '')}</td>
          <td data-label="Cantidad" class="text-end fw-bold">${d.cantidad}</td>
          <td data-label="P. Costo" class="text-end">${Utils.formatMoney(d.precio_costo_unitario)}</td>
          <td data-label="Vencimiento" class="text-end">${d.fecha_vencimiento ? Utils.formatDate(d.fecha_vencimiento) : '<span class="text-muted">Sin Venc.</span>'}</td>
          <td data-label="Subtotal" class="text-end fw-bold text-primary">${Utils.formatMoney(d.subtotal || d.cantidad * d.precio_costo_unitario)}</td>
        </tr>`;
      });
      html += `</tbody></table></div>
      <div class="text-end mt-3">
        <button class="btn btn-outline-primary btn-sm" onclick="window.print()"><i class="fas fa-print me-1"></i>Imprimir Guía de Recepción</button>
      </div>`;
      body.innerHTML = html;
      Utils.showModal('detalleCompraModal');
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'danger');
    } finally {
      loading.close();
    }
  }
};

