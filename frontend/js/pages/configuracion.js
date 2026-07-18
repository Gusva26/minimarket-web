const ConfiguracionPage = {
  selectedSucursalId: null,
  allSucursales: [],
  globalBusinessName: 'Minimarket',
  globalRuc: '',
  globalTelefono: '',

  parseMercadoName: function(fullName) {
    if (!fullName) return { businessName: '', branchName: '' };
    if (fullName.includes(' - ')) {
      const parts = fullName.split(' - ');
      return {
        businessName: parts[0].trim(),
        branchName: parts.slice(1).join(' - ').trim()
      };
    }
    // Si empieza con el nombre global actual
    const currentGlobal = this.globalBusinessName;
    if (currentGlobal && fullName.startsWith(currentGlobal + ' ')) {
      return {
        businessName: currentGlobal,
        branchName: fullName.substring(currentGlobal.length + 1).trim()
      };
    }
    // Soporte para datos iniciales
    if (fullName.startsWith('Minimarket ')) {
      return {
        businessName: 'Minimarket',
        branchName: fullName.substring(11).trim()
      };
    }
    // Separación por espacio por defecto
    const spaceIdx = fullName.indexOf(' ');
    if (spaceIdx > 0) {
      return {
        businessName: fullName.substring(0, spaceIdx).trim(),
        branchName: fullName.substring(spaceIdx + 1).trim()
      };
    }
    return {
      businessName: fullName,
      branchName: ''
    };
  },

  render: async function(container) {
    const user = Auth.getUser();
    const myMercadoId = user ? user.mercado_id : null;

    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-cog text-gradient"></i>Configuración</h3>
      </div>

      <div class="row g-4">
        <!-- Panel 1: Configuración General del Negocio -->
        <div class="col-lg-5">
          <div class="card card-accent h-100">
            <div class="card-header">
              <h5 class="card-title mb-0"><i class="fas fa-building me-2" style="color:var(--accent)"></i>Datos del Negocio</h5>
            </div>
            <div class="card-body">
              <form id="formGlobalNegocio">
                <div class="form-group mb-3">
                  <label class="form-label">Nombre del Negocio <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" name="nombre_negocio" id="glob_nombre" placeholder="Ej. Minimarket Súper" required>
                </div>
                <div class="form-group mb-3">
                  <label class="form-label">RUC <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" name="ruc" id="glob_ruc" placeholder="11 dígitos" maxlength="11" required>
                </div>
                <div class="form-group mb-4">
                  <label class="form-label">Teléfono del Negocio <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" name="telefono" id="glob_telefono" placeholder="Ej. 555-1234" required>
                </div>
                <button type="submit" class="btn btn-primary w-100" id="btnGuardarGlobal">
                  <i class="fas fa-save me-2"></i>Guardar Configuración General
                </button>
              </form>
            </div>
          </div>
        </div>

        <!-- Panel 2: Listado y Gestión de Sucursales -->
        <div class="col-lg-7">
          <div class="card h-100">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="card-title mb-0"><i class="fas fa-network-wired me-2" style="color:var(--accent)"></i>Sucursales</h5>
              <button class="btn btn-primary btn-sm btn-pill" id="btnNuevaSucursal">
                <i class="fas fa-plus me-1"></i>Nueva Sucursal
              </button>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table align-middle">
                  <thead>
                    <tr>
                      <th>Sucursal</th>
                      <th>Dirección</th>
                      <th class="text-center">Estado</th>
                      <th class="text-center" style="width:100px">Acciones</th>
                    </tr>
                  </thead>
                  <tbody id="tbodySucursales">
                    <tr>
                      <td colspan="4" class="text-center py-4 text-muted">
                        <div class="spinner-modern m-auto"></div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Crear/Editar Sucursal -->
      <div class="modal-overlay" id="modalSucursal">
        <div class="modal-card" style="max-width:480px">
          <div class="modal-card-header">
            <h5 id="modalSucursalTitle"><i class="fas fa-store me-2"></i>Nueva Sucursal</h5>
            <button class="modal-close" onclick="Utils.hideModal('modalSucursal')"><i class="fas fa-times"></i></button>
          </div>
          <div class="modal-card-body">
            <form id="formSucursal">
              <div class="form-group mb-3">
                <label class="form-label">Nombre de la Sucursal <span class="text-danger">*</span></label>
                <input type="text" class="form-control" name="nombre_sucursal" placeholder="Ej. Norte, Centro, Sur" required>
              </div>
              <div class="form-group mb-3">
                <label class="form-label">Dirección <span class="text-danger">*</span></label>
                <input type="text" class="form-control" name="direccion" required>
              </div>
              <div class="form-group mb-3 d-flex align-items-center gap-2 mt-4">
                <input type="checkbox" id="suc_activo" name="activo" checked style="width:18px;height:18px;accent-color:var(--accent)">
                <label for="suc_activo" class="mb-0" style="font-weight:600;font-size:.9rem;cursor:pointer">Sucursal Activa</label>
              </div>
              <div id="suc_own_warning" class="alert alert-warning mt-2 d-none" style="font-size: 0.82rem; padding: 8px 12px;">
                <i class="fas fa-exclamation-triangle me-1"></i> No puedes desactivar tu propia sucursal de sesión.
              </div>
            </form>
          </div>
          <div class="modal-card-footer">
            <button class="btn btn-ghost" onclick="Utils.hideModal('modalSucursal')">Cancelar</button>
            <button class="btn btn-primary" id="btnGuardarSucursal"><i class="fas fa-save me-1"></i>Guardar</button>
          </div>
        </div>
      </div>
    `;

    this.bindEvents(myMercadoId);
    await this.cargarSucursales(myMercadoId);
  },

  bindEvents: function(myMercadoId) {
    // Formulario de configuración global
    const formGlobal = document.getElementById('formGlobalNegocio');
    if (formGlobal) {
      formGlobal.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.guardarGlobalNegocio(myMercadoId);
      });
    }

    // Botón Nueva Sucursal
    const btnNueva = document.getElementById('btnNuevaSucursal');
    if (btnNueva) {
      btnNueva.addEventListener('click', () => this.openCreateModal());
    }

    // Guardar en Modal
    const btnGuardarModal = document.getElementById('btnGuardarSucursal');
    if (btnGuardarModal) {
      btnGuardarModal.addEventListener('click', () => this.guardarSucursalModal(myMercadoId));
    }

    // Acciones de fila (editar)
    const tbody = document.getElementById('tbodySucursales');
    if (tbody) {
      tbody.addEventListener('click', async (e) => {
        const btn = e.target.closest('button');
        if (!btn) return;
        const action = btn.dataset.action;
        const id = btn.dataset.id;
        if (action === 'editar') {
          await this.openEditModal(id, myMercadoId);
        }
      });
    }
  },

  cargarSucursales: async function(myMercadoId) {
    const tbody = document.getElementById('tbodySucursales');
    tbody.innerHTML = `
      <tr>
        <td colspan="4" class="text-center py-4 text-muted">
          <div class="spinner-modern m-auto"></div>
        </td>
      </tr>
    `;

    try {
      // Obtenemos todas las sucursales
      const data = await API.get('mercados/?manage=true');
      this.allSucursales = data.results || data || [];

      // Determinar nombre del negocio, RUC y teléfono a partir del primer registro
      if (this.allSucursales.length > 0) {
        const first = this.allSucursales[0];
        this.globalRuc = first.ruc || '';
        this.globalTelefono = first.telefono || '';
        const parsed = this.parseMercadoName(first.nombre);
        this.globalBusinessName = parsed.businessName || 'Minimarket';

        document.getElementById('glob_nombre').value = this.globalBusinessName;
        document.getElementById('glob_ruc').value = this.globalRuc;
        document.getElementById('glob_telefono').value = this.globalTelefono;
      }

      // Renderizar listado general
      this.renderTabla(myMercadoId);
    } catch (e) {
      tbody.innerHTML = `
        <tr>
          <td colspan="4" class="text-center py-4 text-danger">
            <i class="fas fa-exclamation-circle me-1"></i> Error al cargar sucursales: ${e.message}
          </td>
        </tr>
      `;
    }
  },

  renderTabla: function(myMercadoId) {
    const tbody = document.getElementById('tbodySucursales');
    if (!this.allSucursales.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="4" class="text-center py-4 text-muted">
            <div class="empty-state py-3">
              <i class="fas fa-store-slash mb-2" style="font-size: 2rem; color: var(--text-muted)"></i>
              <div class="empty-title">No hay sucursales registradas</div>
            </div>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = this.allSucursales.map(s => {
      const isMyBranch = s.id == myMercadoId;
      const statusBadge = s.activo
        ? '<span class="badge badge-success">Activa</span>'
        : '<span class="badge badge-danger">Inactiva</span>';
      
      const parsedName = this.parseMercadoName(s.nombre);
      const displayBranchName = parsedName.branchName || s.nombre;

      return `
        <tr class="${isMyBranch ? 'table-active' : ''}">
          <td data-label="Sucursal">
            <div class="d-flex align-items-center">
              <div style="font-weight: 600; color: var(--text-main)">${Utils.escapeHtml(displayBranchName)}</div>
              ${isMyBranch ? '<span class="badge badge-accent ms-2 py-0.5" style="font-size:0.7rem">Mi Sede</span>' : ''}
            </div>
          </td>
          <td data-label="Dirección" style="font-size: 0.88rem; max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
            ${Utils.escapeHtml(s.direccion || '-')}
          </td>
          <td data-label="Estado" class="text-center">${statusBadge}</td>
          <td data-label="Acciones" class="text-center">
            <button class="btn btn-sm btn-icon btn-ghost" data-action="editar" data-id="${s.id}" title="Editar Sucursal" style="color: var(--accent)">
              <i class="fas fa-edit"></i>
            </button>
          </td>
        </tr>
      `;
    }).join('');
  },

  guardarGlobalNegocio: async function(myMercadoId) {
    const btn = document.getElementById('btnGuardarGlobal');
    btn.disabled = true;

    const nombre_negocio = document.getElementById('glob_nombre').value.trim();
    const ruc = document.getElementById('glob_ruc').value.trim();
    const telefono = document.getElementById('glob_telefono').value.trim();

    if (!nombre_negocio || !ruc || !telefono) {
      Utils.showToast('Por favor completa todos los campos requeridos', 'warning');
      btn.disabled = false;
      return;
    }

    if (ruc.length !== 11 || isNaN(ruc)) {
      Utils.showToast('El RUC debe tener exactamente 11 números', 'warning');
      btn.disabled = false;
      return;
    }

    try {
      // Llamar al endpoint personalizado para actualizar los campos globales
      await API.post('mercados/update-global/', {
        nombre_negocio,
        ruc,
        telefono
      });

      Utils.showToast('Configuración general actualizada', 'success');

      // Refrescar usuario logueado en caché para actualizar datos de sede si cambiaron
      await Auth.loadUser();
      await this.cargarSucursales(myMercadoId);

      // Renderizar Navbar inmediatamente
      const appInstance = window.App || null;
      if (appInstance && appInstance.navbar) {
        appInstance.navbar.render();
      }
    } catch (e) {
      Utils.showToast('Error al guardar configuración: ' + e.message, 'error');
    } finally {
      btn.disabled = false;
    }
  },

  openCreateModal: function() {
    this.selectedSucursalId = null;
    document.getElementById('modalSucursalTitle').innerHTML = '<i class="fas fa-plus me-2"></i>Nueva Sucursal';
    const form = document.getElementById('formSucursal');
    form.reset();
    
    const chkActivo = document.getElementById('suc_activo');
    chkActivo.disabled = false;
    chkActivo.checked = true;
    document.getElementById('suc_own_warning').classList.add('d-none');

    Utils.showModal('modalSucursal');
  },

  openEditModal: async function(id, myMercadoId) {
    this.selectedSucursalId = id;
    document.getElementById('modalSucursalTitle').innerHTML = '<i class="fas fa-edit me-2"></i>Editar Sucursal';
    const form = document.getElementById('formSucursal');
    form.reset();

    const suc = this.allSucursales.find(s => s.id == id);
    if (!suc) {
      Utils.showToast('No se encontró la sucursal seleccionada', 'error');
      return;
    }

    const parsed = this.parseMercadoName(suc.nombre);
    form.nombre_sucursal.value = parsed.branchName || suc.nombre;
    form.direccion.value = suc.direccion || '';
    
    const chkActivo = document.getElementById('suc_activo');
    chkActivo.checked = !!suc.activo;

    // Bloquear toggle activo para su propia sucursal
    if (id == myMercadoId) {
      chkActivo.disabled = true;
      document.getElementById('suc_own_warning').classList.remove('d-none');
    } else {
      chkActivo.disabled = false;
      document.getElementById('suc_own_warning').classList.add('d-none');
    }

    Utils.showModal('modalSucursal');
  },

  guardarSucursalModal: async function(myMercadoId) {
    const form = document.getElementById('formSucursal');
    const btn = document.getElementById('btnGuardarSucursal');
    
    const branchName = form.nombre_sucursal.value.trim();
    const direccion = form.direccion.value.trim();
    const activo = document.getElementById('suc_activo').checked;

    if (!branchName || !direccion) {
      Utils.showToast('Por favor completa todos los campos obligatorios', 'warning');
      return;
    }

    btn.disabled = true;
    const isEdit = !!this.selectedSucursalId;

    // Construir el nombre completo usando el nombre del negocio actual
    const fullName = this.globalBusinessName
      ? `${this.globalBusinessName} - ${branchName}`
      : branchName;

    try {
      const payload = {
        nombre: fullName,
        direccion,
        activo
      };

      if (isEdit) {
        if (this.selectedSucursalId == myMercadoId) {
          delete payload.activo;
        }
        await API.patch(`mercados/${this.selectedSucursalId}/`, payload);
        Utils.showToast('Sucursal actualizada correctamente', 'success');
      } else {
        // Al crear nueva sucursal, inyectar el RUC y el teléfono globales
        payload.ruc = this.globalRuc;
        payload.telefono = this.globalTelefono;
        await API.post('mercados/', payload);
        Utils.showToast('Sucursal registrada correctamente', 'success');
      }

      Utils.hideModal('modalSucursal');

      // Refrescar usuario logueado
      if (isEdit && this.selectedSucursalId == myMercadoId) {
        await Auth.loadUser();
        const appInstance = window.App || null;
        if (appInstance && appInstance.navbar) {
          appInstance.navbar.render();
        }
      }

      await this.cargarSucursales(myMercadoId);
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'error');
    } finally {
      btn.disabled = false;
    }
  }
};
