const VentasPage = {
  productos: [],
  carrito: {},

  render: async function(container) {
    const loading = Utils.showLoading();
    try {
      const dashData = await API.get('dashboard/');
      if (!dashData.caja_abierta_id) {
        loading.close();
        Utils.showToast('Debe abrir caja antes de ingresar al POS', 'warning');
        window.location.hash = '#/dashboard';
        return;
      }
    } catch (e) {
      console.error('Error verificando caja', e);
    } finally {
      loading.close();
    }

    this.carrito = this.obtenerCarrito();
    container.innerHTML = `
      <div class="row g-4">
        <div class="col-lg-8">
          <div class="card p-4 mb-4">
            <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
              <div>
                <h4 class="fw-bold mb-0"><i class="fas fa-store me-2 text-gradient"></i>Catálogo de Productos</h4>
                <p style="color:var(--text-muted);font-size:.85rem;margin:0">Selecciona los productos para agregar al carrito</p>
              </div>
              <div class="search-bar" style="min-width:280px">
                <i class="fas fa-search search-icon"></i>
                <input type="text" id="buscarProducto" class="form-control" placeholder="Buscar por nombre o código...">
              </div>
            </div>
            <div class="mt-4 overflow-auto">
              <div class="d-flex gap-2 pb-2" id="categoriaFiltros"></div>
            </div>
          </div>
          <div class="row row-cols-2 row-cols-sm-3 row-cols-md-4 row-cols-xl-5 g-3" id="productosGrid"></div>
        </div>
        <div class="col-lg-4">
          <div class="card" style="position:sticky;top:1rem;max-height:calc(100vh - 2rem);overflow-y:auto">
            <div class="card-header">
              <i class="fas fa-shopping-basket" style="color:var(--accent)"></i>
              <h5 class="mb-0">Orden Actual</h5>
              <span class="badge badge-accent" id="cartCount" style="margin-left:auto">0 items</span>
              <button class="btn btn-sm btn-icon btn-ghost" id="btnVaciarCarrito" title="Vaciar carrito" style="display:none;color:var(--danger)"><i class="fas fa-trash-alt"></i></button>
            </div>
            <div class="card-body" id="cartItems"></div>
            <div class="card-header" style="flex-direction:column;gap:12px">
              <div class="d-flex justify-content-between align-items-center w-100">
                <span style="font-size:.75rem;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:.03em">Total a Pagar</span>
                <h4 class="mb-0 fw-bold" style="color:var(--primary)" id="cartTotal">S/ 0.00</h4>
              </div>
              <button class="btn btn-primary w-100 py-3" id="btnPagar" disabled>
                <i class="fas fa-credit-card"></i>Proceder al Pago
              </button>
            </div>
          </div>
        </div>
      </div>
      ${this.modalCheckoutHTML()}
    `;
    await this.cargarProductos();
    this.renderCarrito();
    this.bindEvents();
  },

  modalCheckoutHTML: function() {
    return `
    <div class="modal-overlay" id="checkoutModal">
      <div class="modal-card" style="max-width:560px">
        <div class="modal-card-header">
          <h5><i class="fas fa-receipt me-2"></i>Finalizar Venta</h5>
          <button class="modal-close" onclick="Utils.hideModal('checkoutModal')"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-card-body">
          <div class="text-center mb-3">
            <span class="badge badge-accent" style="font-size:.75rem;padding:0.35rem 1.2rem">Total de la Orden</span>
            <h2 class="fw-bold" style="color:var(--primary);margin-top:8px" id="modalTotal">S/ 0.00</h2>
          </div>
          <h6 style="font-size:.75rem;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:12px">Información de Facturación</h6>
          <div class="row g-2 mb-3">
            <div class="col-md-4">
              <div class="form-group">
                <label class="form-label">Comprobante</label>
                <select class="form-select" id="tipo_comprobante">
                  <option value="TICKET">Ticket</option>
                  <option value="BOLETA">Boleta</option>
                  <option value="FACTURA">Factura</option>
                </select>
              </div>
            </div>
            <div class="col-md-3">
              <div class="form-group">
                <label class="form-label">Tipo Doc.</label>
                <select class="form-select" id="cliente_tipo_doc">
                  <option value="DNI">DNI</option>
                  <option value="RUC">RUC</option>
                </select>
              </div>
            </div>
            <div class="col-md-5">
              <div class="form-group">
                <label class="form-label">N° Documento</label>
                <div class="input-group">
                  <input type="text" class="form-control" id="cliente_documento" placeholder="Ej: 12345678" maxlength="11">
                  <button class="btn btn-primary" type="button" id="btnConsultarCliente"><i class="fas fa-search"></i></button>
                </div>
              </div>
            </div>
          </div>
          <div id="cliente_data" class="d-none mb-3">
            <div class="form-group">
              <label class="form-label">Nombre o Razón Social</label>
              <input type="text" class="form-control" id="cliente_nombre" placeholder="Ej: Juan Pérez o Distribuidora Alimentos EIRL">
            </div>
            <div class="form-group" id="container_direccion_fiscal">
              <label class="form-label">Dirección Fiscal</label>
              <input type="text" class="form-control" id="cliente_direccion" placeholder="Ej: Av. Principal 123, Lima">
            </div>
          </div>
          <h6 style="font-size:.75rem;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:12px">Descuento</h6>
          <div class="form-group mb-3">
            <label class="form-label">Descuento Global (S/)</label>
            <input type="number" step="0.01" min="0" class="form-control" id="descuento_global" placeholder="0.00" value="0.00" autocomplete="off">
          </div>
          <h6 style="font-size:.75rem;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:12px">Método de Pago</h6>
          <div class="row g-2 justify-content-center mb-3">
            <div class="col-4">
              <input type="radio" class="btn-check" name="metodo_pago" id="pago_efectivo" value="Efectivo" checked>
              <label class="btn btn-outline-primary w-100 p-3" for="pago_efectivo" style="border-radius:var(--radius);text-align:center"><i class="fas fa-coins fa-2x mb-1 d-block"></i><small>Efectivo</small></label>
            </div>
            <div class="col-4">
              <input type="radio" class="btn-check" name="metodo_pago" id="pago_yape" value="Yape">
              <label class="btn btn-outline-info w-100 p-3" for="pago_yape" style="border-radius:var(--radius);text-align:center"><i class="fas fa-mobile-alt fa-2x mb-1 d-block"></i><small>Yape</small></label>
            </div>
            <div class="col-4">
              <input type="radio" class="btn-check" name="metodo_pago" id="pago_plin" value="Plin">
              <label class="btn btn-outline-warning w-100 p-3" for="pago_plin" style="border-radius:var(--radius);text-align:center"><i class="fas fa-qrcode fa-2x mb-1 d-block"></i><small>Plin</small></label>
            </div>
          </div>
          <div id="pago_efectivo_container">
            <div class="form-group">
              <label class="form-label">Monto Recibido (S/)</label>
              <input type="number" step="0.01" class="form-control" style="font-size:1.5rem;font-weight:700" id="monto_recibido" placeholder="0.00" autocomplete="off">
            </div>
            <div id="vuelto_display_container"></div>
          </div>
          <div id="pago_digital_container" class="d-none">
            <div class="form-group">
              <label class="form-label">N° Operación <span class="text-danger">*</span></label>
              <input type="text" class="form-control" id="num_operacion" placeholder="Ej: 123ABC (código de la transferencia)">
            </div>
          </div>
          <div style="background:var(--surface-hover);border-radius:var(--radius);padding:1rem;margin-top:12px">
            <div class="d-flex justify-content-between small mb-1"><span>Subtotal</span><span id="checkoutSubtotal">S/ 0.00</span></div>
            <div class="d-flex justify-content-between small mb-1"><span>IGV (18%)</span><span id="checkoutIgv">S/ 0.00</span></div>
            <hr style="margin:8px 0;border-color:var(--border)">
            <div class="d-flex justify-content-between fw-bold"><span>Total</span><span id="checkoutTotal">S/ 0.00</span></div>
          </div>
        </div>
        <div class="modal-card-footer">
          <button class="btn btn-ghost" onclick="Utils.hideModal('checkoutModal')">Regresar</button>
          <button class="btn btn-primary" id="btnConfirmarVenta" style="padding-left:2rem;padding-right:2rem">Completar Venta</button>
        </div>
      </div>
    </div>`;
  },

  obtenerCarrito: function() {
    try { return JSON.parse(localStorage.getItem('pos_carrito')) || {}; } catch { return {}; }
  },

  guardarCarrito: function() {
    localStorage.setItem('pos_carrito', JSON.stringify(this.carrito));
  },

  agregarAlCarrito: function(id, nombre, precio, imagen) {
    const key = String(id);
    if (this.carrito[key]) {
      this.carrito[key].cantidad += 1;
    } else {
      this.carrito[key] = { nombre, precio: parseFloat(precio), cantidad: 1, imagen: imagen || '' };
    }
    this.guardarCarrito();
    this.renderCarrito();
  },

  actualizarCantidad: function(id, cantidad) {
    cantidad = parseFloat(cantidad) || 0;
    const key = String(id);
    if (cantidad <= 0) {
      delete this.carrito[key];
    } else {
      this.carrito[key].cantidad = cantidad;
    }
    this.guardarCarrito();
    this.renderCarrito();
  },

  vaciarCarrito: function() {
    this.carrito = {};
    this.guardarCarrito();
    this.renderCarrito();
    Utils.showToast('Carrito vaciado', 'success');
  },

  renderCarrito: function() {
    const items = document.getElementById('cartItems');
    const totalEl = document.getElementById('cartTotal');
    const countEl = document.getElementById('cartCount');
    const btnPagar = document.getElementById('btnPagar');
    const btnVaciar = document.getElementById('btnVaciarCarrito');
    if (!items) return;

    let html = '', count = 0, total = 0;
    for (const [id, item] of Object.entries(this.carrito)) {
      const subtotal = item.precio * item.cantidad;
      total += subtotal;
      count += item.cantidad;
      html += `
      <div class="d-flex align-items-center mb-2 p-2" style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius)">
        <div class="flex-grow-1 me-2" style="min-width:0">
          <small class="fw-bold d-block text-truncate">${Utils.escapeHtml(item.nombre)}</small>
          <small style="color:var(--text-muted)">${Utils.formatMoney(item.precio)}</small>
        </div>
        <div class="d-flex align-items-center" style="background:var(--surface-hover);border-radius:50px;padding:2px;border:1px solid var(--border)">
          <button class="btn btn-sm btn-icon btn-ghost" onclick="VentasPage.actualizarCantidad(${id}, ${item.cantidad - 1})" style="color:var(--danger);border:none"><i class="fas fa-minus-circle"></i></button>
          <input type="number" class="form-control form-control-sm text-center fw-bold" value="${item.cantidad}" min="0" step="0.01" style="width:48px;border:none;background:transparent;font-size:.85rem;padding:2px" onchange="VentasPage.actualizarCantidad(${id}, this.value)">
          <button class="btn btn-sm btn-icon btn-ghost" onclick="VentasPage.actualizarCantidad(${id}, ${item.cantidad + 1})" style="color:var(--success);border:none"><i class="fas fa-plus-circle"></i></button>
        </div>
        <div class="text-end ms-2" style="min-width:65px"><small class="fw-bold">${Utils.formatMoney(subtotal)}</small></div>
        <button class="btn btn-sm btn-icon btn-ghost" onclick="VentasPage.actualizarCantidad(${id}, 0)" style="color:var(--text-muted);border:none"><i class="fas fa-times"></i></button>
      </div>`;
    }

    if (Object.keys(this.carrito).length === 0) {
      html = '<div class="empty-state py-5" style="min-height:200px"><div class="empty-icon"><i class="fas fa-shopping-cart"></i></div><div class="empty-title">El carrito está vacío</div><div class="empty-desc">Agregue productos del catálogo</div></div>';
      btnPagar.disabled = true;
      btnVaciar.style.display = 'none';
    } else {
      btnPagar.disabled = false;
      btnVaciar.style.display = '';
    }

    items.innerHTML = html;
    countEl.textContent = `${count.toFixed(2)} productos`;
    totalEl.textContent = Utils.formatMoney(total);

    // Dynamic micro-animation feedback
    if (count > 0) {
      countEl.classList.remove('pulse-scale');
      totalEl.classList.remove('pulse-scale');
      void countEl.offsetWidth; // Trigger DOM reflow to restart animation
      void totalEl.offsetWidth;
      countEl.classList.add('pulse-scale');
      totalEl.classList.add('pulse-scale');
    }
  },

  cargarProductos: async function() {
    const loading = Utils.showLoading();
    try {
      const data = await API.get('productos/?page_size=1000');
      const productos = data.results || data;

      this.productos = productos.filter(p => parseFloat(p.stock) > 0);
      this.renderizarCategorias();
      this.renderizarProductos(this.productos);
    } catch (e) {
      Utils.showToast('Error al cargar productos: ' + e.message, 'danger');
    } finally {
      loading.close();
    }
  },

  renderizarCategorias: function() {
    const container = document.getElementById('categoriaFiltros');
    if (!container) return;
    const categorias = [...new Set(this.productos.map(p => p.categoria ? p.categoria.id : null).filter(Boolean))];
    const nombres = {};
    this.productos.forEach(p => { if (p.categoria) nombres[p.categoria.id] = p.categoria.nombre; });
    let html = '<button class="btn btn-primary btn-sm btn-pill filter-btn active" data-categoria="todos">Todos</button>';
    categorias.forEach(id => {
      html += `<button class="btn btn-ghost btn-sm btn-pill filter-btn" data-categoria="${id}">${nombres[id] || id}</button>`;
    });
    container.innerHTML = html;
    container.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        container.querySelectorAll('.filter-btn').forEach(b => { b.className = 'btn btn-ghost btn-sm btn-pill filter-btn'; });
        this.className = 'btn btn-primary btn-sm btn-pill filter-btn';
        VentasPage.filtrarProductos();
      });
    });
  },

  renderizarProductos: function(productos) {
    const grid = document.getElementById('productosGrid');
    if (!grid) return;
    if (!productos || productos.length === 0) {
      grid.innerHTML = '<div class="col-12 text-center py-5"><div class="empty-state"><div class="empty-icon"><i class="fas fa-box-open"></i></div><div class="empty-title">No hay productos disponibles</div></div></div>';
      return;
    }
    let html = '';
    productos.forEach(p => {
      const catId = p.categoria ? p.categoria.id : 'none';
      const stock = parseFloat(p.stock) || 0;
      const stockMin = parseFloat(p.stock_minimo) || 5;
      const outOfStock = stock <= 0;
      const lowStock = stock < stockMin;
      const stockBadgeClass = outOfStock ? 'badge-danger' : (lowStock ? 'badge-warning' : 'badge-info');

      html += `
      <div class="col producto-item" data-categoria="${catId}">
        <div class="card card-flush" style="cursor:pointer;height:100%;display:flex;flex-direction:column;overflow:hidden" onclick='VentasPage.agregarAlCarrito(${p.id}, ${Utils.escapeHtml(JSON.stringify(p.nombre))}, ${p.precio}, ${Utils.escapeHtml(JSON.stringify(p.imagen || ''))})'>
          <div style="height:120px;display:flex;align-items:center;justify-content:center;background:var(--surface-hover);padding:.5rem">
            ${p.imagen ? `<img src="${p.imagen}" style="max-height:110px;max-width:100%;object-fit:contain" alt="${Utils.escapeHtml(p.nombre)}">` : '<div style="opacity:.15;color:var(--text-muted)"><i class="fas fa-box fa-3x"></i></div>'}
          </div>
          <div style="padding:.6rem;text-align:center;flex:1;display:flex;flex-direction:column;justify-content:space-between">
            <div style="font-size:.8rem;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${Utils.escapeHtml(p.nombre)}">${Utils.escapeHtml(p.nombre)}</div>
            <div class="mt-1">
              <div style="font-weight:700;color:var(--primary)">${Utils.formatMoney(p.precio)}</div>
              <span class="badge ${stockBadgeClass}" style="display:block;margin-top:4px;font-size:.65rem">Stock: ${p.stock}</span>
            </div>
          </div>
        </div>
      </div>`;
    });
    grid.innerHTML = html;
  },

  filtrarProductos: function() {
    const searchInput = document.getElementById('buscarProducto');
    const search = searchInput ? searchInput.value.toLowerCase() : '';
    const catBtn = document.querySelector('#categoriaFiltros .btn-primary.filter-btn');
    const categoria = catBtn ? catBtn.dataset.categoria : 'todos';
    const filtered = this.productos.filter(p => {
      const matchSearch = !search || p.nombre.toLowerCase().includes(search) || (p.codigo_barras && p.codigo_barras.toLowerCase().includes(search));
      const matchCat = categoria === 'todos' || (p.categoria && String(p.categoria.id) === categoria);
      return matchSearch && matchCat;
    });
    this.renderizarProductos(filtered);
  },

  bindEvents: function() {
    // 1. Buscador con soporte de escáner de códigos de barra (Enter)
    const buscarInput = document.getElementById('buscarProducto');
    if (buscarInput) {
      buscarInput.addEventListener('input', () => this.filtrarProductos());
      buscarInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          const query = buscarInput.value.trim().toLowerCase();
          if (!query) return;

          // Buscar coincidencia exacta por código de barras o nombre
          const match = this.productos.find(p => 
            (p.codigo_barras && p.codigo_barras.toLowerCase() === query) ||
            (p.nombre.toLowerCase() === query)
          );

          if (match) {
            this.agregarAlCarrito(match.id, match.nombre, match.precio, match.imagen || '');
            buscarInput.value = '';
            this.filtrarProductos();
            Utils.showToast(`${match.nombre} agregado al carrito`, 'success');
          } else {
            // Si no hay coincidencia exacta, verificar si el filtro arroja exactamente un único producto
            const filtered = this.productos.filter(p => 
              p.nombre.toLowerCase().includes(query) || (p.codigo_barras && p.codigo_barras.toLowerCase().includes(query))
            );
            if (filtered.length === 1) {
              const single = filtered[0];
              this.agregarAlCarrito(single.id, single.nombre, single.precio, single.imagen || '');
              buscarInput.value = '';
              this.filtrarProductos();
              Utils.showToast(`${single.nombre} agregado al carrito`, 'success');
            }
          }
        }
      });
    }

    const btnVaciarCarrito = document.getElementById('btnVaciarCarrito');
    if (btnVaciarCarrito) {
      btnVaciarCarrito.addEventListener('click', () => {
        Utils.showConfirm('Vaciar Carrito', 'Se eliminarán todos los productos del carrito.', 'Sí, vaciar')
          .then(result => { if (result.isConfirmed) this.vaciarCarrito(); });
      });
    }

    const updateCheckout = () => {
      const totalCarrito = Object.values(this.carrito).reduce((s, i) => s + i.precio * i.cantidad, 0);
      const discountInput = document.getElementById('descuento_global');
      let descuento = 0;
      if (discountInput) {
        descuento = parseFloat(discountInput.value) || 0;
        if (descuento < 0) {
          descuento = 0;
          discountInput.value = '0.00';
        }
        if (descuento > totalCarrito) {
          descuento = totalCarrito;
          discountInput.value = totalCarrito.toFixed(2);
        }
      }
      
      const totalNeto = Math.max(0, totalCarrito - descuento);
      
      const modalTotal = document.getElementById('modalTotal');
      if (modalTotal) modalTotal.textContent = Utils.formatMoney(totalNeto);
      
      const checkoutSubtotal = document.getElementById('checkoutSubtotal');
      if (checkoutSubtotal) checkoutSubtotal.textContent = Utils.formatMoney(totalNeto / 1.18);
      
      const checkoutIgv = document.getElementById('checkoutIgv');
      if (checkoutIgv) checkoutIgv.textContent = Utils.formatMoney(totalNeto - totalNeto / 1.18);
      
      const checkoutTotal = document.getElementById('checkoutTotal');
      if (checkoutTotal) checkoutTotal.textContent = Utils.formatMoney(totalNeto);

      const inputRecibido = document.getElementById('monto_recibido');
      if (inputRecibido) {
        const recibido = parseFloat(inputRecibido.value) || 0;
        const vueltoDisplay = document.getElementById('vuelto_display_container');
        if (vueltoDisplay) {
          if (recibido === 0) {
            vueltoDisplay.innerHTML = '';
          } else {
            const vuelto = recibido - totalNeto;
            if (vuelto >= 0) {
              vueltoDisplay.innerHTML = `
                <div class="alert alert-success mt-2 d-flex justify-content-between align-items-center py-2 fade-in" style="border-radius:var(--radius);font-weight:600;margin-bottom:0">
                  <span>Cambio a entregar:</span>
                  <span style="font-size:1.25rem">${Utils.formatMoney(vuelto)}</span>
                </div>`;
            } else {
              vueltoDisplay.innerHTML = `
                <div class="alert alert-danger mt-2 d-flex justify-content-between align-items-center py-2 fade-in" style="border-radius:var(--radius);font-weight:600;margin-bottom:0">
                  <span>Falta cubrir:</span>
                  <span style="font-size:1.25rem">${Utils.formatMoney(Math.abs(vuelto))}</span>
                </div>`;
            }
          }
        }
      }
    };

    const btnPagar = document.getElementById('btnPagar');
    if (btnPagar) {
      btnPagar.addEventListener('click', () => {
        const discountInput = document.getElementById('descuento_global');
        if (discountInput) discountInput.value = '0.00';
        
        updateCheckout();

        const inputRecibido = document.getElementById('monto_recibido');
        if (inputRecibido) inputRecibido.value = '';
        const vueltoDisplay = document.getElementById('vuelto_display_container');
        if (vueltoDisplay) vueltoDisplay.innerHTML = '';

        document.getElementById('pago_efectivo').checked = true;
        document.getElementById('pago_efectivo_container').style.display = '';
        document.getElementById('pago_digital_container').classList.add('d-none');

        Utils.showModal('checkoutModal');

        setTimeout(() => {
          if (inputRecibido) {
            inputRecibido.focus();
            inputRecibido.select();
          }
        }, 150);
      });
    }

    const discountInput = document.getElementById('descuento_global');
    if (discountInput) {
      discountInput.addEventListener('input', updateCheckout);
    }

    const inputRecibido = document.getElementById('monto_recibido');
    if (inputRecibido) {
      inputRecibido.addEventListener('input', updateCheckout);
    }

    document.querySelectorAll('input[name="metodo_pago"]').forEach(r => {
      r.addEventListener('change', function() {
        const efectivo = document.getElementById('pago_efectivo_container');
        const digital = document.getElementById('pago_digital_container');
        if (this.value === 'Efectivo') {
          efectivo.style.display = '';
          digital.classList.add('d-none');
          setTimeout(() => {
            const input = document.getElementById('monto_recibido');
            if (input) { input.focus(); input.select(); }
          }, 50);
        } else {
          efectivo.style.display = 'none';
          digital.classList.remove('d-none');
          setTimeout(() => {
            const input = document.getElementById('num_operacion');
            if (input) { input.focus(); input.select(); }
          }, 50);
        }
      });
    });

    const tipoComprobante = document.getElementById('tipo_comprobante');
    if (tipoComprobante) {
      tipoComprobante.addEventListener('change', function() {
        const data = document.getElementById('cliente_data');
        const tipoDoc = document.getElementById('cliente_tipo_doc');
        if (this.value === 'TICKET') {
          data.classList.add('d-none');
        } else {
          data.classList.remove('d-none');
          tipoDoc.value = this.value === 'FACTURA' ? 'RUC' : 'DNI';
          tipoDoc.dispatchEvent(new Event('change'));
        }
      });
    }

    const clienteTipoDoc = document.getElementById('cliente_tipo_doc');
    if (clienteTipoDoc) {
      clienteTipoDoc.addEventListener('change', function() {
        const containerDir = document.getElementById('container_direccion_fiscal');
        if (this.value === 'DNI') {
          containerDir.classList.add('d-none');
        } else {
          containerDir.classList.remove('d-none');
        }
        document.getElementById('cliente_documento').placeholder = this.value === 'RUC' ? 'Ej: 20123456789' : 'Ej: 12345678';
      });
    }

    const btnConsultarCliente = document.getElementById('btnConsultarCliente');
    if (btnConsultarCliente) {
      btnConsultarCliente.addEventListener('click', async function() {
        const doc = document.getElementById('cliente_documento').value.trim();
        if (doc.length < 8) { Utils.showToast('Ingrese un documento válido (mín. 8 dígitos)', 'warning'); return; }
        try {
          this.disabled = true;
          this.innerHTML = '<div class="spinner" style="margin:0"></div>';
          const data = await API.get(`clientes/consultar-documento/?documento=${doc}`);
          document.getElementById('cliente_nombre').value = data.nombre || '';
          document.getElementById('cliente_direccion').value = data.direccion || '';
          document.getElementById('cliente_data').classList.remove('d-none');
          if (data.nombre) Utils.showToast('Cliente encontrado', 'success');
        } catch (e) {
          document.getElementById('cliente_data').classList.remove('d-none');
          Utils.showToast('Cliente no encontrado, puede llenar manualmente', 'warning');
        } finally {
          this.disabled = false;
          this.innerHTML = '<i class="fas fa-search"></i>';
        }
      });
    }

    const btnConfirmarVenta = document.getElementById('btnConfirmarVenta');
    if (btnConfirmarVenta) btnConfirmarVenta.addEventListener('click', async () => this.procesarVenta());

    // 3. Atajos de Teclado Globales (F2, F4, F8, F9, F10, Esc, Enter)
    this.keyListener = (e) => {
      if (window.location.hash !== '#/ventas') {
        document.removeEventListener('keydown', this.keyListener);
        return;
      }

      // F2: Enfocar buscador
      if (e.key === 'F2') {
        e.preventDefault();
        const searchInput = document.getElementById('buscarProducto');
        if (searchInput) {
          searchInput.focus();
          searchInput.select();
        }
      }

      // F4: Proceder al Pago (Checkout)
      if (e.key === 'F4') {
        e.preventDefault();
        const btnPagar = document.getElementById('btnPagar');
        if (btnPagar && !btnPagar.disabled) {
          btnPagar.click();
        }
      }

      // Atajos activos solo si el modal está abierto
      const modal = document.getElementById('checkoutModal');
      if (modal && modal.classList.contains('active')) {
        // F8: Efectivo
        if (e.key === 'F8') {
          e.preventDefault();
          const radio = document.getElementById('pago_efectivo');
          if (radio) {
            radio.checked = true;
            radio.dispatchEvent(new Event('change'));
          }
        }
        // F9: Yape
        if (e.key === 'F9') {
          e.preventDefault();
          const radio = document.getElementById('pago_yape');
          if (radio) {
            radio.checked = true;
            radio.dispatchEvent(new Event('change'));
          }
        }
        // F10: Plin
        if (e.key === 'F10') {
          e.preventDefault();
          const radio = document.getElementById('pago_plin');
          if (radio) {
            radio.checked = true;
            radio.dispatchEvent(new Event('change'));
          }
        }
        // Escape: Cerrar modal
        if (e.key === 'Escape') {
          e.preventDefault();
          Utils.hideModal('checkoutModal');
        }
        // Enter: Enviar formulario
        if (e.key === 'Enter' && (e.target.id === 'monto_recibido' || e.target.id === 'num_operacion' || e.target.id === 'cliente_documento' || e.target.id === 'cliente_nombre')) {
          e.preventDefault();
          const btnConfirmar = document.getElementById('btnConfirmarVenta');
          if (btnConfirmar && !btnConfirmar.disabled) {
            btnConfirmar.click();
          }
        }
      }
    };

    document.removeEventListener('keydown', this.keyListener);
    document.addEventListener('keydown', this.keyListener);
  },

  procesarVenta: async function() {
    const items = Object.entries(this.carrito).map(([id, item]) => ({
      producto_id: parseInt(id),
      cantidad: item.cantidad,
      precio_unitario: item.precio
    }));

    if (items.length === 0) { Utils.showToast('El carrito está vacío', 'warning'); return; }

    const metodo_pago = document.querySelector('input[name="metodo_pago"]:checked').value;
    const tipo_comprobante = document.getElementById('tipo_comprobante').value;
    const total_carrito = Object.values(this.carrito).reduce((s, i) => s + i.precio * i.cantidad, 0);
    const descuento = parseFloat(document.getElementById('descuento_global').value) || 0;
    const total_neto = Math.max(0, total_carrito - descuento);
    let monto_recibido = 0, vuelto = 0, num_operacion = '';

    if (metodo_pago === 'Efectivo') {
      monto_recibido = parseFloat(document.getElementById('monto_recibido').value) || 0;
      if (monto_recibido < total_neto) { Utils.showToast('El monto recibido debe cubrir el total de la venta', 'warning'); return; }
      vuelto = monto_recibido - total_neto;
    } else {
      num_operacion = document.getElementById('num_operacion').value.trim();
      if (!num_operacion) { Utils.showToast('El número de operación es obligatorio para pagos digitales', 'warning'); return; }
    }

    if (tipo_comprobante === 'FACTURA') {
      const doc = document.getElementById('cliente_documento').value.trim();
      const nombre = document.getElementById('cliente_nombre').value.trim();
      if (!doc || doc.length < 11) { Utils.showToast('Ingrese un RUC válido (11 dígitos) para Factura', 'warning'); return; }
      if (!nombre) { Utils.showToast('El nombre o razón social es obligatorio para Factura', 'warning'); return; }
    } else if (tipo_comprobante === 'BOLETA') {
      const doc = document.getElementById('cliente_documento').value.trim();
      if (doc && doc.length !== 8) { Utils.showToast('El DNI debe tener 8 dígitos', 'warning'); return; }
    }

    const cliente = {};
    if (tipo_comprobante !== 'TICKET') {
      cliente.num_documento = document.getElementById('cliente_documento').value.trim();
      cliente.nombre = document.getElementById('cliente_nombre').value.trim();
      cliente.direccion = document.getElementById('cliente_direccion').value.trim();
    }

    const payload = {
      metodo_pago,
      tipo_comprobante,
      monto_recibido,
      vuelto,
      num_operacion,
      cliente_data: Object.keys(cliente).length ? cliente : null,
      descuento,
      items
    };

    const loading = Utils.showLoading();
    try {
      const result = await API.post('ventas/', payload);
      this.vaciarCarrito();
      
      // Invalidate local catalog cache after sale to update stock
      const mercadoId = Auth.getUser().mercado_id;
      localStorage.removeItem(`pos_catalog_mercado_${mercadoId}`);
      localStorage.removeItem(`pos_catalog_mercado_${mercadoId}_timestamp`);

      Utils.hideModal('checkoutModal');
      Utils.showToast('Venta realizada con éxito', 'success');
      window.location.hash = `#/ventas-detalle/${result.id}`;
    } catch (e) {
      Utils.showToast('Error al procesar venta: ' + e.message, 'danger');
    } finally {
      loading.close();
    }
  }
};
