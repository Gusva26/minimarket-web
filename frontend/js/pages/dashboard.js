const DashboardPage = {
  async render(container) {
    container.innerHTML = `
      <div class="page-header">
        <h3><i class="fas fa-chart-pie text-gradient"></i>Dashboard</h3>
        <div class="page-actions">
          <button class="btn btn-primary btn-sm" onclick="window.location.hash='#/ventas'"><i class="fas fa-cart-shopping"></i>Nueva Venta</button>
          <button class="btn btn-accent btn-sm" onclick="window.location.hash='#/cajas'"><i class="fas fa-cash-register"></i>Cajas</button>
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
