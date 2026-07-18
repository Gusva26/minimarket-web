const UsuariosPage = {
  render: async function(container) {
    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-users text-gradient"></i>Usuarios</h3>
        <div class="page-actions">
          <button class="btn btn-primary btn-sm btn-pill" id="btnNuevoUsuario"><i class="fas fa-plus"></i>Nuevo Usuario</button>
        </div>
      </div>

      <div class="table-container">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Nombre Completo</th>
                <th>Email</th>
                <th>Rol</th>
                <th class="text-center">Estado</th>
                <th class="text-center" style="width:160px">Acciones</th>
              </tr>
            </thead>
            <tbody id="usuariosTableBody">
              <tr><td colspan="6" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>
            </tbody>
          </table>
        </div>
        <div id="usuariosPagination" class="py-3"></div>
      </div>
      ${this.modalUsuarioHTML()}
      ${this.modalPasswordHTML()}`;
    this.bindEvents();
    await this.cargarUsuarios();
  },

  modalUsuarioHTML: function() {
    return `
    <div class="modal-overlay" id="usuarioModal">
      <div class="modal-card" style="max-width:560px">
        <div class="modal-card-header">
          <h5 id="usuarioModalTitle"><i class="fas fa-user me-2"></i>Nuevo Usuario</h5>
          <button class="modal-close" onclick="Utils.hideModal('usuarioModal')"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-card-body">
          <input type="hidden" id="usuario_id">
          <div class="row g-3">
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label">Usuario <span class="text-danger">*</span></label>
                <input type="text" class="form-control" id="u_username" placeholder="Ej: jperez" required>
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label">Email</label>
                <input type="email" class="form-control" id="u_email" placeholder="Ej: jperez@ejemplo.com">
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label">Nombres</label>
                <input type="text" class="form-control" id="u_first_name" placeholder="Ej: Juan Carlos">
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label">Apellidos</label>
                <input type="text" class="form-control" id="u_last_name" placeholder="Ej: Pérez García">
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label">Rol <span class="text-danger">*</span></label>
                <select class="form-select" id="u_rol">
                  <option value="VENDEDOR">Vendedor — solo puede vender y ver dashboard</option>
                  <option value="ADMIN">Administrador — acceso completo al sistema</option>
                </select>
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-group">
                <label class="form-label">Mercado/Sucursal</label>
                <select class="form-select" id="u_mercado">
                  <option value="">Seleccionar...</option>
                </select>
              </div>
            </div>
            <div class="col-md-6" id="passwordField">
              <div class="form-group">
                <label class="form-label">Contraseña <span class="text-danger">*</span></label>
                <input type="password" class="form-control" id="u_password" placeholder="Mínimo 8 caracteres">
              </div>
            </div>
            <div class="col-md-6 d-flex align-items-end">
              <div style="display:flex;align-items:center;gap:8px">
                <input type="checkbox" id="u_is_active" checked style="width:18px;height:18px;accent-color:var(--accent)">
                <label for="u_is_active" style="font-weight:600;font-size:.88rem;">Activo</label>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-card-footer">
          <button class="btn btn-ghost" onclick="Utils.hideModal('usuarioModal')">Cancelar</button>
          <button class="btn btn-primary" id="btnGuardarUsuario">Guardar</button>
        </div>
      </div>
    </div>`;
  },

  modalPasswordHTML: function() {
    return `
    <div class="modal-overlay" id="passwordModal">
      <div class="modal-card" style="max-width:440px">
        <div class="modal-card-header">
          <h5><i class="fas fa-key me-2"></i>Cambiar Contraseña</h5>
          <button class="modal-close" onclick="Utils.hideModal('passwordModal')"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-card-body">
          <input type="hidden" id="pw_usuario_id">
          <div class="form-group">
            <label class="form-label">Nueva Contraseña <span class="text-danger">*</span></label>
            <input type="password" class="form-control" id="pw_new_password1" placeholder="Mínimo 8 caracteres">
          </div>
          <div class="form-group">
            <label class="form-label">Confirmar Contraseña <span class="text-danger">*</span></label>
            <input type="password" class="form-control" id="pw_new_password2" placeholder="Repite la contraseña">
          </div>
        </div>
        <div class="modal-card-footer">
          <button class="btn btn-ghost" onclick="Utils.hideModal('passwordModal')">Cancelar</button>
          <button class="btn btn-primary" id="btnGuardarPassword">Cambiar</button>
        </div>
      </div>
    </div>`;
  },

  bindEvents: function() {
    document.getElementById('btnNuevoUsuario').addEventListener('click', () => {
      this.limpiarModalUsuario();
      document.getElementById('usuarioModalTitle').textContent = 'Nuevo Usuario';
      document.getElementById('passwordField').style.display = '';
      this.cargarMercados();
      Utils.showModal('usuarioModal');
    });
    document.getElementById('btnGuardarUsuario').addEventListener('click', () => this.guardarUsuario());
    document.getElementById('btnGuardarPassword').addEventListener('click', () => this.cambiarPassword());
  },

  cargarMercados: async function(selectedId) {
    const select = document.getElementById('u_mercado');
    try {
      const data = await API.get('mercados/?all=true');
      const mercados = data.results || data || [];
      select.innerHTML = '<option value="">Seleccionar...</option>';
      mercados.forEach(m => {
        const sel = m.id === selectedId ? ' selected' : '';
        select.innerHTML += `<option value="${m.id}"${sel}>${m.nombre}</option>`;
      });
    } catch (e) {
      select.innerHTML = '<option value="">Error al cargar</option>';
    }
  },

  cargarUsuarios: async function() {
    const tbody = document.getElementById('usuariosTableBody');
    try {
      const data = await API.get('usuarios/');
      this.renderTabla(data.results || []);
      Utils.renderPagination(data, 'usuariosPagination', 1, (p) => this.cargarUsuarios(p));
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4" style="color:var(--danger)">Error: ${e.message}</td></tr>`;
    }
  },

  renderTabla: function(usuarios) {
    const tbody = document.getElementById('usuariosTableBody');
    if (!usuarios || usuarios.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><div class="empty-icon"><i class="fas fa-users"></i></div><div class="empty-title">No hay usuarios registrados</div></div></td></tr>`;
      return;
    }
    const currentUser = Auth.getUser();
    let html = '';
    usuarios.forEach(u => {
      const badge = u.is_active
        ? '<span class="badge badge-success">Activo</span>'
        : '<span class="badge badge-danger">Inactivo</span>';
      const esMismo = currentUser && currentUser.id === u.id;
      html += `
      <tr>
        <td data-label="Usuario" style="font-weight:500">${Utils.escapeHtml(u.username)}</td>
        <td data-label="Nombre">${Utils.escapeHtml(u.first_name || '')} ${Utils.escapeHtml(u.last_name || '')}</td>
        <td data-label="Email">${Utils.escapeHtml(u.email || '-')}</td>
        <td data-label="Rol"><span class="badge ${u.rol === 'ADMIN' ? 'badge-warning' : 'badge-accent'}">${u.rol || 'VENDEDOR'}</span></td>
        <td data-label="Estado" class="text-center">${badge}</td>
        <td data-label="Acciones" class="text-center">
          <div style="display:flex;gap:4px;justify-content:center">
            <button class="btn btn-sm btn-icon btn-ghost btn-editar-usuario" data-id="${u.id}" title="Editar" style="color:var(--accent)"><i class="fas fa-edit"></i></button>
            <button class="btn btn-sm btn-icon btn-ghost btn-cambiar-pw" data-id="${u.id}" title="Cambiar Contraseña" style="color:var(--warning)"><i class="fas fa-key"></i></button>
            <button class="btn btn-sm btn-icon btn-ghost btn-toggle-activo" data-id="${u.id}" data-activo="${u.is_active}" title="${u.is_active ? 'Desactivar' : 'Activar'}" style="color:${u.is_active ? 'var(--success)' : 'var(--text-muted)'}"><i class="fas ${u.is_active ? 'fa-toggle-on' : 'fa-toggle-off'}"></i></button>
            ${!esMismo ? `<button class="btn btn-sm btn-icon btn-ghost btn-eliminar-usuario" data-id="${u.id}" data-name="${Utils.escapeHtml(u.username)}" title="Eliminar" style="color:var(--danger)"><i class="fas fa-trash"></i></button>` : ''}
          </div>
        </td>
      </tr>`;
    });
    tbody.innerHTML = html;

    tbody.querySelectorAll('.btn-editar-usuario').forEach(btn => {
      btn.addEventListener('click', () => this.editarUsuario(btn.dataset.id));
    });
    tbody.querySelectorAll('.btn-cambiar-pw').forEach(btn => {
      btn.addEventListener('click', () => {
        document.getElementById('pw_usuario_id').value = btn.dataset.id;
        document.getElementById('pw_new_password1').value = '';
        document.getElementById('pw_new_password2').value = '';
        Utils.showModal('passwordModal');
      });
    });
    tbody.querySelectorAll('.btn-toggle-activo').forEach(btn => {
      btn.addEventListener('click', () => this.toggleActivo(btn.dataset.id, btn.dataset.activo === 'true'));
    });
    tbody.querySelectorAll('.btn-eliminar-usuario').forEach(btn => {
      btn.addEventListener('click', () => this.eliminarUsuario(btn.dataset.id, btn.dataset.name));
    });
  },

  limpiarModalUsuario: function() {
    document.getElementById('usuario_id').value = '';
    document.getElementById('u_username').value = '';
    document.getElementById('u_first_name').value = '';
    document.getElementById('u_last_name').value = '';
    document.getElementById('u_email').value = '';
    document.getElementById('u_rol').value = 'VENDEDOR';
    document.getElementById('u_password').value = '';
    document.getElementById('u_is_active').checked = true;
    document.getElementById('u_mercado').innerHTML = '<option value="">Seleccionar...</option>';
  },

  editarUsuario: async function(id) {
    try {
      const u = await API.get(`usuarios/${id}/`);
      document.getElementById('usuario_id').value = u.id;
      document.getElementById('u_username').value = u.username;
      document.getElementById('u_first_name').value = u.first_name || '';
      document.getElementById('u_last_name').value = u.last_name || '';
      document.getElementById('u_email').value = u.email || '';
      document.getElementById('u_rol').value = u.rol || 'VENDEDOR';
      document.getElementById('u_is_active').checked = u.is_active;
      document.getElementById('passwordField').style.display = 'none';
      document.getElementById('usuarioModalTitle').textContent = 'Editar Usuario';
      await this.cargarMercados(u.mercado_id);
      Utils.showModal('usuarioModal');
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'danger');
    }
  },

  guardarUsuario: async function() {
    const id = document.getElementById('usuario_id').value;
    const username = document.getElementById('u_username').value.trim();
    const password = document.getElementById('u_password').value;
    const email = document.getElementById('u_email').value.trim();

    if (!username) { Utils.showToast('El nombre de usuario es obligatorio', 'warning'); return; }
    if (!/^[\w.@+-]+$/.test(username)) { Utils.showToast('El usuario solo puede contener letras, números y @/./+/-/_', 'warning'); return; }
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { Utils.showToast('Ingresa un correo electrónico válido', 'warning'); return; }
    if (!id && !password) { Utils.showToast('La contraseña es obligatoria para nuevos usuarios', 'warning'); return; }
    if (!id && password.length < 6) { Utils.showToast('La contraseña debe tener al menos 6 caracteres', 'warning'); return; }

    const mercadoVal = document.getElementById('u_mercado').value;
    const data = {
      username,
      first_name: document.getElementById('u_first_name').value.trim(),
      last_name: document.getElementById('u_last_name').value.trim(),
      email,
      rol: document.getElementById('u_rol').value,
      is_active: document.getElementById('u_is_active').checked,
      mercado: mercadoVal || null
    };
    if (!id) data.password = password;

    try {
      if (id) {
        await API.patch(`usuarios/${id}/`, data);
      } else {
        await API.post('usuarios/', data);
      }
      Utils.showToast(id ? 'Usuario actualizado' : 'Usuario creado', 'success');
      Utils.hideModal('usuarioModal');
      this.cargarUsuarios();
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'danger');
    }
  },

  cambiarPassword: async function() {
    const id = document.getElementById('pw_usuario_id').value;
    const pw1 = document.getElementById('pw_new_password1').value;
    const pw2 = document.getElementById('pw_new_password2').value;
    if (!pw1 || !pw2) { Utils.showToast('Ambos campos son obligatorios', 'warning'); return; }
    if (pw1.length < 6) { Utils.showToast('La contraseña debe tener al menos 6 caracteres', 'warning'); return; }
    if (pw1 !== pw2) { Utils.showToast('Las contraseñas no coinciden', 'warning'); return; }
    try {
      await API.post(`usuarios/${id}/cambiar-password/`, { new_password1: pw1, new_password2: pw2 });
      Utils.showToast('Contraseña cambiada', 'success');
      Utils.hideModal('passwordModal');
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'danger');
    }
  },

  toggleActivo: async function(id, activo) {
    const action = activo ? 'desactivar' : 'activar';
    const result = await Utils.showConfirm(`¿${action} usuario?`, `Se ${action}á el usuario seleccionado.`);
    if (!result.isConfirmed) return;
    try {
      await API.post(`usuarios/${id}/toggle-activo/`);
      Utils.showToast(`Usuario ${activo ? 'desactivado' : 'activado'}`, 'success');
      this.cargarUsuarios();
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'danger');
    }
  },

  eliminarUsuario: async function(id, name) {
    const result = await Utils.showConfirm('¿Eliminar usuario?', `Se eliminará permanentemente a "${name}".`);
    if (!result.isConfirmed) return;
    try {
      await API.delete(`usuarios/${id}/`);
      Utils.showToast('Usuario eliminado', 'success');
      this.cargarUsuarios();
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'danger');
    }
  }
};
