const ProductosPage = {
  currentPage: 1,
  searchTerm: '',
  categoriaFilter: '',
  stockStatusFilter: '',
  currentProductoId: null,

  render: async function (container) {
    const isAdmin = Auth.isAdmin();
    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-box text-gradient"></i>Productos</h3>
        <div class="page-actions">
          ${isAdmin ? '<button class="btn btn-primary btn-sm btn-pill" id="btnNuevoProducto"><i class="fas fa-plus"></i>Nuevo</button>' : ''}
          ${isAdmin ? '<button class="btn btn-ghost btn-sm" id="btnImportarProductos"><i class="fas fa-file-import"></i>Importar</button>' : ''}
          ${isAdmin ? '<button class="btn btn-success btn-sm" id="btnExportarProductos"><i class="fas fa-file-excel"></i>Exportar Excel</button>' : ''}
          ${isAdmin ? '<button class="btn btn-accent btn-sm" id="btnKardex"><i class="fas fa-book"></i>Kardex</button>' : ''}
        </div>
      </div>

      <div class="filters-bar">
        <div class="search-bar" style="flex:1;min-width:200px">
          <i class="fas fa-search search-icon"></i>
          <input type="text" class="form-control" id="searchProducto" placeholder="Buscar por nombre o código de barras..." value="${this.searchTerm}">
        </div>
        <div class="filter-group">
          <label>Categoría</label>
          <select class="form-select form-select-sm" id="filterCategoria">
            <option value="">Todas</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Stock</label>
          <select class="form-select form-select-sm" id="filterStockStatus">
            <option value="">Todos</option>
            <option value="bajo">Stock Bajo</option>
            <option value="sin_stock">Sin Stock</option>
            <option value="normal">Con Stock</option>
          </select>
        </div>
        <button class="btn btn-primary" id="btnSearchProducto"><i class="fas fa-search"></i></button>
        <div class="filter-group" style="align-self:flex-end">
          <button class="btn btn-ghost btn-sm" id="btnLimpiarFiltrosProducto"><i class="fas fa-undo"></i>Limpiar</button>
        </div>
      </div>

      <div class="table-container" style="margin-top:1rem">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th style="width:55px">Imagen</th>
                <th>Nombre</th>
                <th class="text-center">Código Barras</th>
                <th class="text-center">Categoría</th>
                <th class="text-center">U.M.</th>
                <th class="text-center">Stock</th>
                <th class="text-center">Stock Mín</th>
                <th>Precio</th>
                <th>Costo</th>
                ${isAdmin ? '<th class="text-center" style="width:180px">Acciones</th>' : ''}
              </tr>
            </thead>
            <tbody id="tbodyProductos">
              <tr><td colspan="${isAdmin ? 10 : 9}" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>
            </tbody>
          </table>
        </div>
      </div>
      <div id="paginationProductos" class="d-flex justify-content-center mt-3"></div>

      <!-- Modal Producto -->
      <div class="modal-overlay" id="modalProducto">
        <div class="modal-card" style="max-width:640px">
          <div class="modal-card-header">
            <h5 id="modalProductoTitle">Nuevo Producto</h5>
            <button class="modal-close" onclick="Utils.hideModal('modalProducto')"><i class="fas fa-times"></i></button>
          </div>
          <div class="modal-card-body">
            <form id="formProducto">
              <div class="row g-3">
                <div class="col-md-6">
                  <div class="form-group">
                    <label class="form-label">Nombre <span class="text-danger">*</span></label>
                    <input type="text" class="form-control" name="nombre" placeholder="Ej: Leche Gloria 1L" required>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-group">
                    <label class="form-label">Código de Barras</label>
                    <input type="text" class="form-control" name="codigo_barras" placeholder="Ej: 7750123456789">
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-group">
                    <label class="form-label">Categoría</label>
                    <select class="form-select" name="categoria" id="selectCategoria">
                      <option value="">Seleccione categoría...</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-group">
                    <label class="form-label">Unidad de Medida <span class="text-danger">*</span></label>
                    <select class="form-select" name="unidad_medida">
                      <option value="UNIDAD">Unidad (UND) — productos contables</option>
                      <option value="KILOGRAMO">Kilogramo (KG) — peso</option>
                      <option value="LITRO">Litro (LT) — líquidos</option>
                      <option value="CAJA">Caja (CAJ) — por empaque</option>
                      <option value="BOLSA">Bolsa (BOL) — por empaque</option>
                      <option value="PAQUETE">Paquete (PAQ) — por empaque</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="form-group">
                    <label class="form-label">Precio de Venta <span class="text-danger">*</span></label>
                    <input type="number" step="0.01" class="form-control" name="precio" placeholder="0.00" required>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="form-group">
                    <label class="form-label">Costo <span class="text-danger">*</span></label>
                    <input type="number" step="0.01" class="form-control" name="costo" placeholder="0.00" required>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="form-group">
                    <label class="form-label">Stock Mínimo</label>
                    <input type="number" class="form-control" name="stock_minimo" value="0" placeholder="0">
                  </div>
                </div>
                <div class="col-12">
                  <div class="form-group">
                    <label class="form-label">Imagen</label>
                    <input type="file" class="form-control" name="imagen" accept="image/*" style="padding-top:0.45rem;padding-bottom:0.45rem">
                    <div id="imagenPreview" class="mt-2"></div>
                  </div>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-card-footer">
            <button class="btn btn-ghost" onclick="Utils.hideModal('modalProducto')">Cancelar</button>
            <button class="btn btn-primary" id="btnGuardarProducto"><i class="fas fa-save"></i>Guardar</button>
          </div>
        </div>
      </div>

      <!-- Modal Ajuste Stock -->
      <div class="modal-overlay" id="modalAjuste">
        <div class="modal-card">
          <div class="modal-card-header">
            <h5>Ajustar Stock</h5>
            <button class="modal-close" onclick="Utils.hideModal('modalAjuste')"><i class="fas fa-times"></i></button>
          </div>
          <div class="modal-card-body">
            <form id="formAjuste">
              <div class="form-group">
                <label class="form-label">Producto</label>
                <p style="font-weight:600;margin:0" id="ajusteProductoNombre"></p>
              </div>
              <div class="row g-3">
                <div class="col-md-6">
                  <div class="form-group">
                    <label class="form-label">Tipo <span class="text-danger">*</span></label>
                    <select class="form-select" name="tipo" id="ajusteTipo">
                      <option value="SUMAR">Sumar (+)</option>
                      <option value="RESTAR">Restar (-)</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="form-group">
                    <label class="form-label">Cantidad <span class="text-danger">*</span></label>
                    <input type="number" class="form-control" name="cantidad" min="1" placeholder="Ej: 5" required>
                  </div>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Motivo <span class="text-danger">*</span></label>
                <textarea class="form-control" name="motivo" rows="2" placeholder="Ej: Producto dañado en almacén, Error en inventario, Devolución de cliente..." required></textarea>
              </div>
              <div class="form-group">
                <label class="form-label">Fecha de Vencimiento</label>
                <input type="date" class="form-control" name="fecha_vencimiento">
              </div>
            </form>
          </div>
          <div class="modal-card-footer">
            <button class="btn btn-ghost" onclick="Utils.hideModal('modalAjuste')">Cancelar</button>
            <button class="btn btn-warning" id="btnGuardarAjuste"><i class="fas fa-check"></i>Ajustar</button>
          </div>
        </div>
      </div>

      <!-- Modal Importar -->
      <div class="modal-overlay" id="modalImportar">
        <div class="modal-card">
          <div class="modal-card-header">
            <h5>Importar Productos</h5>
            <button class="modal-close" onclick="Utils.hideModal('modalImportar')"><i class="fas fa-times"></i></button>
          </div>
          <div class="modal-card-body">
            <form id="formImportar">
              <div class="form-group">
                <label class="form-label">Archivo Excel (.xlsx) <span class="text-danger">*</span></label>
                <input type="file" class="form-control" name="archivo" accept=".xlsx,.xls" required style="padding-top:0.45rem;padding-bottom:0.45rem">
              </div>
            </form>
          </div>
          <div class="modal-card-footer">
            <button class="btn btn-ghost" onclick="Utils.hideModal('modalImportar')">Cancelar</button>
            <button class="btn btn-primary" id="btnImportarEnviar"><i class="fas fa-upload"></i>Importar</button>
          </div>
        </div>
      </div>
    `;

    await this.loadFiltrosCategoria();
    await this.loadProductos();
    this.bindEvents(container);
  },

  bindEvents: function (container) {
    const searchInput = document.getElementById('searchProducto');
    const btnSearch = document.getElementById('btnSearchProducto');
    const filterCategoria = document.getElementById('filterCategoria');
    const filterStockStatus = document.getElementById('filterStockStatus');
    const btnLimpiar = document.getElementById('btnLimpiarFiltrosProducto');

    const loadWithFilters = () => {
      this.searchTerm = searchInput ? searchInput.value.trim() : '';
      this.categoriaFilter = filterCategoria ? filterCategoria.value : '';
      this.stockStatusFilter = filterStockStatus ? filterStockStatus.value : '';
      this.currentPage = 1;
      this.loadProductos();
    };

    if (btnSearch) {
      btnSearch.addEventListener('click', loadWithFilters);
    }
    let searchTimer;
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(loadWithFilters, 300);
      });
    }

    if (filterCategoria) {
      filterCategoria.addEventListener('change', loadWithFilters);
    }
    if (filterStockStatus) {
      filterStockStatus.addEventListener('change', loadWithFilters);
    }

    if (btnLimpiar) {
      btnLimpiar.addEventListener('click', () => {
        if (searchInput) searchInput.value = '';
        if (filterCategoria) filterCategoria.value = '';
        if (filterStockStatus) filterStockStatus.value = '';
        this.searchTerm = '';
        this.categoriaFilter = '';
        this.stockStatusFilter = '';
        this.currentPage = 1;
        this.loadProductos();
      });
    }

    const btnNuevo = document.getElementById('btnNuevoProducto');
    if (btnNuevo) btnNuevo.addEventListener('click', () => this.openCreateModal());
    const btnKardex = document.getElementById('btnKardex');
    if (btnKardex) btnKardex.addEventListener('click', () => { window.location.hash = '#/kardex'; });
    const btnImportar = document.getElementById('btnImportarProductos');
    if (btnImportar) {
      btnImportar.addEventListener('click', () => {
        Utils.showModal('modalImportar');
      });
    }
    const btnExportar = document.getElementById('btnExportarProductos');
    if (btnExportar) {
      btnExportar.addEventListener('click', async () => {
        try {
          const response = await fetch(API.baseURL + 'productos/exportar/', {
            headers: { 'Authorization': 'Bearer ' + localStorage.getItem('access_token') }
          });
          if (!response.ok) throw new Error('Error al exportar');
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `productos_${new Date().toISOString().split('T')[0]}.xlsx`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
        } catch (e) {
          Utils.showToast('Error al exportar: ' + e.message, 'error');
        }
      });
    }
    const btnImportarEnviar = document.getElementById('btnImportarEnviar');
    if (btnImportarEnviar) btnImportarEnviar.addEventListener('click', () => this.importarProductos());
    const btnGuardar = document.getElementById('btnGuardarProducto');
    if (btnGuardar) btnGuardar.addEventListener('click', () => this.guardarProducto());
    const btnGuardarAjuste = document.getElementById('btnGuardarAjuste');
    if (btnGuardarAjuste) btnGuardarAjuste.addEventListener('click', () => this.guardarAjuste());

    container.addEventListener('click', async (e) => {
      const btn = e.target.closest('button');
      if (!btn) return;
      const action = btn.dataset.action;
      const id = btn.dataset.id;

      if (action === 'editar') {
        await this.openEditModal(id);
      } else if (action === 'eliminar') {
        this.confirmarEliminar(id, btn.dataset.nombre);
      } else if (action === 'ajustar') {
        this.openAjusteModal(id, btn.dataset.nombre);
      }
    });
  },

  loadFiltrosCategoria: async function () {
    try {
      const data = await API.get('categorias/');
      const categorias = data.results || data || [];
      const select = document.getElementById('filterCategoria');
      if (!select) return;
      select.innerHTML = '<option value="">Todas</option>';
      categorias.forEach(c => {
        select.innerHTML += `<option value="${c.id}">${c.nombre}</option>`;
      });
    } catch (e) {
      console.error('Error cargando categorías para filtro', e);
    }
  },

  loadCategorias: async function () {
    try {
      const data = await API.get('categorias/');
      const categorias = data.results || data || [];
      const select = document.getElementById('selectCategoria');
      if (!select) return;
      select.innerHTML = '<option value="">Seleccione categoría...</option>';
      categorias.forEach(c => {
        select.innerHTML += `<option value="${c.id}">${c.nombre}</option>`;
      });
    } catch (e) {
      console.error('Error cargando categorías', e);
    }
  },

  loadProductos: async function () {
    const tbody = document.getElementById('tbodyProductos');
    const isAdmin = Auth.isAdmin();
    tbody.innerHTML = `<tr><td colspan="${isAdmin ? 10 : 9}" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>`;

    try {
      let url = `productos/?page=${this.currentPage}`;
      if (this.searchTerm) url += `&search=${encodeURIComponent(this.searchTerm)}`;
      if (this.categoriaFilter) url += `&categoria=${this.categoriaFilter}`;
      if (this.stockStatusFilter) url += `&stock_status=${this.stockStatusFilter}`;

      const data = await API.get(url);
      const productos = data.results || [];
      this.renderProductos(productos);
      Utils.renderPagination(data, 'paginationProductos', this.currentPage, (page) => {
        this.currentPage = page;
        this.loadProductos();
      });
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="${isAdmin ? 10 : 9}" class="text-center py-4" style="color:var(--danger)">Error al cargar productos: ${e.message}</td></tr>`;
    }
  },

  renderProductos: function (productos) {
    const tbody = document.getElementById('tbodyProductos');
    const isAdmin = Auth.isAdmin();
    if (!productos.length) {
      tbody.innerHTML = `<tr><td colspan="${isAdmin ? 10 : 9}"><div class="empty-state"><div class="empty-icon"><i class="fas fa-box"></i></div><div class="empty-title">No hay productos registrados</div><div class="empty-desc">Haga clic en "Nuevo" para agregar el primer producto</div></div></td></tr>`;
      return;
    }

    const umLabels = { UNIDAD: 'Und', KILOGRAMO: 'Kg', LITRO: 'Lt', CAJA: 'Cja', BOLSA: 'Bsa', PAQUETE: 'Pqte' };

    tbody.innerHTML = productos.map(p => {
      const stock = parseFloat(p.stock) || 0;
      const stockMin = parseFloat(p.stock_minimo) || 0;
      const outOfStock = stock <= 0;
      const lowStock = stock < stockMin;
      const stockBadgeClass = outOfStock ? 'badge-danger' : (lowStock ? 'badge-warning' : 'badge-success');
      
      const imgUrl = p.imagen ? (typeof p.imagen === 'string' ? p.imagen : p.imagen.url || '') : null;
      return `<tr>
        <td data-label="Imagen">
          ${imgUrl
            ? `<img src="${imgUrl}" alt="" style="width:40px;height:40px;object-fit:cover;border-radius:8px;">`
            : '<div style="width:40px;height:40px;border-radius:8px;background:var(--surface-hover);display:flex;align-items:center;justify-content:center;color:var(--text-muted)"><i class="fas fa-box opacity-50"></i></div>'}
        </td>
        <td data-label="Nombre"><div style="font-weight:600">${p.nombre}</div></td>
        <td data-label="Código Barras" class="text-center"><small style="color:var(--text-muted)">${p.codigo_barras || '---'}</small></td>
        <td data-label="Categoría" class="text-center"><span class="badge badge-accent">${p.categoria ? p.categoria.nombre : 'Sin categoría'}</span></td>
        <td data-label="U.M." class="text-center">${umLabels[p.unidad_medida] || p.unidad_medida || 'Und'}</td>
        <td data-label="Stock" class="text-center"><span class="badge ${stockBadgeClass}">${p.stock}</span></td>
        <td data-label="Stock Mín" class="text-center"><small style="color:var(--text-muted)">${p.stock_minimo}</small></td>
        <td data-label="Precio">${Utils.formatMoney(p.precio)}</td>
        <td data-label="Costo">${Utils.formatMoney(p.costo)}</td>
        ${isAdmin ? `
        <td data-label="Acciones" class="text-center">
          <div style="display:flex;gap:4px;justify-content:center">
            <button class="btn btn-sm btn-icon btn-ghost" data-action="ajustar" data-id="${p.id}" data-nombre="${p.nombre}" title="Ajustar Stock" style="color:var(--warning)"><i class="fas fa-tools"></i></button>
            <button class="btn btn-sm btn-icon btn-ghost" data-action="editar" data-id="${p.id}" title="Editar" style="color:var(--accent)"><i class="fas fa-edit"></i></button>
            <button class="btn btn-sm btn-icon btn-ghost" data-action="eliminar" data-id="${p.id}" data-nombre="${p.nombre}" title="Eliminar" style="color:var(--danger)"><i class="fas fa-trash-alt"></i></button>
          </div>
        </td>` : ''}
      </tr>`;
    }).join('');
  },

  openCreateModal: async function () {
    this.currentProductoId = null;
    document.getElementById('modalProductoTitle').textContent = 'Nuevo Producto';
    document.getElementById('formProducto').reset();
    document.getElementById('imagenPreview').innerHTML = '';
    await this.loadCategorias();
    Utils.showModal('modalProducto');
  },

  openEditModal: async function (id) {
    this.currentProductoId = id;
    document.getElementById('modalProductoTitle').textContent = 'Editar Producto';
    document.getElementById('imagenPreview').innerHTML = '';
    await this.loadCategorias();

    try {
      const p = await API.get(`productos/${id}/`);
      const form = document.getElementById('formProducto');
      form.nombre.value = p.nombre || '';
      form.codigo_barras.value = p.codigo_barras || '';
      form.categoria.value = p.categoria ? p.categoria.id : '';
      form.unidad_medida.value = p.unidad_medida || 'UNIDAD';
      form.precio.value = p.precio || '';
      form.costo.value = p.costo || '';
      form.stock_minimo.value = p.stock_minimo || 0;

      const preview = document.getElementById('imagenPreview');
      if (p.imagen) {
        const imgUrl = typeof p.imagen === 'string' ? p.imagen : p.imagen.url || '';
        if (imgUrl) preview.innerHTML = `<img src="${imgUrl}" style="max-height:80px;border-radius:8px;">`;
      }

      Utils.showModal('modalProducto');
    } catch (e) {
      Utils.showToast('Error al cargar producto: ' + e.message, 'error');
    }
  },

  guardarProducto: async function () {
    const form = document.getElementById('formProducto');
    const nombre = form.nombre.value.trim();
    const precio = parseFloat(form.precio.value);
    const costo = parseFloat(form.costo.value);

    if (!nombre) { Utils.showToast('El nombre del producto es obligatorio', 'warning'); return; }
    if (!precio || precio <= 0) { Utils.showToast('El precio debe ser mayor a 0', 'warning'); return; }
    if (!costo || costo < 0) { Utils.showToast('El costo debe ser mayor o igual a 0', 'warning'); return; }
    if (costo > precio) { Utils.showToast('El costo no puede ser mayor al precio de venta', 'warning'); return; }

    const data = new FormData(form);
    const isEdit = !!this.currentProductoId;
    const btn = document.getElementById('btnGuardarProducto');
    btn.disabled = true;

    if (!data.get('categoria') || data.get('categoria') === '') {
      data.delete('categoria');
    }
    const imagen = data.get('imagen');
    if (imagen && imagen.size === 0) {
      data.delete('imagen');
    }

    try {
      if (isEdit) {
        await API.request('PATCH', `productos/${this.currentProductoId}/`, data, true);
      } else {
        await API.upload('productos/', data);
      }
      Utils.showToast(isEdit ? 'Producto actualizado' : 'Producto creado', 'success');
      Utils.hideModal('modalProducto');
      this.loadProductos();
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'error');
    } finally {
      btn.disabled = false;
    }
  },

  confirmarEliminar: function (id, nombre) {
    Utils.showConfirm('¿Eliminar Producto?', `Se eliminará '${nombre}'. Esta acción no se puede deshacer.`)
      .then(async (result) => {
        if (result.isConfirmed) {
          try {
            await API.delete(`productos/${id}/`);
            Utils.showToast('Producto eliminado', 'success');
            this.loadProductos();
          } catch (e) {
            Utils.showToast('Error: ' + e.message, 'error');
          }
        }
      });
  },

  openAjusteModal: function (id, nombre) {
    document.getElementById('ajusteProductoNombre').textContent = nombre;
    document.getElementById('formAjuste').reset();
    document.getElementById('ajusteTipo').value = 'SUMAR';
    document.getElementById('btnGuardarAjuste').dataset.id = id;
    Utils.showModal('modalAjuste');
  },

  guardarAjuste: async function () {
    const id = document.getElementById('btnGuardarAjuste').dataset.id;
    if (!id) { Utils.showToast('Error: producto no identificado', 'warning'); return; }

    const form = document.getElementById('formAjuste');
    const cantidad = parseInt(form.cantidad.value);
    const motivo = form.motivo.value.trim();

    if (!cantidad || cantidad <= 0) { Utils.showToast('La cantidad debe ser mayor a 0', 'warning'); return; }
    if (!motivo) { Utils.showToast('El motivo es obligatorio', 'warning'); return; }

    const data = {
      tipo: form.tipo.value,
      cantidad,
      motivo,
    };
    const fv = form.fecha_vencimiento.value;
    if (fv) data.fecha_vencimiento = fv;

    const btn = document.getElementById('btnGuardarAjuste');
    btn.disabled = true;

    try {
      await API.post(`productos/${id}/ajustar/`, data);
      Utils.showToast('Stock ajustado correctamente', 'success');
      Utils.hideModal('modalAjuste');
      this.loadProductos();
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'error');
    } finally {
      btn.disabled = false;
    }
  },

  importarProductos: async function () {
    const form = document.getElementById('formImportar');
    const file = form.archivo.files[0];
    if (!file) { Utils.showToast('Seleccione un archivo', 'warning'); return; }

    const fd = new FormData();
    fd.append('archivo', file);
    const btn = document.getElementById('btnImportarEnviar');
    btn.disabled = true;

    try {
      await API.upload('productos/importar/', fd);
      Utils.showToast('Productos importados correctamente', 'success');
      Utils.hideModal('modalImportar');
      this.loadProductos();
    } catch (e) {
      Utils.showToast('Error al importar: ' + e.message, 'error');
    } finally {
      btn.disabled = false;
    }
  }
};
