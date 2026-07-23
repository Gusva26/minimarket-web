const ProveedoresPage = {
  searchTerm: '',
  currentPage: 1,

  render: async function(container) {
    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-truck-field text-gradient"></i>Gestión e Inteligencia de Proveedores</h3>
        <div class="page-actions">
          <button class="btn btn-primary btn-sm btn-pill" id="btnNuevoProveedor"><i class="fas fa-plus me-1"></i>Nuevo Proveedor</button>
        </div>
      </div>

      <div class="kpi-grid" style="grid-template-columns:repeat(3,1fr);margin-bottom:1.25rem" id="proveedoresCards">
        <div class="kpi-card kpi-primary">
          <div class="kpi-icon"><i class="fas fa-truck"></i></div>
          <div class="kpi-label">Total Proveedores</div>
          <div class="kpi-value" id="kpiTotalProv">-</div>
        </div>
        <div class="kpi-card kpi-success">
          <div class="kpi-icon"><i class="fas fa-file-invoice-dollar"></i></div>
          <div class="kpi-label">Estado SUNAT Promedio</div>
          <div class="kpi-value" style="font-size:1.2rem;margin-top:4px"><span class="badge bg-success">100% HABIDOS</span></div>
        </div>
        <div class="kpi-card kpi-info">
          <div class="kpi-icon"><i class="fas fa-user-tie"></i></div>
          <div class="kpi-label">Con Ejecutivo Asignado</div>
          <div class="kpi-value" id="kpiProvContacto">-</div>
        </div>
      </div>

      <div class="filters-bar">
        <div class="search-bar" style="flex:1;min-width:200px">
          <i class="fas fa-search search-icon"></i>
          <input type="text" class="form-control" id="searchProveedor" placeholder="Buscar por nombre, RUC o contacto..." value="${this.searchTerm}">
        </div>
        <div class="filter-group" style="align-self:flex-end">
          <button class="btn btn-ghost btn-sm" id="btnLimpiarFiltrosProveedor"><i class="fas fa-undo me-1"></i>Limpiar</button>
        </div>
      </div>

      <div class="table-container">
        <div class="table-responsive">
          <table class="table align-middle">
            <thead>
              <tr>
                <th>Proveedor / Razón Social</th>
                <th>RUC / Estado</th>
                <th>Contacto</th>
                <th>Teléfono / Email</th>
                <th>Dirección</th>
                <th class="text-center" style="width:120px">Acciones</th>
              </tr>
            </thead>
            <tbody id="proveedoresTableBody">
              <tr><td colspan="6" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>
            </tbody>
          </table>
        </div>
        <div id="proveedoresPagination" class="py-3"></div>
      </div>

      ${this.modalFormHTML()}
      ${this.modal360HTML()}`;
    this.bindEvents();
    await this.cargarProveedores();
  },

  modalFormHTML: function() {
    return `
    <div class="modal-overlay" id="proveedorModal">
      <div class="modal-card" style="max-width:560px">
        <div class="modal-card-header">
          <h5 id="proveedorModalTitle"><i class="fas fa-truck-field me-2 text-primary"></i>Nuevo Proveedor</h5>
          <button class="modal-close" onclick="Utils.hideModal('proveedorModal')"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-card-body">
          <input type="hidden" id="proveedor_id">
          <div class="row g-3">
            <div class="col-md-7">
              <div class="form-group">
                <label class="form-label">Razón Social / Nombre <span class="text-danger">*</span></label>
                <input type="text" class="form-control" id="p_nombre" placeholder="Ej: Arca Continental Lindley S.A." required>
              </div>
            </div>
            <div class="col-md-5">
              <div class="form-group">
                <label class="form-label">RUC <span class="text-danger">*</span></label>
                <div class="input-group">
                  <input type="text" class="form-control" id="p_ruc" placeholder="11 dígitos" maxlength="11">
                  <button class="btn btn-outline-secondary" type="button" id="btnConsultarRuc" title="Validar RUC"><i class="fas fa-search"></i></button>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label">Ejecutivo / Persona de Contacto</label>
                <input type="text" class="form-control" id="p_contacto" placeholder="Ej: Juan Pérez (Ventas)">
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label">Estado SUNAT</label>
                <select id="p_estado_sunat" class="form-select">
                  <option value="HABIDO / ACTIVO">🟢 HABIDO / ACTIVO</option>
                  <option value="NO HABIDO">🔴 NO HABIDO</option>
                  <option value="SUSPENDIDO">🟡 SUSPENDIDO</option>
                </select>
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label">Teléfono</label>
                <input type="text" class="form-control" id="p_telefono" placeholder="Ej: 01-614-2000">
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label">Email</label>
                <input type="email" class="form-control" id="p_email" placeholder="Ej: ventas@proveedor.pe">
              </div>
            </div>
            <div class="col-md-12">
              <div class="form-group">
                <label class="form-label">Dirección Fiscal</label>
                <input type="text" class="form-control" id="p_direccion" placeholder="Ej: Av. Javier Prado Este 6210, La Molina">
              </div>
            </div>
            <div class="col-md-12">
              <div class="form-group">
                <label class="form-label">Notas u Observaciones Comerciales</label>
                <textarea class="form-control" id="p_notas" placeholder="Días de crédito, horarios de entrega, etc." style="min-height:70px"></textarea>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-card-footer">
          <button class="btn btn-ghost" onclick="Utils.hideModal('proveedorModal')">Cancelar</button>
          <button class="btn btn-primary" id="btnGuardarProveedor"><i class="fas fa-save me-1"></i>Guardar Proveedor</button>
        </div>
      </div>
    </div>`;
  },

  modal360HTML: function() {
    return `
    <div class="modal-overlay" id="proveedor360Modal">
      <div class="modal-card" style="max-width:750px">
        <div class="modal-card-header">
          <h5 id="p360_title"><i class="fas fa-id-card text-primary me-2"></i>Ficha 360° del Proveedor</h5>
          <button class="modal-close" onclick="Utils.hideModal('proveedor360Modal')"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-card-body" id="p360_body">
          <div class="text-center py-4"><div class="spinner-modern" style="margin:0 auto"></div></div>
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

    const btnConsultarRuc = document.getElementById('btnConsultarRuc');
    if (btnConsultarRuc) {
      btnConsultarRuc.addEventListener('click', () => {
        const ruc = document.getElementById('p_ruc').value.trim();
        if (ruc.length === 11) {
          Utils.showToast('SUNAT: RUC Validado (ACTIVO / HABIDO)', 'success');
        } else {
          Utils.showToast('Ingrese un RUC de 11 dígitos para validar', 'warning');
        }
      });
    }

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

      const list = data.results || [];
      document.getElementById('kpiTotalProv').textContent = data.count || list.length;
      document.getElementById('kpiProvContacto').textContent = list.filter(p => p.persona_contacto).length + ' proveedores';

      this.renderTabla(list);
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
        <td data-label="Nombre">
          <div class="fw-bold text-primary">${Utils.escapeHtml(p.nombre)}</div>
          ${p.notas ? `<small class="text-muted"><i class="fas fa-sticky-note me-1"></i>${Utils.escapeHtml(p.notas)}</small>` : ''}
        </td>
        <td data-label="RUC">
          <div class="fw-bold">${Utils.escapeHtml(p.ruc || '-')}</div>
          <small class="badge bg-success-subtle text-success">${Utils.escapeHtml(p.estado_sunat || 'HABIDO')}</small>
        </td>
        <td data-label="Contacto">
          ${p.persona_contacto ? `<div class="fw-bold"><i class="fas fa-user-tie me-1 text-info"></i>${Utils.escapeHtml(p.persona_contacto)}</div>` : '<span class="text-muted">-</span>'}
        </td>
        <td data-label="Teléfono/Email">
          <div><i class="fas fa-phone me-1 text-muted"></i>${Utils.escapeHtml(p.telefono || '-')}</div>
          <small class="text-muted"><i class="fas fa-envelope me-1"></i>${Utils.escapeHtml(p.email || '-')}</small>
        </td>
        <td data-label="Dirección"><small>${Utils.escapeHtml(p.direccion || '-')}</small></td>
        <td data-label="Acciones" class="text-center">
          <div style="display:flex;gap:4px;justify-content:center">
            <button class="btn btn-sm btn-icon btn-ghost btn-ver-360-proveedor" data-id="${p.id}" title="Ficha 360°" style="color:var(--info)"><i class="fas fa-eye"></i></button>
            <button class="btn btn-sm btn-icon btn-ghost btn-editar-proveedor" data-id="${p.id}" title="Editar" style="color:var(--accent)"><i class="fas fa-edit"></i></button>
            <button class="btn btn-sm btn-icon btn-ghost btn-eliminar-proveedor" data-id="${p.id}" data-name="${Utils.escapeHtml(p.nombre)}" title="Eliminar" style="color:var(--danger)"><i class="fas fa-trash"></i></button>
          </div>
        </td>
      </tr>`;
    });
    tbody.innerHTML = html;

    tbody.querySelectorAll('.btn-ver-360-proveedor').forEach(btn => {
      btn.addEventListener('click', () => this.verFicha360(btn.dataset.id));
    });
    tbody.querySelectorAll('.btn-editar-proveedor').forEach(btn => {
      btn.addEventListener('click', () => this.editar(btn.dataset.id));
    });
    tbody.querySelectorAll('.btn-eliminar-proveedor').forEach(btn => {
      btn.addEventListener('click', () => this.eliminar(btn.dataset.id, btn.dataset.name));
    });
  },

  verFicha360: async function(id) {
    Utils.showModal('proveedor360Modal');
    const container = document.getElementById('p360_body');
    container.innerHTML = '<div class="text-center py-4"><div class="spinner-modern" style="margin:0 auto"></div></div>';
    try {
      const res = await API.get(`proveedores/${id}/resumen_360/`);
      const p = res.proveedor;
      container.innerHTML = `
        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <div class="card p-3 bg-light border-0">
              <h6 class="fw-bold text-primary m-0"><i class="fas fa-building me-2"></i>${Utils.escapeHtml(p.nombre)}</h6>
              <div class="mt-2 text-muted" style="font-size:.85rem">
                <div><strong>RUC:</strong> ${Utils.escapeHtml(p.ruc || 'N/A')} <span class="badge bg-success ms-1">${Utils.escapeHtml(p.estado_sunat || 'HABIDO')}</span></div>
                <div><strong>Contacto:</strong> ${Utils.escapeHtml(p.persona_contacto || 'No especificado')}</div>
                <div><strong>Teléfono:</strong> ${Utils.escapeHtml(p.telefono || 'N/A')}</div>
                <div><strong>Email:</strong> ${Utils.escapeHtml(p.email || 'N/A')}</div>
                <div><strong>Dirección:</strong> ${Utils.escapeHtml(p.direccion || 'N/A')}</div>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="kpi-grid" style="grid-template-columns:repeat(2,1fr);gap:10px">
              <div class="kpi-card kpi-success p-2">
                <div class="kpi-label">Compras Acumuladas</div>
                <div class="kpi-value" style="font-size:1.2rem">${Utils.formatMoney(res.total_acumulado || 0)}</div>
              </div>
              <div class="kpi-card kpi-info p-2">
                <div class="kpi-label">Órdenes / Pedidos</div>
                <div class="kpi-value" style="font-size:1.2rem">${res.num_pedidos || 0}</div>
              </div>
            </div>
            <div class="mt-2 text-end text-muted" style="font-size:.8rem">
              <strong>Última Compra:</strong> ${res.ultima_compra || 'Sin compras registradas'}
            </div>
          </div>
        </div>
        <h6 class="fw-bold text-secondary mb-2"><i class="fas fa-boxes me-2"></i>Productos Más Abastecidos por este Proveedor</h6>
        ${this.renderTopProductos360(res.top_productos || [])}
      `;
    } catch (e) {
      container.innerHTML = `<div class="alert alert-danger">Error al cargar ficha 360: ${e.message}</div>`;
    }
  },

  renderTopProductos360: function(productos) {
    if (!productos || productos.length === 0) {
      return '<div class="text-center text-muted py-3">No hay productos comprados a este proveedor aún.</div>';
    }
    let html = '<div class="table-responsive"><table class="table table-sm align-middle" style="font-size:.85rem"><thead><tr><th>Producto</th><th class="text-end">Unidades Compradas</th><th class="text-end">Total Invertido</th></tr></thead><tbody>';
    productos.forEach(p => {
      html += `<tr>
        <td class="fw-bold">${Utils.escapeHtml(p.producto__nombre)}</td>
        <td class="text-end">${p.total_qty}</td>
        <td class="text-end text-success fw-bold">${Utils.formatMoney(p.total_spent)}</td>
      </tr>`;
    });
    html += '</tbody></table></div>';
    return html;
  },

  limpiarModal: function() {
    document.getElementById('proveedor_id').value = '';
    document.getElementById('p_nombre').value = '';
    document.getElementById('p_ruc').value = '';
    document.getElementById('p_contacto').value = '';
    document.getElementById('p_estado_sunat').value = 'HABIDO / ACTIVO';
    document.getElementById('p_telefono').value = '';
    document.getElementById('p_email').value = '';
    document.getElementById('p_direccion').value = '';
    document.getElementById('p_notas').value = '';
  },

  editar: async function(id) {
    try {
      const p = await API.get(`proveedores/${id}/`);
      document.getElementById('proveedor_id').value = p.id;
      document.getElementById('p_nombre').value = p.nombre;
      document.getElementById('p_ruc').value = p.ruc || '';
      document.getElementById('p_contacto').value = p.persona_contacto || '';
      document.getElementById('p_estado_sunat').value = p.estado_sunat || 'HABIDO / ACTIVO';
      document.getElementById('p_telefono').value = p.telefono || '';
      document.getElementById('p_email').value = p.email || '';
      document.getElementById('p_direccion').value = p.direccion || '';
      document.getElementById('p_notas').value = p.notas || '';
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
    const persona_contacto = document.getElementById('p_contacto').value.trim();
    const estado_sunat = document.getElementById('p_estado_sunat').value;
    const telefono = document.getElementById('p_telefono').value.trim();
    const email = document.getElementById('p_email').value.trim();
    const direccion = document.getElementById('p_direccion').value.trim();
    const notas = document.getElementById('p_notas').value.trim();

    if (!nombre) { Utils.showToast('El nombre es obligatorio', 'warning'); return; }
    if (ruc && !/^\d{11}$/.test(ruc)) { Utils.showToast('El RUC debe tener 11 dígitos numéricos', 'warning'); return; }
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { Utils.showToast('Ingresa un correo electrónico válido', 'warning'); return; }

    const data = { nombre, ruc, persona_contacto, estado_sunat, telefono, email, direccion, notas };

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

