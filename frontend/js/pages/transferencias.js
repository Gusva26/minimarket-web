const TransferenciasPage = {
  currentPage: 1,
  filtroEstado: '',
  filtroQ: '',

  render: async function (container) {
    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-exchange-alt text-gradient"></i>Transferencias</h3>
        <div class="page-actions">
          <button class="btn btn-primary btn-sm btn-pill" id="btnNuevaTransferencia"><i class="fas fa-plus"></i>Nueva Transferencia</button>
        </div>
      </div>

      <div class="filters-bar">
        <div class="filter-group">
          <label>Estado</label>
          <select class="form-select form-select-sm" id="filterTransferenciaEstado" style="min-width:160px">
            <option value="">Todos</option>
            <option value="EN_TRANSITO">En Tránsito</option>
            <option value="COMPLETADA">Completada</option>
            <option value="ANULADA">Anulada</option>
            <option value="RECHAZADA">Rechazada</option>
          </select>
        </div>
        <div class="filter-group" style="flex:1;min-width:150px">
          <label>Buscar</label>
          <input type="text" id="filterTransferenciaQ" class="form-control form-control-sm" placeholder="ID, mercado origen o destino...">
        </div>
        <div class="filter-group" style="align-self:flex-end">
          <button class="btn btn-ghost btn-sm" id="btnLimpiarFiltrosTransferencia"><i class="fas fa-undo"></i>Limpiar</button>
        </div>
      </div>

      <div id="transferenciasContent">
        <div class="loading-page"><div class="spinner-modern"></div><span>Cargando transferencias...</span></div>
      </div>

      ${this.modalNuevaHTML()}
      ${this.modalDetalleHTML()}
      ${this.modalRechazoHTML()}
    `;
    await this.cargarListado();
    this.bindEvents();
  },

  modalNuevaHTML: function() {
    return `
    <div class="modal-overlay" id="modalNuevaTransferencia">
      <div class="modal-card" style="max-width:900px">
        <div class="modal-card-header">
          <h5><i class="fas fa-exchange-alt me-2"></i>Nueva Transferencia</h5>
          <button class="modal-close" onclick="Utils.hideModal('modalNuevaTransferencia')"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-card-body">
          <div class="row g-4">
            <div class="col-md-4">
              <div class="form-group">
                <label class="form-label">Mercado Destino <span class="text-danger">*</span></label>
                <select class="form-select" id="selectMercadoDestino" required>
                  <option value="">Seleccione destino...</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Observaciones</label>
                <textarea class="form-control" id="inputObservaciones" rows="3" placeholder="Ej: Productos solicitados vía WhatsApp, urgente"></textarea>
              </div>
              <button class="btn btn-primary w-100" id="btnEnviarTransferencia" disabled>
                <i class="fas fa-paper-plane"></i>Enviar Transferencia
              </button>
              <div class="mt-3">
                <h6 style="font-weight:600;font-size:.75rem;text-transform:uppercase">Resumen</h6>
                <div id="resumenTransferencia" style="font-size:.85rem;color:var(--text-muted)">No hay productos seleccionados.</div>
              </div>
            </div>
            <div class="col-md-8">
              <div class="form-group">
                <input type="text" class="form-control" id="buscarProductoTransferencia" placeholder="Buscar producto por nombre...">
              </div>
              <div class="table-container card-flush" style="max-height:450px;overflow-y:auto;border:1px solid var(--border)">
                <table class="table">
                  <thead class="sticky-top" style="top:0;z-index:2">
                    <tr><th>Producto</th><th class="text-center">Stock Actual</th><th style="width:130px">Cantidad a Transferir</th></tr>
                  </thead>
                  <tbody id="tbodyProductosTransferencia">
                    <tr><td colspan="3" class="text-center py-3" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>`;
  },

  modalDetalleHTML: function() {
    return `
    <div class="modal-overlay" id="modalDetalleTransferencia">
      <div class="modal-card" style="max-width:700px">
        <div class="modal-card-header">
          <h5 id="detalleTransferenciaTitle">Detalle de Transferencia</h5>
          <button class="modal-close" onclick="Utils.hideModal('modalDetalleTransferencia')"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-card-body" id="detalleTransferenciaBody"></div>
      </div>
    </div>`;
  },

  modalRechazoHTML: function() {
    return `
    <div class="modal-overlay" id="modalRechazarTransferencia">
      <div class="modal-card" style="max-width:460px">
        <div class="modal-card-header">
          <h5>Rechazar Transferencia</h5>
          <button class="modal-close" onclick="Utils.hideModal('modalRechazarTransferencia')"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-card-body">
          <div class="form-group">
            <label class="form-label">Motivo del Rechazo</label>
            <textarea class="form-control" id="motivoRechazo" rows="3" required placeholder="Ej: Productos dañados, Cantidad incorrecta..."></textarea>
          </div>
        </div>
        <div class="modal-card-footer">
          <button class="btn btn-ghost" onclick="Utils.hideModal('modalRechazarTransferencia')">Cancelar</button>
          <button class="btn btn-danger" id="btnConfirmarRechazo"><i class="fas fa-times me-1"></i>Confirmar Rechazo</button>
        </div>
      </div>
    </div>`;
  },

  bindEvents: function () {
    const btnNuevaTransferencia = document.getElementById('btnNuevaTransferencia');
    if (btnNuevaTransferencia) btnNuevaTransferencia.addEventListener('click', () => this.abrirModalCrear());
    const btnEnviarTransferencia = document.getElementById('btnEnviarTransferencia');
    if (btnEnviarTransferencia) btnEnviarTransferencia.addEventListener('click', () => this.enviarTransferencia());

    const filterEstado = document.getElementById('filterTransferenciaEstado');
    const filterQ = document.getElementById('filterTransferenciaQ');
    const btnLimpiar = document.getElementById('btnLimpiarFiltrosTransferencia');

    const doFilter = () => {
      this.filtroEstado = filterEstado ? filterEstado.value : '';
      this.filtroQ = filterQ ? filterQ.value.trim() : '';
      this.currentPage = 1;
      this.cargarListado();
    };

    if (filterEstado) filterEstado.addEventListener('change', doFilter);
    let searchTimer;
    if (filterQ) {
      filterQ.addEventListener('input', () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(doFilter, 400);
      });
    }
    if (btnLimpiar) {
      btnLimpiar.addEventListener('click', () => {
        if (filterEstado) filterEstado.value = '';
        if (filterQ) filterQ.value = '';
        this.filtroEstado = '';
        this.filtroQ = '';
        this.currentPage = 1;
        this.cargarListado();
      });
    }

    document.getElementById('transferenciasContent').addEventListener('click', (e) => {
      const btn = e.target.closest('button');
      if (!btn) return;
      const action = btn.dataset.action;
      const id = btn.dataset.id;

      if (action === 'ver-detalle') {
        this.verDetalle(id);
      } else if (action === 'anular') {
        this.confirmarAnular(id);
      } else if (action === 'recibir') {
        this.confirmarRecibir(id);
      } else if (action === 'rechazar') {
        this.abrirModalRechazo(id);
      }
    });
  },

  cargarListado: async function (page = 1) {
    this.currentPage = page;
    const content = document.getElementById('transferenciasContent');
    content.innerHTML = '<div class="loading-page"><div class="spinner-modern"></div><span>Cargando transferencias...</span></div>';

    try {
      let url = `transferencias/?page=${page}`;
      if (this.filtroEstado) url += `&estado=${this.filtroEstado}`;
      if (this.filtroQ) url += `&q=${encodeURIComponent(this.filtroQ)}`;
      const data = await API.get(url);
      const transferencias = data.results || data || [];
      const user = Auth.getUser();
      const userMercadoId = user?.mercado_id || user?.mercado;

      let recibidas, enviadas;
      if (!userMercadoId) {
        recibidas = transferencias;
        enviadas = transferencias;
      } else {
        recibidas = transferencias.filter(t => t.mercado_destino === userMercadoId || t.mercado_destino?.id === userMercadoId);
        enviadas = transferencias.filter(t => t.mercado_origen === userMercadoId || t.mercado_origen?.id === userMercadoId);
      }

      const pendientes = transferencias.filter(t => t.estado === 'EN_TRANSITO');
      const completadas = transferencias.filter(t => t.estado === 'COMPLETADA');


      this.renderListado(content, pendientes, enviadas, completadas);

      if (data.results) {
        const pagDiv = document.createElement('div');
        pagDiv.id = 'transferenciasPagination';
        pagDiv.className = 'py-3';
        content.appendChild(pagDiv);
        Utils.renderPagination(data, 'transferenciasPagination', this.currentPage, (p) => this.cargarListado(p));
      }
    } catch (e) {
      content.innerHTML = `<div class="alert alert-danger">Error al cargar transferencias: ${e.message}</div>`;
    }
  },

  renderListado: function (container, pendientes, enviadas, completadas) {
    container.innerHTML = `
      <div class="row g-4">
        <div class="col-12">
          <div class="table-container">
            <div class="table-toolbar">
              <h6 class="toolbar-title"><i class="fas fa-download" style="color:var(--accent)"></i>Pendientes de Recibir</h6>
            </div>
            <div class="table-responsive">
              <table class="table">
                <thead><tr><th>ID</th><th>Origen</th><th>Fecha Envío</th><th>Estado</th><th class="text-center">Acción</th></tr></thead>
                <tbody>
                  ${pendientes.length ? pendientes.map(t => `
                    <tr>
                      <td data-label="ID" style="font-weight:700">#${t.id}</td>
                      <td data-label="Origen">${t.mercado_origen_nombre || t.mercado_origen?.nombre || '---'}</td>
                      <td data-label="Fecha">${Utils.formatDateTime(t.fecha_envio)}</td>
                      <td data-label="Estado"><span class="badge badge-accent">En Tránsito</span></td>
                      <td data-label="Acción" class="text-center">
                        <button class="btn btn-sm btn-accent btn-pill" data-action="ver-detalle" data-id="${t.id}"><i class="fas fa-eye me-1"></i>Revisar</button>
                      </td>
                    </tr>
                  `).join('') : '<tr><td colspan="5"><div class="empty-state py-3"><div class="empty-title">No hay transferencias pendientes</div></div></td></tr>'}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="table-container">
            <div class="table-toolbar">
              <h6 class="toolbar-title"><i class="fas fa-upload" style="color:var(--primary)"></i>Envíos Realizados</h6>
            </div>
            <div class="table-responsive">
              <table class="table">
                <thead><tr><th>ID</th><th>Destino</th><th>Estado</th><th></th></tr></thead>
                <tbody>
                  ${enviadas.length ? enviadas.map(t => `
                    <tr>
                      <td data-label="ID" style="font-weight:700">#${t.id}</td>
                      <td data-label="Destino">${t.mercado_destino_nombre || t.mercado_destino?.nombre || '---'}</td>
                      <td data-label="Estado">${this.estadoBadge(t.estado)}</td>
                      <td class="text-end"><button class="btn btn-sm btn-icon btn-ghost" data-action="ver-detalle" data-id="${t.id}" style="color:var(--accent)"><i class="fas fa-chevron-right"></i></button></td>
                    </tr>
                  `).join('') : '<tr><td colspan="4"><div class="empty-state py-3"><div class="empty-title">No ha realizado envíos</div></div></td></tr>'}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="table-container">
            <div class="table-toolbar">
              <h6 class="toolbar-title"><i class="fas fa-history" style="color:var(--success)"></i>Completadas</h6>
            </div>
            <div class="table-responsive">
              <table class="table">
                <thead><tr><th>ID</th><th>Origen</th><th>Fecha Rec.</th><th></th></tr></thead>
                <tbody>
                  ${completadas.length ? completadas.map(t => `
                    <tr>
                      <td data-label="ID" style="font-weight:700">#${t.id}</td>
                      <td data-label="Origen">${t.mercado_origen_nombre || t.mercado_origen?.nombre || '---'}</td>
                      <td data-label="Fecha">${Utils.formatDate(t.fecha_recepcion)}</td>
                      <td class="text-end"><button class="btn btn-sm btn-icon btn-ghost" data-action="ver-detalle" data-id="${t.id}" style="color:var(--accent)"><i class="fas fa-chevron-right"></i></button></td>
                    </tr>
                  `).join('') : '<tr><td colspan="4"><div class="empty-state py-3"><div class="empty-title">No hay transferencias completadas</div></div></td></tr>'}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    `;
  },

  estadoBadge: function (estado) {
    const map = {
      EN_TRANSITO: '<span class="badge badge-accent">En Tránsito</span>',
      COMPLETADA: '<span class="badge badge-success">Completada</span>',
      ANULADA: '<span class="badge badge-danger">Anulada</span>',
      RECHAZADA: '<span class="badge badge-warning">Rechazada</span>',
    };
    return map[estado] || `<span class="badge">${estado}</span>`;
  },

  abrirModalCrear: async function () {
    Utils.showModal('modalNuevaTransferencia');

    document.getElementById('selectMercadoDestino').innerHTML = '<option value="">Cargando...</option>';
    document.getElementById('tbodyProductosTransferencia').innerHTML = '<tr><td colspan="3" class="text-center py-3" style="color:var(--text-muted)"><div class="spinner-modern" style="margin:0 auto"></div></td></tr>';
    document.getElementById('resumenTransferencia').textContent = 'No hay productos seleccionados.';
    document.getElementById('btnEnviarTransferencia').disabled = true;

    try {
      const [mercadosData, productosData] = await Promise.all([
        API.get('mercados/'),
        API.get('productos/?page_size=1000')
      ]);

      const mercados = mercadosData.results || mercadosData || [];
      const productos = productosData.results || productosData || [];
      const user = Auth.getUser();
      const userMercadoId = user?.mercado_id || user?.mercado;

      const select = document.getElementById('selectMercadoDestino');
      select.innerHTML = '<option value="">Seleccione destino...</option>';
      mercados.forEach(m => {
        const mId = m.id;
        if (mId != userMercadoId) {
          select.innerHTML += `<option value="${m.id}">${m.nombre}</option>`;
        }
      });

      this.renderProductosTransferencia(productos);
      this.initBusquedaTransferencia();
    } catch (e) {
      Utils.showToast('Error al cargar datos: ' + e.message, 'error');
    }
  },

  renderProductosTransferencia: function (productos) {
    const tbody = document.getElementById('tbodyProductosTransferencia');
    if (!productos.length) {
      tbody.innerHTML = '<tr><td colspan="3" class="text-center py-3" style="color:var(--text-muted)">No hay productos disponibles.</td></tr>';
      return;
    }

    tbody.innerHTML = productos.map(p => `
      <tr class="producto-fila-transferencia" data-nombre="${p.nombre.toLowerCase()}">
        <td data-label="Producto">
          <div style="font-weight:600">${p.nombre}</div>
          <small style="color:var(--text-muted)">S/ ${p.precio}</small>
        </td>
        <td data-label="Stock" class="text-center">
          <span class="badge ${p.stock <= 0 ? 'badge-danger' : (p.stock < (p.stock_minimo || 5) ? 'badge-warning' : 'badge-info')}">${p.stock}</span>
        </td>
        <td data-label="Cantidad">
          <input type="number" class="form-control form-control-sm cant-transferencia"
            data-id="${p.id}" data-nombre="${p.nombre}" data-max="${p.stock}"
            min="0" max="${p.stock}" value="0" style="border-radius:50px">
        </td>
      </tr>
    `).join('');

    tbody.querySelectorAll('.cant-transferencia').forEach(input => {
      input.addEventListener('input', () => {
        let val = parseInt(input.value) || 0;
        const max = parseInt(input.dataset.max) || 0;
        if (val > max) {
          input.value = max;
          input.style.borderColor = 'var(--danger)';
          input.style.boxShadow = '0 0 0 3px rgba(239,68,68,0.15)';
        } else if (val < 0) {
          input.value = 0;
          input.style.borderColor = '';
          input.style.boxShadow = '';
        } else {
          input.style.borderColor = '';
          input.style.boxShadow = '';
        }
        this.actualizarResumenTransferencia();
      });
    });
  },

  initBusquedaTransferencia: function () {
    const input = document.getElementById('buscarProductoTransferencia');
    input.addEventListener('keyup', () => {
      const q = input.value.toLowerCase().trim();
      document.querySelectorAll('.producto-fila-transferencia').forEach(fila => {
        fila.style.display = fila.dataset.nombre.includes(q) ? '' : 'none';
      });
    });
  },

  actualizarResumenTransferencia: function () {
    const resumen = document.getElementById('resumenTransferencia');
    const btn = document.getElementById('btnEnviarTransferencia');
    const inputs = document.querySelectorAll('.cant-transferencia');
    let items = [];
    let total = 0;

    inputs.forEach(inp => {
      const cant = parseInt(inp.value) || 0;
      if (cant > 0) {
        items.push({ id: inp.dataset.id, nombre: inp.dataset.nombre, cantidad: cant });
        total += cant;
      }
    });

    if (items.length) {
      resumen.innerHTML = items.map(i => `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid var(--border)">
          <div style="flex:1;min-width:0">
            <div style="font-weight:600;font-size:.85rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${i.nombre}</div>
          </div>
          <div style="display:flex;align-items:center;gap:8px;margin-left:8px">
            <span class="badge badge-primary">${i.cantidad}</span>
            <button class="btn btn-sm btn-icon" style="color:var(--danger);padding:2px 6px;font-size:.75rem;background:none;border:none;cursor:pointer" data-remove-id="${i.id}" title="Quitar producto">
              <i class="fas fa-trash-alt"></i>
            </button>
          </div>
        </div>
      `).join('');
      resumen.querySelectorAll('[data-remove-id]').forEach(btn => {
        btn.addEventListener('click', () => {
          const id = btn.dataset.removeId;
          const input = document.querySelector(`.cant-transferencia[data-id="${id}"]`);
          if (input) {
            input.value = 0;
            input.style.borderColor = '';
            input.style.boxShadow = '';
          }
          this.actualizarResumenTransferencia();
        });
      });
      btn.disabled = false;
    } else {
      resumen.textContent = 'No hay productos seleccionados.';
      btn.disabled = true;
    }
  },

  enviarTransferencia: async function () {
    const mercadoId = document.getElementById('selectMercadoDestino').value;
    if (!mercadoId) { Utils.showToast('Seleccione un mercado destino', 'warning'); return; }

    const productos = [];
    let hayExceso = false;
    document.querySelectorAll('.cant-transferencia').forEach(inp => {
      const cant = parseInt(inp.value) || 0;
      const max = parseInt(inp.dataset.max) || 0;
      if (cant > max) hayExceso = true;
      if (cant > 0) productos.push({ producto_id: parseInt(inp.dataset.id), cantidad: cant });
    });

    if (hayExceso) { Utils.showToast('Hay productos con cantidad superior al stock disponible', 'error'); return; }
    if (!productos.length) { Utils.showToast('Seleccione al menos un producto', 'warning'); return; }

    const observaciones = document.getElementById('inputObservaciones').value;
    const btn = document.getElementById('btnEnviarTransferencia');
    btn.disabled = true;

    try {
      await API.post('transferencias/', {
        mercado_destino_id: parseInt(mercadoId),
        productos,
        observaciones
      });
      Utils.showToast('Transferencia creada correctamente', 'success');
      Utils.hideModal('modalNuevaTransferencia');
      this.cargarListado();
    } catch (e) {
      Utils.showToast('Error: ' + e.message, 'error');
    } finally {
      btn.disabled = false;
    }
  },

  verDetalle: async function (id) {
    Utils.showModal('modalDetalleTransferencia');
    const body = document.getElementById('detalleTransferenciaBody');
    body.innerHTML = '<div class="loading-page py-4"><div class="spinner-modern"></div><span>Cargando...</span></div>';

    try {
      const t = await API.get(`transferencias/${id}/`);
      const user = Auth.getUser();
      const userMercadoId = user?.mercado_id || user?.mercado;
      const esOrigen = (t.mercado_origen === userMercadoId || t.mercado_origen?.id === userMercadoId);
      const esDestino = (t.mercado_destino === userMercadoId || t.mercado_destino?.id === userMercadoId);
      const enTransito = t.estado === 'EN_TRANSITO';

      document.getElementById('detalleTransferenciaTitle').textContent = `Transferencia #${t.id}`;
      body.innerHTML = `
        <div class="row g-3 mb-3">
          <div class="col-md-5">
            <div class="card card-flush text-center p-3" style="background:var(--surface-hover)">
              <i class="fas fa-store fa-2x" style="color:var(--primary);margin-bottom:8px"></i>
              <h6 style="font-size:.7rem;font-weight:600;text-transform:uppercase;color:var(--text-muted)">Origen</h6>
              <div style="font-weight:600">${t.mercado_origen_nombre || t.mercado_origen?.nombre || '---'}</div>
              <small style="color:var(--text-muted)">${t.usuario_envio_nombre || t.usuario_envio?.username || ''}</small>
            </div>
          </div>
          <div class="col-md-2 d-flex align-items-center justify-content-center">
            <i class="fas fa-long-arrow-alt-right fa-2x" style="color:var(--text-muted);opacity:.5"></i>
          </div>
          <div class="col-md-5">
            <div class="card card-flush text-center p-3" style="background:var(--surface-hover)">
              <i class="fas fa-truck-loading fa-2x" style="color:var(--accent);margin-bottom:8px"></i>
              <h6 style="font-size:.7rem;font-weight:600;text-transform:uppercase;color:var(--text-muted)">Destino</h6>
              <div style="font-weight:600">${t.mercado_destino_nombre || t.mercado_destino?.nombre || '---'}</div>
              <small style="${t.usuario_recepcion ? 'color:var(--text-muted)' : 'color:var(--accent);font-weight:600'}">${t.usuario_recepcion_nombre || t.usuario_recepcion?.username || 'Pendiente de recepción'}</small>
            </div>
          </div>
        </div>

        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
          ${this.estadoBadge(t.estado)}
          <small style="color:var(--text-muted)">Enviado: ${Utils.formatDateTime(t.fecha_envio)}</small>
        </div>

        <h6 style="font-weight:600;font-size:.75rem;text-transform:uppercase;margin-bottom:8px">Productos Transferidos</h6>
        <div class="table-container card-flush" style="border:1px solid var(--border)">
          <table class="table">
            <thead><tr><th>Producto</th><th class="text-center">Vencimiento</th><th class="text-center">Cantidad</th></tr></thead>
            <tbody>
              ${(t.detalles || []).map(d => `
                <tr>
                  <td data-label="Producto">
                    <div style="font-weight:600;color:var(--primary)">${d.producto_origen_nombre || d.producto_origen?.nombre || '---'}</div>
                    <small style="color:var(--text-muted)">${d.producto_origen?.categoria?.nombre || ''}</small>
                  </td>
                  <td data-label="Vencimiento" class="text-center">${d.fecha_vencimiento ? Utils.formatDate(d.fecha_vencimiento) : '<small style="color:var(--text-muted)">---</small>'}</td>
                  <td data-label="Cantidad" class="text-center"><span style="font-size:1.2rem;font-weight:700">${d.cantidad}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        ${t.observaciones ? `
          <div class="mb-3">
            <h6 style="font-weight:600;font-size:.75rem;text-transform:uppercase;margin-bottom:4px">Observaciones</h6>
            <div class="p-3" style="background:var(--surface-hover);border-radius:var(--radius);font-size:.85rem">${t.observaciones}</div>
          </div>
        ` : ''}

        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <button class="btn btn-primary btn-pill" id="btnImprimirGuia">
            <i class="fas fa-print me-1"></i>Imprimir Guía de Recepción
          </button>
          ${enTransito && esOrigen ? `
            <button class="btn btn-outline-danger btn-pill" data-action="anular" data-id="${t.id}">
              <i class="fas fa-undo me-1"></i>Anular Transferencia
            </button>
          ` : ''}
          ${enTransito && esDestino ? `
            <button class="btn btn-success btn-pill" data-action="recibir" data-id="${t.id}">
              <i class="fas fa-check-circle me-1"></i>Recibir Productos
            </button>
            <button class="btn btn-outline-danger btn-pill" data-action="rechazar" data-id="${t.id}">
              <i class="fas fa-times-circle me-1"></i>Rechazar
            </button>
          ` : ''}
        </div>
      `;

      const btnImprimir = document.getElementById('btnImprimirGuia');
      if (btnImprimir) {
        btnImprimir.addEventListener('click', () => {
          Utils.imprimirGuiaTransferencia(t);
        });
      }

      body.querySelectorAll('[data-action]').forEach(btn => {
        btn.addEventListener('click', () => {
          const action = btn.dataset.action;
          const tid = btn.dataset.id;
          Utils.hideModal('modalDetalleTransferencia');
          if (action === 'anular') this.confirmarAnular(tid);
          else if (action === 'recibir') this.confirmarRecibir(tid);
          else if (action === 'rechazar') this.abrirModalRechazo(tid);
        });
      });

    } catch (e) {
      body.innerHTML = `<div class="alert alert-danger">Error: ${e.message}</div>`;
    }
  },

  confirmarAnular: function (id) {
    Utils.showConfirm('¿Anular Transferencia?', 'El stock regresará inmediatamente a su inventario actual.')
      .then(async (result) => {
        if (result.isConfirmed) {
          try {
            await API.post(`transferencias/${id}/anular/`);
            Utils.showToast('Transferencia anulada', 'success');
            this.cargarListado();
          } catch (e) {
            Utils.showToast('Error: ' + e.message, 'error');
          }
        }
      });
  },

  confirmarRecibir: function (id) {
    Utils.showConfirm('¿Confirmar Recepción?', 'Los productos se sumarán a su stock disponible.')
      .then(async (result) => {
        if (result.isConfirmed) {
          try {
            await API.post(`transferencias/${id}/recibir/`);
            Utils.showToast('Productos recibidos correctamente', 'success');
            this.cargarListado();
          } catch (e) {
            Utils.showToast('Error: ' + e.message, 'error');
          }
        }
      });
  },

  abrirModalRechazo: function (id) {
    document.getElementById('motivoRechazo').value = '';
    document.getElementById('btnConfirmarRechazo').dataset.id = id;
    Utils.showModal('modalRechazarTransferencia');
    document.getElementById('btnConfirmarRechazo').onclick = async () => {
      const motivo = document.getElementById('motivoRechazo').value.trim();
      if (!motivo) { Utils.showToast('Debe ingresar un motivo', 'warning'); return; }
      try {
        await API.post(`transferencias/${id}/rechazar/`, { motivo_rechazo: motivo });
        Utils.showToast('Transferencia rechazada', 'success');
        Utils.hideModal('modalRechazarTransferencia');
        this.cargarListado();
      } catch (e) {
        Utils.showToast('Error: ' + e.message, 'error');
      }
    };
  }
};
