const ProveedoresPage = {
  searchTerm: '',
  currentPage: 1,

  render: async function(container) {
    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-truck-field text-gradient"></i>Proveedores</h3>
        <div class="page-actions">
          <button class="btn btn-primary btn-sm btn-pill" id="btnNuevoProveedor"><i class="fas fa-plus"></i>Nuevo Proveedor</button>
        </div>
      </div>

      <div class="filters-bar">
        <div class="search-bar" style="flex:1;min-width:200px">
          <i class="fas fa-search search-icon"></i>
          <input type="text" class="form-control" id="searchProveedor" placeholder="Buscar por nombre o RUC..." value="${this.searchTerm}">
        </div>
        <div class="filter-group" style="align-self:flex-end">
          <button class="btn btn-ghost btn-sm" id="btnLimpiarFiltrosProveedor"><i class="fas fa-undo"></i>Limpiar</button>
        </div>
      </div>

      <div class="table-container">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>RUC</th>
                <th>Teléfono</th>
                <th>Email</th>
                <th>Dirección</th>
                <th class="text-center" style="width:100px">Acciones</th>
              </tr>
            </thead>
            <tbody id="proveedoresTableBody">
              <tr><td colspan="6" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>
            </tbody>
          </table>
        </div>
        <div id="proveedoresPagination" class="py-3"></div>
      </div>
      ${this.modalFormHTML()}`;
    this.bindEvents();
    await this.cargarProveedores();
  },

  modalFormHTML: function() {
    return `
    <div class="modal-overlay" id="proveedorModal">
      <div class="modal-card" style="max-width:500px">
        <div class="modal-card-header">
          <h5 id="proveedorModalTitle"><i class="fas fa-truck-field me-2"></i>Nuevo Proveedor</h5>
          <button class="modal-close" onclick="Utils.hideModal('proveedorModal')"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-card-body">
          <input type="hidden" id="proveedor_id">
          <div class="form-group">
            <label class="form-label">Nombre <span class="text-danger">*</span></label>
            <input type="text" class="form-control" id="p_nombre" placeholder="Ej: Distribuidora Alimentos SAC" required>
          </div>
          <div class="form-group">
            <label class="form-label">RUC</label>
            <input type="text" class="form-control" id="p_ruc" placeholder="Ej: 20123456789">
          </div>
          <div class="form-group">
            <label class="form-label">Teléfono</label>
            <input type="text" class="form-control" id="p_telefono" placeholder="Ej: 999 888 777">
          </div>
          <div class="form-group">
            <label class="form-label">Email</label>
            <input type="email" class="form-control" id="p_email" placeholder="Ej: contacto@proveedor.com">
          </div>
          <div class="form-group">
            <label class="form-label">Dirección</label>
            <textarea class="form-control" id="p_direccion" placeholder="Ej: Av. Principal 123, Lima" style="min-height:80px"></textarea>
          </div>
        </div>
        <div class="modal-card-footer">
          <button class="btn btn-ghost" onclick="Utils.hideModal('proveedorModal')">Cancelar</button>
          <button class="btn btn-primary" id="btnGuardarProveedor">Guardar</button>
        </div>
      </div>
    </div>`;
  },

  bindEvents: function() {
    const btnNuevoProveedor = document.getElementById('btnNuevoProveedor');
    if (btnNuevoProveedor) {
      btnNuevoProveedor.addEventListener('click', () => {
        this.limpiarModal();
        document.getElementById('proveedorModalTitle').textContent = 'Nuevo Proveedor';
        Utils.showModal('proveedorModal');
      });
    }
    const btnGuardarProveedor = document.getElementById('btnGuardarProveedor');
    if (btnGuardarProveedor) btnGuardarProveedor.addEventListener('click', () => this.guardar());

    const searchInput = document.getElementById('searchProveedor');
    const btnLimpiar = document.getElementById('btnLimpiarFiltrosProveedor');

    const doSearch = () => {
      this.searchTerm = searchInput.value.trim();
      this.currentPage = 1;
      this.cargarProveedores();
    };

    let searchTimer;
    if (searchInput) {
      searchInput.addEventListener('input', () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(doSearch, 300);
      });
    }
    if (btnLimpiar) {
      btnLimpiar.addEventListener('click', () => {
        if (searchInput) searchInput.value = '';
        this.searchTerm = '';
        this.currentPage = 1;
        this.cargarProveedores();
      });
    }
  },

  cargarProveedores: async function(page) {
    const pg = page || this.currentPage;
    this.currentPage = pg;
    const tbody = document.getElementById('proveedoresTableBody');
    try {
      let url = `proveedores/?page=${pg}`;
      if (this.searchTerm) url += `&search=${encodeURIComponent(this.searchTerm)}`;
      const data = await API.get(url);
      this.renderTabla(data.results || []);
      Utils.renderPagination(data, 'proveedoresPagination', this.currentPage, (p) => this.cargarProveedores(p));
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4" style="color:var(--danger)">Error: ${e.message}</td></tr>`;
    }
  },

  renderTabla: function(proveedores) {
    const tbody = document.getElementById('proveedoresTableBody');
    if (!proveedores || proveedores.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><div class="empty-icon"><i class="fas fa-truck-field"></i></div><div class="empty-title">No hay proveedores registrados</div></div></td></tr>`;
      return;
    }
    let html = '';
    proveedores.forEach(p => {
      html += `
      <tr>
        <td data-label="Nombre" style="font-weight:500">${p.nombre}</td>
        <td data-label="RUC">${p.ruc || '-'}</td>
        <td data-label="Teléfono">${p.telefono || '-'}</td>
        <td data-label="Email">${p.email || '-'}</td>
        <td data-label="Dirección">${p.direccion || '-'}</td>
        <td data-label="Acciones" class="text-center">
          <div style="display:flex;gap:4px;justify-content:center">
            <button class="btn btn-sm btn-icon btn-ghost btn-editar-proveedor" data-id="${p.id}" title="Editar" style="color:var(--accent)"><i class="fas fa-edit"></i></button>
            <button class="btn btn-sm btn-icon btn-ghost btn-eliminar-proveedor" data-id="${p.id}" data-name="${p.nombre}" title="Eliminar" style="color:var(--danger)"><i class="fas fa-trash"></i></button>
          </div>
        </td>
      </tr>`;
    });
    tbody.innerHTML = html;

    tbody.querySelectorAll('.btn-editar-proveedor').forEach(btn => {
      btn.addEventListener('click', () => this.editar(btn.dataset.id));
    });
    tbody.querySelectorAll('.btn-eliminar-proveedor').forEach(btn => {
      btn.addEventListener('click', () => this.eliminar(btn.dataset.id, btn.dataset.name));
    });
  },

  limpiarModal: function() {
    document.getElementById('proveedor_id').value = '';
    document.getElementById('p_nombre').value = '';
    document.getElementById('p_ruc').value = '';
    document.getElementById('p_telefono').value = '';
    document.getElementById('p_email').value = '';
    document.getElementById('p_direccion').value = '';
  },

  editar: async function(id) {
    try {
      const p = await API.get(`proveedores/${id}/`);
      document.getElementById('proveedor_id').value = p.id;
      document.getElementById('p_nombre').value = p.nombre;
      document.getElementById('p_ruc').value = p.ruc || '';
      document.getElementById('p_telefono').value = p.telefono || '';
      document.getElementById('p_email').value = p.email || '';
      document.getElementById('p_direccion').value = p.direccion || '';
      document.getElementById('proveedorModalTitle').textContent = 'Editar Proveedor';
      Utils.showModal('proveedorModal');
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'danger');
    }
  },

  guardar: async function() {
    const id = document.getElementById('proveedor_id').value;
    const nombre = document.getElementById('p_nombre').value.trim();
    const ruc = document.getElementById('p_ruc').value.trim();
    const telefono = document.getElementById('p_telefono').value.trim();
    const email = document.getElementById('p_email').value.trim();
    if (!nombre) { Utils.showToast('El nombre es obligatorio', 'warning'); return; }
    if (ruc && !/^\d{11}$/.test(ruc)) { Utils.showToast('El RUC debe tener 11 dígitos numéricos', 'warning'); return; }
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { Utils.showToast('Ingresa un correo electrónico válido', 'warning'); return; }

    const data = { nombre, ruc, telefono, email, direccion: document.getElementById('p_direccion').value };

    try {
      if (id) {
        await API.patch(`proveedores/${id}/`, data);
      } else {
        await API.post('proveedores/', data);
      }
      Utils.showToast(id ? 'Proveedor actualizado' : 'Proveedor creado', 'success');
      Utils.hideModal('proveedorModal');
      this.cargarProveedores();
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'danger');
    }
  },

  eliminar: async function(id, name) {
    const result = await Utils.showConfirm('¿Eliminar proveedor?', `Se eliminará permanentemente a "${name}".`);
    if (!result.isConfirmed) return;
    try {
      await API.delete(`proveedores/${id}/`);
      Utils.showToast('Proveedor eliminado', 'success');
      this.cargarProveedores();
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'danger');
    }
  }
};
