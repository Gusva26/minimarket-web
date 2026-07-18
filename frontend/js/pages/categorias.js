const CategoriasPage = {
  currentCategoriaId: null,
  currentPage: 1,
  searchTerm: '',

  render: async function (container) {
    const isAdmin = Auth.isAdmin();
    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-tags text-gradient"></i>Categorías</h3>
        <div class="page-actions">
          ${isAdmin ? '<button class="btn btn-primary btn-sm btn-pill" id="btnNuevaCategoria"><i class="fas fa-plus"></i>Nueva Categoría</button>' : ''}
        </div>
      </div>

      <div style="max-width:700px;margin:0 auto">
        <div class="filters-bar">
          <div class="search-bar" style="flex:1;min-width:200px">
            <i class="fas fa-search search-icon"></i>
            <input type="text" class="form-control" id="searchCategoria" placeholder="Buscar por nombre..." value="${this.searchTerm}">
          </div>
          <div class="filter-group" style="align-self:flex-end">
            <button class="btn btn-ghost btn-sm" id="btnLimpiarFiltrosCategoria"><i class="fas fa-undo"></i>Limpiar</button>
          </div>
        </div>
        <div class="table-container">
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th class="text-center">Cant. Productos</th>
                  ${isAdmin ? '<th class="text-center" style="width:120px">Acciones</th>' : ''}
                </tr>
              </thead>
              <tbody id="tbodyCategorias">
                <tr><td colspan="${isAdmin ? 3 : 2}" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>
              </tbody>
            </table>
          </div>
        </div>
        <div id="categoriasPagination" class="py-3"></div>
      </div>

      <!-- Modal Categoría -->
      <div class="modal-overlay" id="modalCategoria">
        <div class="modal-card" style="max-width:420px">
          <div class="modal-card-header">
            <h5 id="modalCategoriaTitle">Nueva Categoría</h5>
            <button class="modal-close" onclick="Utils.hideModal('modalCategoria')"><i class="fas fa-times"></i></button>
          </div>
          <div class="modal-card-body">
            <form id="formCategoria">
              <div class="form-group">
                <label class="form-label">Nombre</label>
                <input type="text" class="form-control" name="nombre" required autofocus>
              </div>
            </form>
          </div>
          <div class="modal-card-footer">
            <button class="btn btn-ghost" onclick="Utils.hideModal('modalCategoria')">Cancelar</button>
            <button class="btn btn-primary" id="btnGuardarCategoria"><i class="fas fa-save"></i>Guardar</button>
          </div>
        </div>
      </div>
    `;

    await this.loadCategorias();
    this.bindEvents();
  },

  bindEvents: function () {
    const btnNueva = document.getElementById('btnNuevaCategoria');
    if (btnNueva) btnNueva.addEventListener('click', () => this.openCreateModal());
    const btnGuardar = document.getElementById('btnGuardarCategoria');
    if (btnGuardar) btnGuardar.addEventListener('click', () => this.guardarCategoria());

    const searchInput = document.getElementById('searchCategoria');
    const btnLimpiar = document.getElementById('btnLimpiarFiltrosCategoria');

    const doSearch = () => {
      this.searchTerm = searchInput.value.trim();
      this.currentPage = 1;
      this.loadCategorias();
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
        this.loadCategorias();
      });
    }

    const tbodyCategorias = document.getElementById('tbodyCategorias');
    if (tbodyCategorias) {
      tbodyCategorias.addEventListener('click', async (e) => {
      const btn = e.target.closest('button');
      if (!btn) return;
      const action = btn.dataset.action;
      const id = btn.dataset.id;

      if (action === 'editar') {
        await this.openEditModal(id);
      } else if (action === 'eliminar') {
        this.confirmarEliminar(id, btn.dataset.nombre);
      }
    });
    }
  },

  loadCategorias: async function (page = 1) {
    this.currentPage = page;
    const tbody = document.getElementById('tbodyCategorias');
    const isAdmin = Auth.isAdmin();
    tbody.innerHTML = `<tr><td colspan="${isAdmin ? 3 : 2}" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>`;

    try {
      let url = `categorias/?page=${page}`;
      if (this.searchTerm) url += `&search=${encodeURIComponent(this.searchTerm)}`;
      const data = await API.get(url);
      const categorias = data.results || data || [];
      this.renderCategorias(categorias);
      
      if (data.results) {
        Utils.renderPagination(data, 'categoriasPagination', this.currentPage, (p) => this.loadCategorias(p));
      }
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="${isAdmin ? 3 : 2}" class="text-center py-4" style="color:var(--danger)">Error: ${e.message}</td></tr>`;
    }
  },

  renderCategorias: function (categorias) {
    const tbody = document.getElementById('tbodyCategorias');
    const isAdmin = Auth.isAdmin();
    if (!categorias.length) {
      tbody.innerHTML = `<tr><td colspan="${isAdmin ? 3 : 2}"><div class="empty-state"><div class="empty-icon"><i class="fas fa-tags"></i></div><div class="empty-title">No hay categorías registradas</div><div class="empty-desc">Haga clic en "Nueva Categoría" para crear la primera</div></div></td></tr>`;
      return;
    }

    tbody.innerHTML = categorias.map(c => `
      <tr>
        <td data-label="Nombre"><div style="font-weight:600">${Utils.escapeHtml(c.nombre)}</div></td>
        <td data-label="Cant. Productos" class="text-center"><span class="badge badge-info">${c.cantidad_productos ?? 0} items</span></td>
        ${isAdmin ? `
        <td data-label="Acciones" class="text-center">
          <div style="display:flex;gap:4px;justify-content:center">
            <button class="btn btn-sm btn-icon btn-ghost" data-action="editar" data-id="${c.id}" title="Editar" style="color:var(--accent)"><i class="fas fa-edit"></i></button>
            <button class="btn btn-sm btn-icon btn-ghost" data-action="eliminar" data-id="${c.id}" data-nombre="${Utils.escapeHtml(c.nombre)}" title="Eliminar" style="color:var(--danger)"><i class="fas fa-trash-alt"></i></button>
          </div>
        </td>` : ''}
      </tr>
    `).join('');
  },

  openCreateModal: function () {
    this.currentCategoriaId = null;
    document.getElementById('modalCategoriaTitle').textContent = 'Nueva Categoría';
    document.getElementById('formCategoria').reset();
    Utils.showModal('modalCategoria');
    setTimeout(() => document.querySelector('#modalCategoria input').focus(), 100);
  },

  openEditModal: async function (id) {
    this.currentCategoriaId = id;
    document.getElementById('modalCategoriaTitle').textContent = 'Editar Categoría';
    document.getElementById('formCategoria').reset();

    try {
      const data = await API.get('categorias/');
      const categorias = data.results || data || [];
      const cat = categorias.find(c => c.id == id);
      if (cat) document.getElementById('formCategoria').nombre.value = cat.nombre;
      Utils.showModal('modalCategoria');
      setTimeout(() => document.querySelector('#modalCategoria input').focus(), 100);
    } catch (e) {
      Utils.showToast('Error al cargar categoría: ' + e.message, 'error');
    }
  },

  guardarCategoria: async function () {
    const form = document.getElementById('formCategoria');
    const nombre = form.nombre.value.trim();
    if (!nombre) { Utils.showToast('El nombre es obligatorio', 'warning'); return; }

    const isEdit = !!this.currentCategoriaId;
    const btn = document.getElementById('btnGuardarCategoria');
    btn.disabled = true;

    try {
      if (isEdit) {
        await API.patch(`categorias/${this.currentCategoriaId}/`, { nombre });
      } else {
        await API.post('categorias/', { nombre });
      }
      Utils.showToast(isEdit ? 'Categoría actualizada' : 'Categoría creada', 'success');
      Utils.hideModal('modalCategoria');
      this.loadCategorias();
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'error');
    } finally {
      btn.disabled = false;
    }
  },

  confirmarEliminar: function (id, nombre) {
    Utils.showConfirm('¿Eliminar Categoría?', `Se eliminará '${nombre}'. Verifique que no tenga productos asociados.`)
      .then(async (result) => {
        if (result.isConfirmed) {
          try {
            await API.delete(`categorias/${id}/`);
            Utils.showToast('Categoría eliminada', 'success');
            this.loadCategorias();
          } catch (e) {
            Utils.showToast('Error: ' + e.message, 'error');
          }
        }
      });
  }
};
