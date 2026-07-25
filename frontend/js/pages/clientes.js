const ClientesPage = {
  searchTerm: '',
  currentPage: 1,

  render: async function(container) {
    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-address-book text-gradient"></i>Gestión de Clientes</h3>
        <div class="page-actions">
          <button class="btn btn-primary btn-sm btn-pill" id="btnNuevoCliente">
            <i class="fas fa-plus me-1"></i>Nuevo Cliente
          </button>
        </div>
      </div>

      <div class="kpi-grid" style="grid-template-columns:repeat(3,1fr);margin-bottom:1.25rem" id="clientesCards">
        <div class="kpi-card kpi-primary">
          <div class="kpi-icon"><i class="fas fa-users"></i></div>
          <div class="kpi-label">Total Clientes</div>
          <div class="kpi-value" id="kpiTotalClientes">-</div>
        </div>
        <div class="kpi-card kpi-info">
          <div class="kpi-icon"><i class="fas fa-id-card"></i></div>
          <div class="kpi-label">Clientes DNI</div>
          <div class="kpi-value" id="kpiClientesDNI">-</div>
        </div>
        <div class="kpi-card kpi-success">
          <div class="kpi-icon"><i class="fas fa-building"></i></div>
          <div class="kpi-label">Clientes RUC (Empresas)</div>
          <div class="kpi-value" id="kpiClientesRUC">-</div>
        </div>
      </div>

      <div class="filters-bar">
        <div class="search-bar" style="flex:1;min-width:220px">
          <i class="fas fa-search search-icon"></i>
          <input type="text" class="form-control" id="searchCliente" placeholder="Buscar por nombre, DNI o RUC..." value="${this.searchTerm}">
        </div>
        <div class="filter-group" style="align-self:flex-end">
          <button class="btn btn-ghost btn-sm" id="btnLimpiarFiltrosCliente"><i class="fas fa-undo me-1"></i>Limpiar</button>
        </div>
      </div>

      <div class="table-container">
        <div class="table-responsive">
          <table class="table align-middle">
            <thead>
              <tr>
                <th>Documento</th>
                <th>Cliente / Razón Social</th>
                <th>Teléfono</th>
                <th>Email</th>
                <th>Dirección</th>
                <th class="text-center" style="width:120px">Acciones</th>
              </tr>
            </thead>
            <tbody id="clientesTableBody">
              <tr>
                <td colspan="6" class="text-center py-4" style="color:var(--text-muted)">
                  <div class="spinner-modern" style="margin:0 auto"></div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div id="clientesPagination" class="py-3"></div>
      </div>

      ${this.modalFormHTML()}
    `;

    this.bindEvents();
    await this.cargarClientes();
  },

  modalFormHTML: function() {
    return `
    <div class="modal-overlay" id="clienteModal">
      <div class="modal-card" style="max-width:540px">
        <div class="modal-card-header">
          <h5 id="clienteModalTitle"><i class="fas fa-user-plus me-2 text-primary"></i>Nuevo Cliente</h5>
          <button class="modal-close" onclick="Utils.hideModal('clienteModal')"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-card-body">
          <input type="hidden" id="c_id">
          <div class="row g-3">
            <div class="col-md-4">
              <div class="form-group">
                <label class="form-label">Tipo Doc. <span class="text-danger">*</span></label>
                <select class="form-select" id="c_tipo_documento">
                  <option value="DNI">DNI</option>
                  <option value="RUC">RUC</option>
                </select>
              </div>
            </div>
            <div class="col-md-8">
              <div class="form-group">
                <label class="form-label">N° Documento <span class="text-danger">*</span></label>
                <div class="input-group">
                  <input type="text" class="form-control" id="c_num_documento" placeholder="Ingrese número" maxlength="11" required>
                  <button class="btn btn-outline-secondary" type="button" id="btnConsultarDoc" title="Buscar en RENIEC / SUNAT">
                    <i class="fas fa-search"></i>
                  </button>
                </div>
              </div>
            </div>
            <div class="col-12">
              <div class="form-group">
                <label class="form-label">Nombre / Razón Social <span class="text-danger">*</span></label>
                <input type="text" class="form-control" id="c_nombre" placeholder="Nombre completo o nombre comercial" required>
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label">Teléfono / Celular</label>
                <input type="text" class="form-control" id="c_telefono" placeholder="Ej: 987654321">
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label">Correo Electrónico</label>
                <input type="email" class="form-control" id="c_email" placeholder="cliente@correo.com">
              </div>
            </div>
            <div class="col-12">
              <div class="form-group">
                <label class="form-label">Dirección</label>
                <input type="text" class="form-control" id="c_direccion" placeholder="Av. Principal #123">
              </div>
            </div>
          </div>
        </div>
        <div class="modal-card-footer">
          <button type="button" class="btn btn-ghost btn-sm" onclick="Utils.hideModal('clienteModal')">Cancelar</button>
          <button type="button" class="btn btn-primary btn-sm btn-pill" id="btnGuardarCliente"><i class="fas fa-save me-1"></i>Guardar Cliente</button>
        </div>
      </div>
    </div>`;
  },

  bindEvents: function() {
    document.getElementById('btnNuevoCliente')?.addEventListener('click', () => this.abrirModal());
    document.getElementById('btnGuardarCliente')?.addEventListener('click', () => this.guardarCliente());
    document.getElementById('btnLimpiarFiltrosCliente')?.addEventListener('click', () => {
      this.searchTerm = '';
      const s = document.getElementById('searchCliente');
      if (s) s.value = '';
      this.currentPage = 1;
      this.cargarClientes();
    });

    const searchInput = document.getElementById('searchCliente');
    if (searchInput) {
      searchInput.addEventListener('input', Utils.debounce(() => {
        this.searchTerm = searchInput.value.trim();
        this.currentPage = 1;
        this.cargarClientes();
      }, 300));
    }

    const docTypeSelect = document.getElementById('c_tipo_documento');
    const numDocInput = document.getElementById('c_num_documento');
    if (docTypeSelect && numDocInput) {
      docTypeSelect.addEventListener('change', () => {
        if (docTypeSelect.value === 'DNI') {
          numDocInput.maxLength = 8;
        } else {
          numDocInput.maxLength = 11;
        }
      });
    }

    document.getElementById('btnConsultarDoc')?.addEventListener('click', () => this.consultarDocumento());
  },

  cargarClientes: async function() {
    const tbody = document.getElementById('clientesTableBody');
    if (!tbody) return;

    try {
      let query = `clientes/?page=${this.currentPage}`;
      if (this.searchTerm) {
        query += `&search=${encodeURIComponent(this.searchTerm)}`;
      }

      const res = await API.get(query);
      const clientes = res.results || res;
      const count = res.count || clientes.length;

      // Actualizar KPIs
      const kpiTotal = document.getElementById('kpiTotalClientes');
      const kpiDni = document.getElementById('kpiClientesDNI');
      const kpiRuc = document.getElementById('kpiClientesRUC');

      if (kpiTotal) kpiTotal.textContent = count;
      if (kpiDni) kpiDni.textContent = clientes.filter(c => c.tipo_documento === 'DNI').length;
      if (kpiRuc) kpiRuc.textContent = clientes.filter(c => c.tipo_documento === 'RUC').length;

      if (!clientes || clientes.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="6" class="text-center py-4" style="color:var(--text-muted)">
              <i class="fas fa-users-slash text-muted mb-2" style="font-size:2rem;display:block"></i>
              No se encontraron clientes registrados.
            </td>
          </tr>`;
        const pag = document.getElementById('clientesPagination');
        if (pag) pag.innerHTML = '';
        return;
      }

      tbody.innerHTML = clientes.map(c => `
        <tr>
          <td>
            <span class="badge ${c.tipo_documento === 'RUC' ? 'bg-primary-subtle text-primary' : 'bg-info-subtle text-info'} fw-bold" style="font-size:0.75rem;padding:4px 8px;border-radius:6px">
              ${c.tipo_documento || 'DNI'}: ${c.num_documento || ''}
            </span>
          </td>
          <td class="fw-bold" style="color:var(--text)">${Utils.escapeHtml(c.nombre || '')}</td>
          <td>${c.telefono ? `<i class="fas fa-phone me-1 text-muted"></i>${Utils.escapeHtml(c.telefono)}` : '<span class="text-muted">-</span>'}</td>
          <td>${c.email ? `<i class="fas fa-envelope me-1 text-muted"></i>${Utils.escapeHtml(c.email)}` : '<span class="text-muted">-</span>'}</td>
          <td style="max-width:200px" class="text-truncate" title="${Utils.escapeHtml(c.direccion || '')}">
            ${c.direccion ? Utils.escapeHtml(c.direccion) : '<span class="text-muted">-</span>'}
          </td>
          <td class="text-center">
            <div class="btn-group btn-group-sm">
              <button class="btn btn-ghost text-primary" onclick="ClientesPage.editarCliente(${c.id})" title="Editar Cliente">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn btn-ghost text-danger" onclick="ClientesPage.eliminarCliente(${c.id}, '${Utils.escapeHtml(c.nombre)}')" title="Eliminar Cliente">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </td>
        </tr>
      `).join('');

      // Paginación
      if (res.count && res.count > 25) {
        Utils.renderPagination('clientesPagination', res.count, 25, this.currentPage, (p) => {
          this.currentPage = p;
          this.cargarClientes();
        });
      } else {
        const pag = document.getElementById('clientesPagination');
        if (pag) pag.innerHTML = '';
      }

    } catch (err) {
      console.error('Error cargando clientes:', err);
      tbody.innerHTML = `
        <tr>
          <td colspan="6" class="text-center text-danger py-4">
            <i class="fas fa-exclamation-circle me-1"></i> Error al cargar clientes: ${err.message}
          </td>
        </tr>`;
    }
  },

  abrirModal: function(cliente = null) {
    document.getElementById('c_id').value = cliente ? cliente.id : '';
    document.getElementById('c_tipo_documento').value = cliente ? (cliente.tipo_documento || 'DNI') : 'DNI';
    document.getElementById('c_num_documento').value = cliente ? (cliente.num_documento || '') : '';
    document.getElementById('c_nombre').value = cliente ? (cliente.nombre || '') : '';
    document.getElementById('c_telefono').value = cliente ? (cliente.telefono || '') : '';
    document.getElementById('c_email').value = cliente ? (cliente.email || '') : '';
    document.getElementById('c_direccion').value = cliente ? (cliente.direccion || '') : '';

    const title = document.getElementById('clienteModalTitle');
    if (title) {
      title.innerHTML = cliente 
        ? '<i class="fas fa-user-edit me-2 text-primary"></i>Editar Cliente'
        : '<i class="fas fa-user-plus me-2 text-primary"></i>Nuevo Cliente';
    }

    Utils.showModal('clienteModal');
  },

  consultarDocumento: async function() {
    const tipo = document.getElementById('c_tipo_documento').value;
    const num = document.getElementById('c_num_documento').value.trim();
    const btn = document.getElementById('btnConsultarDoc');

    if (!num) {
      Utils.showToast('Ingresa un número de documento para consultar', 'warning');
      return;
    }

    if (tipo === 'DNI' && num.length !== 8) {
      Utils.showToast('El DNI debe tener 8 dígitos', 'warning');
      return;
    }

    if (tipo === 'RUC' && num.length !== 11) {
      Utils.showToast('El RUC debe tener 11 dígitos', 'warning');
      return;
    }

    const origBtnHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>';

    try {
      const res = await API.get(`clientes/consultar-documento/?documento=${encodeURIComponent(num)}`);
      if (res && res.nombre) {
        document.getElementById('c_nombre').value = res.nombre;
        if (res.direccion) document.getElementById('c_direccion').value = res.direccion;
        if (res.id && !document.getElementById('c_id').value) {
          document.getElementById('c_id').value = res.id;
        }
        Utils.showToast(`Datos encontrados: ${res.nombre}`, 'success');
      } else {
        Utils.showToast('Documento válido. Ingresa el nombre manualmente.', 'info');
      }
    } catch (err) {
      console.error(err);
      Utils.showToast('No se encontró el documento. Ingresa los datos del cliente.', 'info');
    } finally {
      btn.disabled = false;
      btn.innerHTML = origBtnHTML;
    }
  },

  guardarCliente: async function() {
    const id = document.getElementById('c_id').value;
    const tipo_documento = document.getElementById('c_tipo_documento').value;
    const num_documento = document.getElementById('c_num_documento').value.trim();
    const nombre = document.getElementById('c_nombre').value.trim();
    const telefono = document.getElementById('c_telefono').value.trim();
    const email = document.getElementById('c_email').value.trim();
    const direccion = document.getElementById('c_direccion').value.trim();

    if (!num_documento) {
      Utils.showToast('El número de documento es obligatorio', 'warning');
      return;
    }
    if (!nombre) {
      Utils.showToast('El nombre o razón social es obligatorio', 'warning');
      return;
    }

    const payload = {
      tipo_documento,
      num_documento,
      nombre,
      telefono: telefono || null,
      email: email || null,
      direccion: direccion || null
    };

    const btn = document.getElementById('btnGuardarCliente');
    btn.disabled = true;
    btn.innerHTML = '<div class="spinner-border spinner-border-sm me-1"></div> Guardando...';

    try {
      if (id) {
        await API.put(`clientes/${id}/`, payload);
        Utils.showToast('Cliente actualizado correctamente', 'success');
      } else {
        await API.post('clientes/', payload);
        Utils.showToast('Cliente registrado con éxito', 'success');
      }

      Utils.hideModal('clienteModal');
      await this.cargarClientes();

    } catch (err) {
      console.error('Error al guardar cliente:', err);
      Swal.fire({
        icon: 'error',
        title: 'Error al guardar',
        text: err.message || 'No se pudo guardar el cliente.'
      });
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-save me-1"></i>Guardar Cliente';
    }
  },

  editarCliente: async function(id) {
    try {
      const cliente = await API.get(`clientes/${id}/`);
      this.abrirModal(cliente);
    } catch (err) {
      Utils.showToast('Error al cargar datos del cliente', 'error');
    }
  },

  eliminarCliente: function(id, nombre) {
    Swal.fire({
      title: '¿Eliminar cliente?',
      text: `¿Estás seguro de eliminar a "${nombre}"?`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#ef4444',
      cancelButtonColor: '#64748b',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    }).then(async (result) => {
      if (result.isConfirmed) {
        try {
          await API.delete(`clientes/${id}/`);
          Utils.showToast('Cliente eliminado correctamente', 'success');
          await this.cargarClientes();
        } catch (err) {
          Swal.fire('Error', err.message || 'No se pudo eliminar el cliente.', 'error');
        }
      }
    });
  }
};
