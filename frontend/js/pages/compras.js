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
        <h3><i class="fas fa-truck text-gradient"></i>Compras</h3>
        <div class="page-actions">
          <button class="btn btn-primary btn-sm btn-pill" id="btnNuevaCompra"><i class="fas fa-plus"></i>Nueva Compra</button>
        </div>
      </div>

      <div class="filters-bar">
        <div class="filter-group">
          <label>Proveedor</label>
          <select id="filterCompraProveedor" class="form-select form-select-sm" style="min-width:180px">
            <option value="">Todos</option>
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
          <input type="text" id="filterCompraQ" class="form-control form-control-sm" placeholder="ID, proveedor o producto...">
        </div>
        <div class="filter-group" style="align-self:flex-end">
          <button class="btn btn-ghost btn-sm" id="btnLimpiarFiltrosCompra"><i class="fas fa-undo"></i>Limpiar</button>
        </div>
      </div>

      <div class="table-container">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>#</th>
                <th>Proveedor</th>
                <th>Fecha</th>
                <th class="text-end">Total</th>
                <th class="text-center" style="width:80px">Acción</th>
              </tr>
            </thead>
            <tbody id="comprasTableBody">
              <tr><td colspan="5" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>
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
      <div class="modal-card" style="max-width:820px">
        <div class="modal-card-header">
          <h5><i class="fas fa-truck me-2"></i>Nueva Compra</h5>
          <button class="modal-close" onclick="Utils.hideModal('compraModal')"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-card-body">
          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label">Proveedor <span class="text-danger">*</span></label>
                <select id="compra_proveedor" placeholder="Buscar proveedor..."></select>
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label">Fecha <span class="text-danger">*</span></label>
                <input type="date" class="form-control" id="compra_fecha">
              </div>
            </div>
          </div>
          <h6 style="font-weight:600;margin-bottom:12px"><i class="fas fa-box me-2"></i>Productos</h6>
          <div id="compraProductos"></div>
          <button class="btn btn-ghost btn-sm" id="btnAgregarProducto" style="margin-top:8px"><i class="fas fa-plus"></i>Agregar Producto</button>
          <hr>
          <div class="d-flex justify-content-between" style="font-size:1.25rem;font-weight:700">
            <span>Total:</span>
            <span id="compraTotal">S/ 0.00</span>
          </div>
        </div>
        <div class="modal-card-footer">
          <button class="btn btn-ghost" onclick="Utils.hideModal('compraModal')">Cancelar</button>
          <button class="btn btn-primary" id="btnGuardarCompra">Registrar Compra</button>
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
      this.renderTabla(data.results || []);
      Utils.renderPagination(data, 'comprasPagination', this.currentPage, (p) => this.cargarCompras(p));
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="5" class="text-center py-4" style="color:var(--danger)">Error: ${e.message}</td></tr>`;
    }
  },

  renderTabla: function(compras) {
    const tbody = document.getElementById('comprasTableBody');
    if (!compras || compras.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5"><div class="empty-state"><div class="empty-icon"><i class="fas fa-truck"></i></div><div class="empty-title">No hay compras registradas</div></div></td></tr>`;
      return;
    }
    let html = '';
    compras.forEach(c => {
      html += `
      <tr>
        <td data-label="#" style="font-weight:500">${c.id}</td>
        <td data-label="Proveedor">${c.proveedor ? (c.proveedor.nombre || c.proveedor) : '-'}</td>
        <td data-label="Fecha">${Utils.formatDate(c.fecha)}</td>
        <td data-label="Total" class="text-end fw-bold">${Utils.formatMoney(c.total)}</td>
        <td data-label="Acción" class="text-center">
          <button class="btn btn-sm btn-icon btn-ghost btn-ver-compra" data-id="${c.id}" style="color:var(--accent)"><i class="fas fa-eye"></i></button>
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

    // Initialize Provider TomSelect with Remote Search
    this.tomSelects['proveedor'] = new TomSelect('#compra_proveedor', {
      valueField: 'id',
      labelField: 'nombre',
      searchField: 'nombre',
      load: async (query, callback) => {
        try {
          const data = await API.get(`proveedores/?search=${encodeURIComponent(query)}`);
          callback(data.results || data);
        } catch (e) { callback(); }
      },
      placeholder: 'Buscar proveedor...',
      create: false
    });

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
    
    // Initialize Product TomSelect with Remote Search
    const ts = new TomSelect(`#prod_select_${index}`, {
      valueField: 'id',
      labelField: 'nombre',
      searchField: 'nombre',
      load: async (query, callback) => {
        try {
          const data = await API.get(`productos/?search=${encodeURIComponent(query)}`);
          callback(data.results || data);
        } catch (e) { callback(); }
      },
      placeholder: 'Buscar producto...',
      create: false,
      onChange: async (val) => {
        if (!val) return;
        const item = document.querySelector(`.compra-item[data-index="${index}"]`);
        const precioInput = item.querySelector('.precio-input');
        // Fetch full product details to get current cost
        try {
          const p = await API.get(`productos/${val}/detalle/`);
          if (precioInput) precioInput.value = p.costo || 0;
          this.calcularTotal();
        } catch (e) {}
      }
    });

    this.tomSelects[`prod_${index}`] = ts;
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
      await API.post('compras/', { proveedor_id, fecha, detalles });
      Utils.showToast('Compra registrada correctamente', 'success');
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
      let html = `
      <div class="mb-3">
        <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="font-weight:600">Proveedor:</span><span>${compra.proveedor ? (compra.proveedor.nombre || compra.proveedor) : '-'}</span></div>
        <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="font-weight:600">Fecha:</span><span>${Utils.formatDate(compra.fecha)}</span></div>
        <div style="display:flex;justify-content:space-between;font-weight:700;font-size:1.2rem;margin-top:8px;padding-top:8px;border-top:1px solid var(--border)"><span>Total:</span><span>${Utils.formatMoney(compra.total)}</span></div>
      </div>
      <h6 style="font-weight:600;margin-bottom:8px">Productos</h6>
      <div class="table-container card-flush" style="border:1px solid var(--border)">
        <table class="table table-sm" style="font-size:.82rem">
          <thead><tr><th>Producto</th><th class="text-end">Cantidad</th><th class="text-end">P. Costo</th><th class="text-end">Vencimiento</th><th class="text-end">Subtotal</th></tr></thead>
          <tbody>`;
      detalles.forEach(d => {
        html += `<tr>
          <td data-label="Producto">${d.producto ? d.producto.nombre : d.producto_nombre || ''}</td>
          <td data-label="Cantidad" class="text-end">${d.cantidad}</td>
          <td data-label="P. Costo" class="text-end">${Utils.formatMoney(d.precio_costo_unitario)}</td>
          <td data-label="Vencimiento" class="text-end">${d.fecha_vencimiento ? Utils.formatDate(d.fecha_vencimiento) : '-'}</td>
          <td data-label="Subtotal" class="text-end fw-bold">${Utils.formatMoney(d.subtotal || d.cantidad * d.precio_costo_unitario)}</td>
        </tr>`;
      });
      html += '</tbody></table></div>';
      body.innerHTML = html;
      Utils.showModal('detalleCompraModal');
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'danger');
    } finally {
      loading.close();
    }
  }
};
