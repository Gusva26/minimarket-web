const ComprobantePage = {
  render: async function(container, id) {
    const loading = Utils.showLoading();
    try {
      const venta = await API.get(`ventas/${id}/`);
      this.renderHTML(container, venta);
    } catch (e) {
      container.innerHTML = `<div class="alert alert-danger">Error al cargar comprobante: ${e.message}</div>`;
    } finally {
      loading.close();
    }
  },

  renderHTML: function(container, venta) {
    const isAnulada = venta.estado === 'ANULADA';
    const mercado = venta.mercado || {};

    container.innerHTML = `
    <style>
      .watermark-anulada { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%) rotate(-45deg); font-size: 5rem; font-weight: 900; color: rgba(220,53,69,0.2); z-index: 0; pointer-events: none; text-transform: uppercase; white-space: nowrap; }
      @media print {
        .no-print { display: none !important; }
        .print-ticket { display: block !important; width: 76mm !important; margin: 0 auto !important; padding: 0 !important; font-family: monospace !important; font-size: 8.5pt !important; color: black !important; background: white !important; }
        @page { size: 80mm auto; margin: 0 !important; }
        body { background: white !important; margin: 0 !important; padding: 0 !important; width: 80mm !important; }
        .ticket-divider { border-top: 1px dashed black; margin: 5px 0; }
      }
      .print-ticket { display: none; }
    </style>

    <div class="row justify-content-center py-4">
      <div class="col-lg-6">
        <div class="card card-elevated no-print position-relative overflow-hidden">
          ${isAnulada ? '<div class="watermark-anulada">VENTA ANULADA</div>' : ''}
          <div style="background:${isAnulada ? 'var(--text-muted)' : 'var(--primary)'};padding:1.5rem;text-align:center;color:white">
            <div style="width:50px;height:50px;border-radius:50%;background:white;display:inline-flex;align-items:center;justify-content:center;margin-bottom:12px;box-shadow:var(--shadow)">
              <i class="fas fa-store" style="color:var(--primary)"></i>
            </div>
            <h3 style="font-weight:700;margin:0">${Utils.escapeHtml(mercado.nombre || 'MINIMARKET').toUpperCase()}</h3>
            <p style="opacity:.75;font-size:.85rem;margin:0">RUC: ${Utils.escapeHtml(mercado.ruc || '20123456789')}</p>
            <p style="opacity:.75;font-size:.85rem;margin:0">${Utils.escapeHtml(mercado.direccion || '')}</p>
          </div>
          <div class="card-body p-4 p-md-5">
            <div style="text-align:center;margin-bottom:1rem;border-bottom:1px solid var(--border);padding-bottom:1rem">
              <h5 style="font-weight:700;color:var(--primary);margin-bottom:4px">${Utils.escapeHtml(venta.tipo_comprobante)}</h5>
              <h6 style="font-weight:700">${Utils.escapeHtml(venta.serie || '')}-${String(venta.numero || '').padStart(6, '0')}</h6>
              <p style="color:var(--text-muted);font-size:.85rem;margin:0">${Utils.formatDateTime(venta.fecha_hora)}</p>
            </div>

            ${venta.cliente ? `
            <div style="font-size:.85rem;margin-bottom:1rem;padding:0.75rem 1rem;background:var(--surface-hover);border-radius:var(--radius)">
              <h6 style="font-size:.7rem;font-weight:600;text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px">Datos del Cliente</h6>
              <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="color:var(--text-muted)">NOMBRE:</span><span style="font-weight:600">${Utils.escapeHtml(venta.cliente.nombre)}</span></div>
              <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="color:var(--text-muted)">${Utils.escapeHtml(venta.cliente.tipo_documento || 'DOC')}:</span><span style="font-weight:600">${Utils.escapeHtml(venta.cliente.num_documento)}</span></div>
              ${venta.cliente.direccion ? `<div style="display:flex;justify-content:space-between"><span style="color:var(--text-muted)">DIRECCIÓN:</span><span style="font-weight:600;text-align:right;max-width:200px">${Utils.escapeHtml(venta.cliente.direccion)}</span></div>` : ''}
            </div>` : ''}

            <div style="font-size:.85rem;margin-bottom:1rem">
              <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="font-weight:600;font-size:.7rem;text-transform:uppercase;color:var(--text-muted)">Vendedor:</span><span style="font-weight:600">${Utils.escapeHtml(venta.usuario ? (venta.usuario.first_name || venta.usuario.username) : '')}</span></div>
              <div style="display:flex;justify-content:space-between"><span style="font-weight:600;font-size:.7rem;text-transform:uppercase;color:var(--text-muted)">Método de Pago:</span><span style="font-weight:600">${Utils.escapeHtml(venta.metodo_pago)}</span></div>
            </div>

            <div class="table-container card-flush" style="border:1px solid var(--border);margin-bottom:1rem;font-size:.88rem">
              <table class="table" style="margin:0">
                <thead><tr><th>DESCRIPCIÓN</th><th class="text-center">CANT.</th><th class="text-center">P.UNIT</th><th class="text-end">TOTAL</th></tr></thead>
                <tbody id="detalleBody"></tbody>
              </table>
            </div>

            <div style="background:var(--surface-hover);border-radius:var(--radius);padding:1rem;margin-bottom:1rem;border:1px solid var(--border)">
              <div style="display:flex;justify-content:space-between;margin-bottom:8px"><span class="fw-bold small">OP. GRAVADA</span><span class="fw-bold small">${Utils.formatMoney(venta.subtotal)}</span></div>
              ${venta.descuento && parseFloat(venta.descuento) > 0 ? `
              <div style="display:flex;justify-content:space-between;margin-bottom:8px;color:var(--danger)"><span class="fw-bold small">DESCUENTO</span><span class="fw-bold small">-${Utils.formatMoney(venta.descuento)}</span></div>
              ` : ''}
              <div style="display:flex;justify-content:space-between;margin-bottom:8px"><span class="fw-bold small">IGV (18%)</span><span class="fw-bold small">${Utils.formatMoney(venta.igv)}</span></div>
              <hr>
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                <h5 style="font-weight:700;color:var(--primary);margin:0">TOTAL A PAGAR</h5>
                <h4 style="font-weight:700;color:var(--primary);margin:0">${Utils.formatMoney(venta.total)}</h4>
              </div>
              ${venta.metodo_pago === 'Efectivo' ? `
              <div style="border-top:1px solid var(--border);padding-top:12px">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="color:var(--text-muted);font-size:.85rem">RECIBIDO</span><span style="font-weight:600;font-size:.85rem">${Utils.formatMoney(venta.monto_recibido)}</span></div>
                <div style="display:flex;justify-content:space-between"><span style="color:var(--text-muted);font-size:.85rem">VUELTO</span><span style="font-weight:600;color:var(--success);font-size:.85rem">${Utils.formatMoney(venta.vuelto)}</span></div>
              </div>` : `
              <div style="border-top:1px solid var(--border);padding-top:12px;display:flex;justify-content:space-between">
                <span style="color:var(--text-muted);font-size:.85rem">NRO. OPERACIÓN</span>
                <span style="font-weight:600;font-size:.85rem">${Utils.escapeHtml(venta.num_operacion || '---')}</span>
              </div>`}
            </div>

            <div style="text-align:center;margin-bottom:1rem">
              <p style="color:var(--text-muted);font-size:.85rem;font-weight:500;font-style:italic;margin:0">¡Gracias por su preferencia!</p>
              <p style="color:var(--text-muted);font-size:.85rem;margin:0">Vuelva pronto</p>
            </div>

            <div style="display:flex;gap:8px;flex-wrap:wrap" class="no-print">
              ${venta.estado === 'COMPLETADA'
                ? `<button id="btnImprimirComprobante" class="btn btn-primary" style="flex:1;padding:0.85rem"><i class="fas fa-print me-2"></i>Imprimir Comprobante</button>`
                : `<button class="btn btn-danger" style="flex:1;padding:0.85rem" disabled><i class="fas fa-ban me-2"></i>VENTA ANULADA</button>`}
              <a href="#/ventas-historial" class="btn btn-ghost" style="padding:0.85rem 1.5rem"><i class="fas fa-arrow-left me-2"></i>Regresar</a>
            </div>

          </div>
        </div>
      </div>
    </div>

    <div class="print-ticket">
      <div class="text-center">
        <div class="fw-bold" style="font-size:11pt">${Utils.escapeHtml(mercado.nombre || 'MINIMARKET').toUpperCase()}</div>
        <div>RUC: ${Utils.escapeHtml(mercado.ruc || '20123456789')}</div>
        <div style="font-size:7pt">${Utils.escapeHtml(mercado.direccion || '').toUpperCase()}</div>
        <div class="ticket-divider"></div>
        <div class="fw-bold">${Utils.escapeHtml(venta.tipo_comprobante)}</div>
        <div class="fw-bold">${Utils.escapeHtml(venta.serie || '')}-${String(venta.numero || '').padStart(6, '0')}</div>
        <div class="ticket-divider"></div>
      </div>
      <div style="font-size:7.5pt">
        <div>FECHA: ${Utils.formatDateTime(venta.fecha_hora)}</div>
        <div>CAJERO: ${venta.usuario ? Utils.escapeHtml(venta.usuario.username || '').toUpperCase() : ''}</div>
        ${venta.cliente ? `<div class="ticket-divider"></div><div>CLIENTE: ${Utils.escapeHtml(venta.cliente.nombre).toUpperCase()}</div><div>${Utils.escapeHtml(venta.cliente.tipo_documento || 'DOC')}: ${Utils.escapeHtml(venta.cliente.num_documento)}</div>` : ''}
        <div class="ticket-divider"></div>
      </div>
      <table style="width:100%;border-collapse:collapse;font-size:7.5pt">
        <thead><tr><th style="text-align:left;border-bottom:1px dashed black">CANT</th><th style="text-align:left;border-bottom:1px dashed black">DESCRIPCION</th><th style="text-align:right;border-bottom:1px dashed black">TOTAL</th></tr></thead>
        <tbody id="printDetalleBody"></tbody>
      </table>
      <div class="ticket-divider"></div>
      <table style="width:100%;font-size:7.5pt">
        <tr><td class="text-right">OP. GRAVADA S/</td><td class="text-right" style="width:30%">${Number(venta.subtotal).toFixed(2)}</td></tr>
        ${venta.descuento && parseFloat(venta.descuento) > 0 ? `
        <tr><td class="text-right">DESCUENTO S/</td><td class="text-right">-${Number(venta.descuento).toFixed(2)}</td></tr>
        ` : ''}
        <tr><td class="text-right">I.G.V. (18%) S/</td><td class="text-right">${Number(venta.igv).toFixed(2)}</td></tr>
        <tr><td class="text-right fw-bold" style="font-size:9pt">TOTAL S/</td><td class="text-right fw-bold" style="font-size:9pt">${Number(venta.total).toFixed(2)}</td></tr>
        ${venta.metodo_pago === 'Efectivo'
          ? `<tr><td class="text-right">RECIBIDO S/</td><td class="text-right">${Number(venta.monto_recibido || 0).toFixed(2)}</td></tr><tr><td class="text-right">VUELTO S/</td><td class="text-right">${Number(venta.vuelto || 0).toFixed(2)}</td></tr>`
          : `<tr><td class="text-right">NRO. OP:</td><td class="text-right">${Utils.escapeHtml(venta.num_operacion || '---')}</td></tr>`}
      </table>
      <div class="text-center" style="margin-top:10px"><div class="fw-bold">¡GRACIAS POR SU PREFERENCIA!</div><div>SISTEMA MINIMARKET POS</div></div>
    </div>`;

    const tbody = document.getElementById('detalleBody');
    const printTbody = document.getElementById('printDetalleBody');
    if (venta.detalles) {
      let html = '', printHtml = '';
      venta.detalles.forEach(d => {
        const prodNombre = d.producto ? d.producto.nombre : d.producto_nombre || '';
        html += `<tr><td style="font-weight:500">${Utils.escapeHtml(prodNombre)}<br><small style="color:var(--text-muted)">${Utils.formatMoney(d.precio_unitario)} c/u</small></td><td class="text-center">${d.cantidad}</td><td class="text-center">${Utils.formatMoney(d.precio_unitario)}</td><td class="text-end fw-bold">${Utils.formatMoney(d.subtotal)}</td></tr>`;
        printHtml += `<tr><td style="padding:2px 0">${d.cantidad}</td><td style="padding:2px 0">${Utils.escapeHtml(prodNombre).toUpperCase()}</td><td class="text-right" style="padding:2px 0">${Number(d.subtotal || 0).toFixed(2)}</td></tr>`;
      });
      tbody.innerHTML = html;
      printTbody.innerHTML = printHtml;
    }

    const btnImp = document.getElementById('btnImprimirComprobante');
    if (btnImp) {
      btnImp.addEventListener('click', () => {
        Utils.imprimirComprobante(venta);
      });
    }
  }
};

