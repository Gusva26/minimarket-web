const HistorialPage = {
  currentPage: 1,
  currentVentasData: [],

  render: async function(container) {
    container.innerHTML = `
      <div class="page-header d-flex flex-wrap justify-content-between align-items-center gap-3">
        <div>
          <h3><i class="fas fa-history text-gradient me-2"></i>Historial de Ventas</h3>
          <p style="color:var(--text-muted);font-size:.85rem;margin:0">Gestiona, filtra, audita y anula ventas del sistema.</p>
        </div>
        <div>
          <button class="btn btn-success btn-sm btn-pill" id="btnExportarHistorialExcel">
            <i class="fas fa-file-excel me-1"></i>Exportar Excel
          </button>
        </div>
      </div>

      <!-- KPI Summary Cards -->
      <div class="kpi-grid mb-4" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1rem">
        <div class="kpi-card">
          <div class="kpi-icon icon-primary"><i class="fas fa-coins"></i></div>
          <div class="kpi-info">
            <span class="kpi-title">Ventas Totales</span>
            <span class="kpi-value text-primary" id="kpiTotalVentas">S/ 0.00</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon icon-success"><i class="fas fa-shopping-bag"></i></div>
          <div class="kpi-info">
            <span class="kpi-title">N° Transacciones</span>
            <span class="kpi-value text-success" id="kpiCantidadVentas">0</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon icon-info"><i class="fas fa-calculator"></i></div>
          <div class="kpi-info">
            <span class="kpi-title">Ticket Promedio</span>
            <span class="kpi-value" id="kpiTicketPromedio">S/ 0.00</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon icon-danger"><i class="fas fa-ban"></i></div>
          <div class="kpi-info">
            <span class="kpi-title">Comprobantes Anulados</span>
            <span class="kpi-value text-danger" id="kpiAnulaciones">0</span>
          </div>
        </div>

      </div>

      <!-- Quick Date Pills & Filters -->
      <div class="filters-bar" style="row-gap: 12px">
        <div class="filter-group w-100 mb-1">
          <label class="d-block mb-1" style="font-weight:600;font-size:0.75rem;text-transform:uppercase;color:var(--text-muted)">Período Rápido</label>
          <div class="btn-group" role="group" id="historialFiltrosRapidos">
            <button class="btn btn-primary btn-sm active" data-range="todos">Todos</button>
            <button class="btn btn-ghost btn-sm" data-range="hoy">Hoy</button>
            <button class="btn btn-ghost btn-sm" data-range="ayer">Ayer</button>
            <button class="btn btn-ghost btn-sm" data-range="semana">Últimos 7 Días</button>
            <button class="btn btn-ghost btn-sm" data-range="mes">Este Mes</button>
          </div>
        </div>

        <div class="filter-group">
          <label>Desde</label>
          <input type="date" id="filtro_fecha_inicio" class="form-control form-control-sm">
        </div>
        <div class="filter-group">
          <label>Hasta</label>
          <input type="date" id="filtro_fecha_fin" class="form-control form-control-sm">
        </div>
        <div class="filter-group">
          <label>Método</label>
          <select id="filtro_metodo_pago" class="form-select form-select-sm">
            <option value="">Todos</option>
            <option value="Efectivo">💵 Efectivo</option>
            <option value="Yape">📱 Yape</option>
            <option value="Plin">📱 Plin</option>
            <option value="Tarjeta">💳 Tarjeta</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Tipo</label>
          <select id="filtro_tipo_comprobante" class="form-select form-select-sm">
            <option value="">Todos</option>
            <option value="TICKET">Ticket</option>
            <option value="BOLETA">Boleta</option>
            <option value="FACTURA">Factura</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Estado</label>
          <select id="filtro_estado" class="form-select form-select-sm">
            <option value="">Todos</option>
            <option value="COMPLETADA">Completada</option>
            <option value="ANULADA">Anulada</option>
          </select>
        </div>
        <div class="filter-group" style="flex:1;min-width:160px">
          <label>Buscar</label>
          <input type="text" id="filtro_q" class="form-control form-control-sm" placeholder="Serie, cliente, OP o producto">
        </div>
        <div class="filter-group" style="align-self:flex-end">
          <button class="btn btn-ghost btn-sm" id="btnLimpiarFiltros"><i class="fas fa-undo me-1"></i>Limpiar</button>
        </div>
      </div>

      <!-- Sales Table -->
      <div class="table-container" style="margin-top:1rem">
        <div class="table-responsive">
          <table class="table align-middle">
            <thead>
              <tr>
                <th>Comprobante</th>
                <th>Fecha y Hora</th>
                <th>Cliente</th>
                <th class="text-center">Método</th>
                <th class="text-center">Estado</th>
                <th class="text-center">Total</th>
                <th class="text-center" style="width:130px">Acciones</th>
              </tr>
            </thead>
            <tbody id="historialTableBody">
              <tr><td colspan="7" class="text-center py-4" style="color:var(--text-muted)"><div class="spinner-modern m-auto"></div></td></tr>
            </tbody>
          </table>
        </div>
        <div id="historialPagination" class="py-3"></div>
      </div>

      <!-- Modal Vista Rápida del Comprobante -->
      <div class="modal-overlay" id="modalVentaDetalle">
        <div class="modal-card" style="max-width:620px">
          <div class="modal-card-header d-flex justify-content-between align-items-center">
            <h5 class="m-0" id="modalVentaTitle"><i class="fas fa-receipt me-2 text-primary"></i>Detalle de Comprobante</h5>
            <button class="modal-close" onclick="Utils.hideModal('modalVentaDetalle')"><i class="fas fa-times"></i></button>
          </div>
          <div class="modal-card-body p-4" id="modalVentaBody">
            <div class="text-center py-4"><div class="spinner-modern m-auto"></div></div>
          </div>
          <div class="modal-card-footer d-flex justify-content-between">
            <button class="btn btn-ghost" onclick="Utils.hideModal('modalVentaDetalle')">Cerrar</button>
            <div class="d-flex gap-2">
              <button class="btn btn-primary" id="btnImprimirModalVenta"><i class="fas fa-print me-1"></i>Imprimir Ticket</button>
            </div>
          </div>
        </div>
      </div>
    `;

    if (typeof API !== 'undefined' && API.clearCache) {
      API.clearCache();
    }

    // Por defecto mostrar Todos los comprobantes del historial
    document.getElementById('filtro_fecha_inicio').value = '';
    document.getElementById('filtro_fecha_fin').value = '';

    this.bindEvents();
    await this.cargarVentas();
  },

  bindEvents: function() {
    // Eventos de Pills de Rango Rápido
    document.querySelectorAll('#historialFiltrosRapidos .btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('#historialFiltrosRapidos .btn').forEach(b => {
          b.className = 'btn btn-ghost btn-sm';
        });
        e.target.className = 'btn btn-primary btn-sm active';
        
        const range = e.target.dataset.range;
        const fi = document.getElementById('filtro_fecha_inicio');
        const ff = document.getElementById('filtro_fecha_fin');
        const now = new Date();
        
        if (range === 'hoy') {
          const hoyStr = now.toISOString().split('T')[0];
          fi.value = hoyStr;
          ff.value = hoyStr;
        } else if (range === 'ayer') {
          const ayer = new Date(now);
          ayer.setDate(now.getDate() - 1);
          const ayerStr = ayer.toISOString().split('T')[0];
          fi.value = ayerStr;
          ff.value = ayerStr;
        } else if (range === 'semana') {
          const sem = new Date(now);
          sem.setDate(now.getDate() - 6);
          fi.value = sem.toISOString().split('T')[0];
          ff.value = now.toISOString().split('T')[0];
        } else if (range === 'mes') {
          const primero = new Date(now.getFullYear(), now.getMonth(), 1);
          fi.value = primero.toISOString().split('T')[0];
          ff.value = now.toISOString().split('T')[0];
        } else if (range === 'todos') {
          fi.value = '';
          ff.value = '';
        }

        this.currentPage = 1;
        this.cargarVentas();
      });
    });

    const filterIds = [
      'filtro_fecha_inicio', 'filtro_fecha_fin', 'filtro_metodo_pago',
      'filtro_tipo_comprobante', 'filtro_estado'
    ];
    filterIds.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('change', () => {
        // Desactivar pills si cambia manualmente el calendario
        if (id === 'filtro_fecha_inicio' || id === 'filtro_fecha_fin') {
          document.querySelectorAll('#historialFiltrosRapidos .btn').forEach(b => b.className = 'btn btn-ghost btn-sm');
        }
        this.currentPage = 1;
        this.cargarVentas();
      });
    });

    const searchInput = document.getElementById('filtro_q');
    const debouncedSearch = Utils.debounce(() => {
      this.currentPage = 1;
      this.cargarVentas();
    }, 400);

    if (searchInput) searchInput.addEventListener('input', debouncedSearch);

    const btnLimpiarFiltros = document.getElementById('btnLimpiarFiltros');
    if (btnLimpiarFiltros) {
      btnLimpiarFiltros.addEventListener('click', () => {
        document.getElementById('filtro_fecha_inicio').value = '';
        document.getElementById('filtro_fecha_fin').value = '';
        document.getElementById('filtro_metodo_pago').value = '';
        document.getElementById('filtro_tipo_comprobante').value = '';
        document.getElementById('filtro_estado').value = '';
        document.getElementById('filtro_q').value = '';
        document.querySelectorAll('#historialFiltrosRapidos .btn').forEach(b => b.className = 'btn btn-ghost btn-sm');
        this.currentPage = 1;
        this.cargarVentas();
      });
    }

    const btnExportarExcel = document.getElementById('btnExportarHistorialExcel');
    if (btnExportarExcel) {
      btnExportarExcel.addEventListener('click', () => this.exportarExcel());
    }
  },

  cargarVentas: async function(page = 1) {
    this.currentPage = page;
    const fecha_inicio = document.getElementById('filtro_fecha_inicio')?.value || '';
    const fecha_fin = document.getElementById('filtro_fecha_fin')?.value || '';
    const metodo_pago = document.getElementById('filtro_metodo_pago')?.value || '';
    const tipo_comprobante = document.getElementById('filtro_tipo_comprobante')?.value || '';
    const estado = document.getElementById('filtro_estado')?.value || '';
    const q = document.getElementById('filtro_q')?.value || '';

    let params = `?page=${this.currentPage}`;
    if (fecha_inicio) params += `&fecha_inicio=${fecha_inicio}`;
    if (fecha_fin) params += `&fecha_fin=${fecha_fin}`;
    if (metodo_pago) params += `&metodo_pago=${metodo_pago}`;
    if (tipo_comprobante) params += `&tipo_comprobante=${tipo_comprobante}`;
    if (estado) params += `&estado=${estado}`;
    if (q) params += `&q=${encodeURIComponent(q)}`;

    const tbody = document.getElementById('historialTableBody');
    if (!tbody) return;

    try {
      const data = await API.get('ventas/' + params);
      this.currentVentasData = data.results || [];
      this.renderKPIs(data.summary || null, this.currentVentasData);
      this.renderTabla(this.currentVentasData);
      Utils.renderPagination(data, 'historialPagination', this.currentPage, (p) => this.cargarVentas(p));
    } catch (e) {
      if (tbody) tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-danger">Error al cargar historial: ${e.message}</td></tr>`;
    }
  },

  renderKPIs: function(summary, pageVentas = []) {
    let totalCompletado = 0;
    let cantCompletada = 0;
    let ticketProm = 0;
    let cantAnulada = 0;

    if (summary) {
      totalCompletado = summary.total_completado || 0;
      cantCompletada = summary.cant_completada || 0;
      ticketProm = summary.ticket_promedio || 0;
      cantAnulada = summary.cant_anulada || 0;
    } else if (pageVentas && pageVentas.length > 0) {
      pageVentas.forEach(v => {
        const monto = parseFloat(v.total || 0);
        if (v.estado === 'COMPLETADA') {
          totalCompletado += monto;
          cantCompletada++;
        } else {
          cantAnulada++;
        }
      });
      ticketProm = cantCompletada > 0 ? (totalCompletado / cantCompletada) : 0;
    }

    const elTotal = document.getElementById('kpiTotalVentas');
    const elCant = document.getElementById('kpiCantidadVentas');
    const elProm = document.getElementById('kpiTicketPromedio');
    const elAnul = document.getElementById('kpiAnulaciones');

    if (elTotal) elTotal.textContent = Utils.formatMoney(totalCompletado);
    if (elCant) elCant.textContent = cantCompletada;
    if (elProm) elProm.textContent = Utils.formatMoney(ticketProm);
    if (elAnul) elAnul.textContent = cantAnulada;
  },



  renderTabla: function(ventas) {
    const tbody = document.getElementById('historialTableBody');
    if (!ventas || ventas.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><div class="empty-icon"><i class="fas fa-search"></i></div><div class="empty-title">No se encontraron ventas con los filtros seleccionados</div></div></td></tr>`;
      return;
    }

    let html = '';
    ventas.forEach(v => {
      const estadoBadge = v.estado === 'COMPLETADA'
        ? '<span class="badge badge-success" style="padding:5px 10px;border-radius:20px"><i class="fas fa-check me-1"></i>Completada</span>'
        : '<span class="badge badge-danger" style="padding:5px 10px;border-radius:20px"><i class="fas fa-times me-1"></i>Anulada</span>';

      let metodoBadge = '<span class="badge badge-secondary">Efectivo</span>';
      if (v.metodo_pago === 'Efectivo') {
        metodoBadge = '<span class="badge badge-success"><i class="fas fa-money-bill-wave me-1"></i>Efectivo</span>';
      } else if (v.metodo_pago === 'Yape') {
        metodoBadge = '<span class="badge badge-yape"><i class="fas fa-mobile-alt me-1"></i>Yape</span>';
      } else if (v.metodo_pago === 'Plin') {
        metodoBadge = '<span class="badge badge-plin"><i class="fas fa-mobile-alt me-1"></i>Plin</span>';
      } else if (v.metodo_pago === 'Tarjeta') {
        metodoBadge = '<span class="badge" style="background:rgba(99,102,241,0.15);color:#818cf8;border:1px solid rgba(99,102,241,0.3)"><i class="fas fa-credit-card me-1"></i>Tarjeta</span>';
      }

      const clienteText = v.cliente 
        ? `<div class="fw-semibold">${Utils.escapeHtml(v.cliente.nombre)}</div><small style="color:var(--text-muted)">Doc: ${Utils.escapeHtml(v.cliente.num_documento || 'S/N')}</small>` 
        : '<span style="color:var(--text-muted);font-style:italic">Cliente Genérico</span>';

      const hoy = new Date().toISOString().split('T')[0];
      const fechaVenta = new Date(v.fecha_hora).toISOString().split('T')[0];
      const puedeAnular = v.estado === 'COMPLETADA' && fechaVenta === hoy;

      const comprobanteNumStr = `${v.serie || ''}-${String(v.numero || '').padStart(6, '0')}`;

      html += `
      <tr${v.estado === 'ANULADA' ? ' style="opacity:.65;background:rgba(239,68,68,0.03)"' : ''}>
        <td data-label="Comprobante">
          <div style="font-weight:700;font-size:0.9rem">${Utils.escapeHtml(v.tipo_comprobante)}</div>
          <small class="fw-bold" style="color:var(--accent)">${Utils.escapeHtml(comprobanteNumStr)}</small>
          ${v.num_operacion ? `<br><span class="badge mt-1" style="font-size:.65rem;background:var(--surface-hover);color:var(--text)">OP: ${Utils.escapeHtml(v.num_operacion)}</span>` : ''}
        </td>
        <td data-label="Fecha" style="font-size:.85rem">
          <div><i class="far fa-calendar me-1 text-muted"></i>${Utils.formatDate(v.fecha_hora)}</div>
          <small style="color:var(--text-muted)"><i class="far fa-clock me-1"></i>${new Date(v.fecha_hora).toLocaleTimeString('es-PE', {hour:'2-digit',minute:'2-digit'})}</small>
        </td>
        <td data-label="Cliente" style="font-size:.85rem">${clienteText}</td>
        <td data-label="Método" class="text-center">${metodoBadge}</td>
        <td data-label="Estado" class="text-center">${estadoBadge}</td>
        <td data-label="Total" class="text-center fw-bold fs-6">${Utils.formatMoney(v.total)}</td>
        <td data-label="Acciones" class="text-center">
          <div class="d-flex justify-content-center gap-1">
            <button class="btn btn-sm btn-icon btn-ghost btn-ver-modal-venta" data-id="${v.id}" title="Vista Rápida" style="color:var(--accent)">
              <i class="fas fa-eye"></i>
            </button>
            ${puedeAnular ? `
              <button class="btn btn-sm btn-icon btn-ghost btn-anular-venta" data-id="${v.id}" data-numero="${Utils.escapeHtml(comprobanteNumStr)}" title="Anular Venta" style="color:var(--danger)">
                <i class="fas fa-ban"></i>
              </button>
            ` : ''}
          </div>
        </td>
      </tr>`;
    });

    tbody.innerHTML = html;

    // Escuchadores de eventos para la tabla
    tbody.querySelectorAll('.btn-ver-modal-venta').forEach(btn => {
      btn.addEventListener('click', () => this.abrirModalVenta(btn.dataset.id));
    });

    tbody.querySelectorAll('.btn-anular-venta').forEach(btn => {
      btn.addEventListener('click', async () => {
        const result = await Utils.showConfirm('¿Anular venta?', `¿Está seguro de ANULAR la venta ${btn.dataset.numero}? Esta acción devolverá el stock al inventario.`, 'Sí, anular');
        if (result.isConfirmed) {
          await this.anularVenta(btn.dataset.id);
        }
      });
    });
  },

  abrirModalVenta: async function(id) {
    Utils.showModal('modalVentaDetalle');
    const modalBody = document.getElementById('modalVentaBody');
    const btnImprimir = document.getElementById('btnImprimirModalVenta');
    
    modalBody.innerHTML = '<div class="text-center py-4"><div class="spinner-modern m-auto"></div></div>';

    if (btnImprimir) {
      btnImprimir.onclick = () => {
        window.open(API.baseURL + `ventas/${id}/pdf/`, '_blank');
      };
    }

    try {
      const v = await API.get(`ventas/${id}/`);
      const comprobanteStr = `${v.serie || ''}-${String(v.numero || '').padStart(6, '0')}`;

      let itemsHtml = '';
      if (v.detalles && v.detalles.length > 0) {
        v.detalles.forEach(d => {
          itemsHtml += `
            <tr>
              <td>${Utils.escapeHtml(d.producto_nombre || (d.producto ? d.producto.nombre : 'Producto'))}</td>
              <td class="text-center fw-bold">${parseFloat(d.cantidad)}</td>
              <td class="text-end">${Utils.formatMoney(d.precio_unitario)}</td>
              <td class="text-end fw-bold">${Utils.formatMoney(d.subtotal)}</td>
            </tr>
          `;
        });
      } else {
        itemsHtml = '<tr><td colspan="4" class="text-center text-muted">Sin detalles de productos</td></tr>';
      }

      modalBody.innerHTML = `
        <div class="card p-3 mb-3 border-0" style="background:var(--surface-hover)">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <div>
              <span class="badge bg-primary me-2">${Utils.escapeHtml(v.tipo_comprobante)}</span>
              <strong style="font-size:1.1rem;color:var(--accent)">${Utils.escapeHtml(comprobanteStr)}</strong>
            </div>
            <div>
              ${v.estado === 'COMPLETADA' 
                ? '<span class="badge badge-success"><i class="fas fa-check me-1"></i>COMPLETADA</span>' 
                : '<span class="badge badge-danger"><i class="fas fa-times me-1"></i>ANULADA</span>'}
            </div>
          </div>
          <div class="row g-2" style="font-size:0.85rem">
            <div class="col-6"><strong>Fecha:</strong> ${Utils.formatDate(v.fecha_hora)} ${new Date(v.fecha_hora).toLocaleTimeString('es-PE', {hour:'2-digit',minute:'2-digit'})}</div>
            <div class="col-6"><strong>Cajero:</strong> ${Utils.escapeHtml(v.usuario_username || 'Sistema')}</div>
            <div class="col-6"><strong>Cliente:</strong> ${v.cliente ? Utils.escapeHtml(v.cliente.nombre) : 'Público General'}</div>
            <div class="col-6"><strong>Método Pago:</strong> ${Utils.escapeHtml(v.metodo_pago || 'Efectivo')}</div>
            ${v.num_operacion ? `<div class="col-12"><strong>N° Operación:</strong> ${Utils.escapeHtml(v.num_operacion)}</div>` : ''}
          </div>
        </div>

        <h6 class="fw-bold mb-2" style="font-size:0.9rem"><i class="fas fa-list me-1 text-primary"></i>Productos Comprados</h6>
        <div class="table-responsive mb-3">
          <table class="table table-sm align-middle" style="font-size:0.85rem">
            <thead>
              <tr class="table-light">
                <th>Producto</th>
                <th class="text-center">Cant.</th>
                <th class="text-end">P.Unit</th>
                <th class="text-end">Subtotal</th>
              </tr>
            </thead>
            <tbody>
              ${itemsHtml}
            </tbody>
          </table>
        </div>

        <div class="p-3 rounded-3" style="background:var(--surface);border:1px solid var(--border)">
          <div class="d-flex justify-content-between mb-1" style="font-size:0.85rem">
            <span class="text-muted">Subtotal:</span>
            <span>${Utils.formatMoney(v.subtotal)}</span>
          </div>
          <div class="d-flex justify-content-between mb-1" style="font-size:0.85rem">
            <span class="text-muted">IGV (18%):</span>
            <span>${Utils.formatMoney(v.igv)}</span>
          </div>
          ${parseFloat(v.descuento || 0) > 0 ? `
            <div class="d-flex justify-content-between mb-1 text-danger" style="font-size:0.85rem">
              <span>Descuento:</span>
              <span>-${Utils.formatMoney(v.descuento)}</span>
            </div>
          ` : ''}
          <div class="d-flex justify-content-between pt-2 border-top fw-bold" style="font-size:1.1rem">
            <span>TOTAL:</span>
            <span class="text-primary">${Utils.formatMoney(v.total)}</span>
          </div>
          ${v.metodo_pago === 'Efectivo' && parseFloat(v.monto_recibido || 0) > 0 ? `
            <div class="d-flex justify-content-between pt-1 text-muted" style="font-size:0.8rem">
              <span>Monto Recibido: ${Utils.formatMoney(v.monto_recibido)}</span>
              <span>Vuelto: ${Utils.formatMoney(v.vuelto)}</span>
            </div>
          ` : ''}
        </div>
      `;
    } catch (e) {
      modalBody.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-1"></i>Error al cargar comprobante: ${e.message}</div>`;
    }
  },

  exportarExcel: async function() {
    const loading = Utils.showLoading();
    try {
      const fecha_inicio = document.getElementById('filtro_fecha_inicio')?.value || '';
      const fecha_fin = document.getElementById('filtro_fecha_fin')?.value || '';
      const metodo_pago = document.getElementById('filtro_metodo_pago')?.value || '';
      const tipo_comprobante = document.getElementById('filtro_tipo_comprobante')?.value || '';
      const estado = document.getElementById('filtro_estado')?.value || '';
      const q = document.getElementById('filtro_q')?.value || '';

      let params = `filtro=personalizado`;
      if (fecha_inicio) params += `&fecha_inicio=${fecha_inicio}`;
      if (fecha_fin) params += `&fecha_fin=${fecha_fin}`;
      if (metodo_pago) params += `&metodo_pago=${metodo_pago}`;

      const url = API.baseURL + `reportes/ventas/excel/?${params}`;
      const response = await fetch(url, { credentials: 'include' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const blob = await response.blob();
      const downloadUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `historial_ventas_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(downloadUrl);
      Utils.showToast('Historial de ventas descargado en Excel correctamente', 'success');
    } catch (e) {
      Utils.showToast('Error al exportar a Excel: ' + e.message, 'danger');
    } finally {
      loading.close();
    }
  },

  anularVenta: async function(id) {
    try {
      await API.post(`ventas/${id}/anular/`);
      Utils.showToast('Venta anulada correctamente', 'success');
      this.cargarVentas();
    } catch (e) {
      Utils.showToast('Error al anular venta: ' + e.message, 'danger');
    }
  }
};
