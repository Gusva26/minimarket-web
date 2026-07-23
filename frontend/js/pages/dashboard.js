const DashboardPage = {
  async render(container) {
    const user = Auth.getUser();
    const userName = user ? (user.first_name || user.username) : 'Administrador';
    const userRole = user?.is_superuser ? 'Superadministrador' : 'Administrador de Sucursal';
    const ahora = new Date();
    const hora = ahora.getHours();
    const saludo = hora < 12 ? '¡Buenos días' : hora < 19 ? '¡Buenas tardes' : '¡Buenas noches';
    const fechaStr = ahora.toLocaleDateString('es-PE', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    const fechaFormateada = fechaStr.charAt(0).toUpperCase() + fechaStr.slice(1);

    container.innerHTML = `
      <div class="dashboard-hero-banner" style="background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); border-radius: 16px; padding: 1.75rem 2rem; color: white; margin-bottom: 1.5rem; box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.4); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; position: relative; overflow: hidden;">
        <div style="position: absolute; right: -20px; bottom: -30px; opacity: 0.12; font-size: 10rem; pointer-events: none;"><i class="fas fa-store"></i></div>
        <div style="z-index: 1;">
          <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.9; font-weight: 600; margin-bottom: 4px;">
            <i class="fas fa-calendar-day me-1"></i>${fechaFormateada}
          </div>
          <h2 style="font-weight: 800; font-size: 1.75rem; margin: 0; letter-spacing: -0.02em;">
            ${saludo}, ${Utils.escapeHtml(userName)}! 👋
          </h2>
          <p style="opacity: 0.88; font-size: 0.9rem; margin: 6px 0 0 0; font-weight: 500; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span class="badge bg-white text-dark fw-bold" style="padding: 4px 10px; border-radius: 20px; font-size: 0.75rem;"><i class="fas fa-shield-alt text-primary me-1"></i>${userRole}</span>
            <span>Monitoreo en tiempo real de ventas, inventario y caja.</span>
          </p>
        </div>
        <div style="z-index: 1; display: flex; gap: 10px; flex-wrap: wrap;">
          <button class="btn btn-light btn-pill fw-bold text-primary shadow-sm" onclick="window.location.hash='#/ventas'" style="padding: 0.65rem 1.25rem; border: none;">
            <i class="fas fa-cart-shopping me-1"></i>Ir a Caja POS
          </button>
          <button class="btn btn-outline-light btn-pill fw-bold shadow-sm" onclick="window.location.hash='#/cajas'" style="padding: 0.65rem 1.25rem;">
            <i class="fas fa-cash-register me-1"></i>Cajas
          </button>
        </div>
      </div>

      <div id="dash-content">
        <div class="kpi-grid" id="dashSkeleton">
          ${'<div class="skeleton skeleton-card"></div>'.repeat(4)}
        </div>
      </div>
    `;


    try {
      const data = await API.get('dashboard/');
      const dash = document.getElementById('dash-content');

      dash.innerHTML = `
        <div class="kpi-grid fade-in">
          <div class="kpi-card kpi-sales">
            <div class="kpi-top">
              <div class="kpi-icon"><i class="fas fa-chart-line"></i></div>
            </div>
            <div class="kpi-label">Ventas Hoy</div>
            <div class="kpi-value">${Utils.formatMoney(data.ventas_hoy)}</div>
            <div class="kpi-sub">Ingresos del día</div>
          </div>

          <div class="kpi-card kpi-stock">
            <div class="kpi-top">
              <div class="kpi-icon"><i class="fas fa-box"></i></div>
            </div>
            <div class="kpi-label">Stock Bajo</div>
            <div class="kpi-value">${data.productos_bajo_stock.length}</div>
            <div class="kpi-sub">Productos por reabastecer</div>
          </div>

          <div class="kpi-card kpi-expiry">
            <div class="kpi-top">
              <div class="kpi-icon"><i class="fas fa-clock"></i></div>
            </div>
            <div class="kpi-label">Próximos a Vencer</div>
            <div class="kpi-value">${data.proximos_vencer.length}</div>
            <div class="kpi-sub">Productos &le; 30 días</div>
          </div>

          <div class="kpi-card kpi-market">
            <div class="kpi-top">
              <div class="kpi-icon"><i class="fas fa-store"></i></div>
            </div>
            <div class="kpi-label">Sucursal</div>
            <div class="kpi-value" style="font-size:1.2rem">${data.mercado_nombre || 'N/A'}</div>
            <div class="kpi-sub">${data.caja_abierta_id ? '<span class="badge-success" style="display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:50px;font-size:.7rem"><span class="badge-dot badge-dot-success"></span>Caja abierta</span>' : '<span class="badge" style="display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:50px;font-size:.7rem;background:var(--danger-light);color:var(--danger)"><span class="badge-dot" style="display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--danger)"></span>Sin caja abierta</span>'}</div>
          </div>
        </div>

        <div class="dashboard-two-col">
          <div class="card card-accent">
            <div class="card-header">
              <i class="fas fa-exclamation-triangle" style="color:var(--warning)"></i>
              <h5>Stock Bajo</h5>
            </div>
            <div class="card-body" style="padding:0.75rem 1.25rem">
              ${data.productos_bajo_stock.length === 0
                ? '<div class="dashboard-empty"><i class="fas fa-check-circle"></i><p>Sin alertas de stock bajo</p></div>'
                : `<table class="alert-table"><tbody>
                    ${data.productos_bajo_stock.map(p => `
                      <tr>
                        <td>
                          <div class="product-name">${p.nombre}</div>
                          <div class="product-category">${p.categoria__nombre || 'Sin categoría'}</div>
                        </td>
                        <td style="text-align:right">
                          <div class="stock-value danger">${p.stock}</div>
                          <div style="font-size:.7rem;color:var(--text-muted)">min ${p.stock_minimo}</div>
                        </td>
                      </tr>
                    `).join('')}
                  </tbody></table>`
              }
            </div>
          </div>

          <div class="card card-danger">
            <div class="card-header">
              <i class="fas fa-clock" style="color:var(--danger)"></i>
              <h5>Próximos a Vencer</h5>
            </div>
            <div class="card-body" style="padding:0.75rem 1.25rem">
              ${data.proximos_vencer.length === 0
                ? '<div class="dashboard-empty"><i class="fas fa-check-circle"></i><p>Sin productos próximos a vencer</p></div>'
                : `<table class="alert-table"><tbody>
                    ${data.proximos_vencer.map(l => {
                      const cls = l.dias_para_vencer <= 7 ? 'danger' : 'warning';
                      return `
                        <tr>
                          <td>
                            <div class="product-name">${l.producto__nombre}</div>
                            <div class="product-category">${l.fecha_vencimiento}</div>
                          </td>
                          <td style="text-align:right">
                            <div class="stock-value ${cls}">${l.cantidad_actual}</div>
                            <div style="font-size:.7rem;color:var(--text-muted)">${l.dias_para_vencer}d</div>
                          </td>
                        </tr>
                      `;
                    }).join('')}
                  </tbody></table>`
              }
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <i class="fas fa-bolt" style="color:var(--accent)"></i>
            <h5>Acceso Rápido</h5>
          </div>
          <div class="card-body">
            <div class="quick-grid">
              <a href="#/ventas" class="quick-action">
                <div class="qa-icon" style="background:var(--success-light);color:var(--success)"><i class="fas fa-cart-shopping"></i></div>
                <span class="qa-label">Nueva Venta</span>
              </a>
              <a href="#/productos" class="quick-action">
                <div class="qa-icon" style="background:var(--accent-light);color:var(--accent)"><i class="fas fa-box"></i></div>
                <span class="qa-label">Productos</span>
              </a>
              <a href="#/compras" class="quick-action ${Auth.isAdmin() ? '' : 'd-none'}">
                <div class="qa-icon" style="background:var(--info-light);color:var(--info)"><i class="fas fa-truck"></i></div>
                <span class="qa-label">Compras</span>
              </a>
              <a href="#/cajas" class="quick-action">
                <div class="qa-icon" style="background:var(--warning-light);color:var(--warning)"><i class="fas fa-cash-register"></i></div>
                <span class="qa-label">Cajas</span>
              </a>
              <a href="#/reportes" class="quick-action ${Auth.isAdmin() ? '' : 'd-none'}">
                <div class="qa-icon" style="background:var(--danger-light);color:var(--danger)"><i class="fas fa-chart-line"></i></div>
                <span class="qa-label">Reportes</span>
              </a>
              <a href="#/kardex" class="quick-action ${Auth.isAdmin() ? '' : 'd-none'}">
                <div class="qa-icon" style="background:var(--primary-lighter);color:var(--primary)"><i class="fas fa-book"></i></div>
                <span class="qa-label">Kardex</span>
              </a>
            </div>
          </div>
        </div>
      `;
    } catch(e) {
      const dash = document.getElementById('dash-content');
      dash.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>${e.message}</div>`;
    }
  }
};
