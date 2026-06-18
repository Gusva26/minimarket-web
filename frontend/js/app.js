const App = {
  currentPage: null,
  _pageToken: 0,

  routes: {
    'login': { page: 'login', title: 'Iniciar Sesión', auth: false },
    'password-reset': { page: 'password-reset', title: 'Recuperar Contraseña', auth: false },
    'reset-password': { page: 'reset-password', title: 'Nueva Contraseña', auth: false },
    'dashboard': { page: 'dashboard', title: 'Dashboard', auth: true },
    'usuarios': { page: 'usuarios', title: 'Usuarios', auth: true, admin: true },
    'productos': { page: 'productos', title: 'Productos', auth: true },
    'categorias': { page: 'categorias', title: 'Categorías', auth: true },
    'kardex': { page: 'kardex', title: 'Kardex', auth: true, admin: true },
    'transferencias': { page: 'transferencias', title: 'Transferencias', auth: true },
    'vencimientos': { page: 'vencimientos', title: 'Vencimientos', auth: true },
    'valoracion': { page: 'valoracion', title: 'Valoración', auth: true, admin: true },
    'ventas': { page: 'ventas', title: 'Punto de Venta', auth: true },
    'ventas-historial': { page: 'historial', title: 'Historial de Ventas', auth: true },
    'ventas-detalle': { page: 'comprobante', title: 'Detalle de Venta', auth: true },
    'cajas': { page: 'cajas', title: 'Cajas', auth: true },
    'compras': { page: 'compras', title: 'Compras', auth: true, admin: true },
    'proveedores': { page: 'proveedores', title: 'Proveedores', auth: true, admin: true },
    'reportes': { page: 'reportes', title: 'Reportes', auth: true, admin: true },
    'section-gestion': { root: true },
    'section-ventas': { root: true },
    'section-admin': { root: true },
  },

  groupMap: {
    'gestion': ['productos','categorias','kardex','transferencias','vencimientos','valoracion'],
    'ventas': ['ventas','ventas-historial','ventas-detalle','cajas'],
    'admin': ['compras','proveedores','reportes','usuarios'],
  },

  async init() {
    this.navbar = new Navbar();
    await Auth.init();
    this.initSidebar();
    this.initTheme();
    this.initLogout();
    window.addEventListener('hashchange', () => this.handleRoute());
    // Only call handleRoute if there is no hash yet, otherwise hashchange will fire it
    if (!window.location.hash) {
      window.location.hash = '#/dashboard';
    } else {
      this.handleRoute();
    }
  },

  initSidebar() {
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (!toggle || !sidebar || !overlay) return;

    const mobileHamburger = document.getElementById('mobileHamburger');

    const openMobile = () => {
      sidebar.classList.add('mobile-open');
      overlay.classList.add('active');
    };

    const closeMobile = () => {
      sidebar.classList.remove('mobile-open');
      overlay.classList.remove('active');
    };

    const toggleCollapsed = () => {
      if (window.innerWidth <= 768) return;
      sidebar.classList.toggle('collapsed');
      localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
    };

    toggle.addEventListener('click', () => {
      if (window.innerWidth <= 768) {
        sidebar.classList.contains('mobile-open') ? closeMobile() : openMobile();
      } else {
        toggleCollapsed();
      }
    });

    document.querySelector('.sidebar-brand .brand-icon')?.addEventListener('click', toggleCollapsed);

    if (mobileHamburger) {
      mobileHamburger.addEventListener('click', openMobile);
    }

    overlay.addEventListener('click', closeMobile);

    // Auto-close mobile sidebar on link click
    sidebar.querySelectorAll('.sidebar-link').forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth <= 768) closeMobile();
      });
    });

    const savedCollapse = localStorage.getItem('sidebarCollapsed');
    if (savedCollapse === 'true' && window.innerWidth > 768) {
      sidebar.classList.add('collapsed');
    }

    // Section collapse toggles
    document.querySelectorAll('.sidebar-section-link').forEach(btn => {
      btn.addEventListener('click', () => {
        const section = btn.dataset.section;
        if (!section) return;
        const group = document.getElementById(`group-${section}`);
        const chevron = btn.querySelector('.sec-chevron');
        if (!group) return;
        const willClose = !group.classList.contains('closed');
        group.classList.toggle('closed');
        if (chevron) chevron.classList.toggle('open');
        localStorage.setItem(`section-${section}`, willClose ? 'closed' : 'open');
      });
    });

    // Restore section states
    ['gestion', 'ventas', 'admin'].forEach(s => {
      const state = localStorage.getItem(`section-${s}`);
      if (state === 'closed') {
        const group = document.getElementById(`group-${s}`);
        const btn = document.querySelector(`.sidebar-section-link[data-section="${s}"]`);
        if (group) group.classList.add('closed');
        if (btn) btn.querySelector('.sec-chevron')?.classList.remove('open');
      }
    });
  },

  initLogout() {
    const btn = document.getElementById('logoutBtn');
    if (!btn) return;
    btn.addEventListener('click', async () => {
      await Auth.logout();
      window.location.hash = '#/login';
    });
  },

  initTheme() {
    const toggle = document.getElementById('themeToggle');
    if (!toggle) return;

    const saved = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);
    this.updateThemeIcon(toggle, saved);

    toggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      this.updateThemeIcon(toggle, next);
    });
  },

  updateThemeIcon(btn, theme) {
    const icon = btn.querySelector('i');
    const text = btn.querySelector('span');
    if (theme === 'dark') {
      icon.className = 'fas fa-sun';
      text.textContent = 'Modo Claro';
    } else {
      icon.className = 'fas fa-moon';
      text.textContent = 'Modo Oscuro';
    }
  },

  savePageState() {
    const prev = this.currentPage;
    if (!prev) return;
    const container = document.getElementById('app-content');
    if (!container) return;
    const inputs = container.querySelectorAll('input, select, textarea');
    const state = {};
    inputs.forEach(el => {
      if (el.id) state[el.id] = el.value;
      else if (el.name) state[el.name] = el.value;
    });
    sessionStorage.setItem(`filters_${prev}`, JSON.stringify(state));
  },

  restorePageState(hash) {
    try {
      const saved = sessionStorage.getItem(`filters_${hash}`);
      if (!saved) return;
      const state = JSON.parse(saved);
      const container = document.getElementById('app-content');
      if (!container) return;
      // Restore after a short delay to let the page render
      requestAnimationFrame(() => {
        Object.entries(state).forEach(([id, val]) => {
          const el = container.querySelector(`#${CSS.escape(id)}`) || container.querySelector(`[name="${CSS.escape(id)}"]`);
          if (el && (el.tagName === 'INPUT' || el.tagName === 'SELECT' || el.tagName === 'TEXTAREA')) {
            el.value = val;
            el.dispatchEvent(new Event('change', { bubbles: true }));
          }
        });
      });
    } catch(e) { /* ignore */ }
  },

  isPageActive() {
    return this._pageToken;
  },

  async handleRoute() {
    this.savePageState();
    this._pageToken = Date.now() + Math.random();
    const pageToken = this._pageToken;

    let hash = window.location.hash.replace('#/', '') || 'dashboard';
    let params = {};

    const match = hash.match(/^([\w-]+)\/(\d+)$/);
    if (match) {
      params.id = match[2];
      const base = match[1];
      if (base === 'ventas' || base === 'ventas-detalle') hash = 'ventas-detalle';
      if (base === 'cajas') hash = 'cajas-detalle';
    }

    const resetMatch = hash.match(/^reset-password\/([\w-]+)\/([\w-]+)$/);
    if (resetMatch) {
      params.uid = resetMatch[1];
      params.token = resetMatch[2];
      hash = 'reset-password';
    }

    const route = this.routes[hash];
    if (!route) { window.location.hash = '#/dashboard'; return; }

    if (route.auth && !Auth.isAuthenticated()) { window.location.hash = '#/login'; return; }
    if (route.admin && !Auth.isAdmin()) { Utils.showToast('Acceso denegado', 'danger'); window.location.hash = '#/dashboard'; return; }

    const navEl = document.querySelector('.sidebar');
    if (navEl) navEl.style.display = route.auth ? '' : 'none';

    document.title = `${route.title} - Minimarket`;
    this.currentPage = hash;

    const container = document.getElementById('app-content');

    container.innerHTML = '<div class="loading-page"><div class="spinner-modern spinner-modern-lg"></div></div>';

    if (route.auth) {
      this.ensureSectionOpen(hash);
      this.navbar.render();
      this.navbar.highlight(hash);
    }

    Utils.clearModals();

    try {
      if (hash === 'ventas-detalle' && params.id) {
        await ComprobantePage.render(container, params.id);
      } else {
        const pageMap = {
          login: LoginPage, 'password-reset': PasswordResetPage, 'reset-password': ResetPasswordPage,
          dashboard: DashboardPage, usuarios: UsuariosPage,
          productos: ProductosPage, categorias: CategoriasPage, kardex: KardexPage,
          transferencias: TransferenciasPage, vencimientos: VencimientosPage,
          valoracion: ValoracionPage, ventas: VentasPage, 'ventas-historial': HistorialPage,
          cajas: CajasPage, compras: ComprasPage, proveedores: ProveedoresPage,
          reportes: ReportesPage,
        };
        if (pageMap[hash]) {
          container.classList.remove('page-enter');
          void container.offsetWidth;
          if (hash === 'reset-password') {
            await pageMap[hash].render(container, params);
          } else {
            await pageMap[hash].render(container);
          }
          if (this._pageToken !== pageToken) return;
          container.classList.add('page-enter');
          this.restorePageState(hash);
        } else {
          container.innerHTML = '<div class="empty-state"><div class="empty-icon"><i class="fas fa-map-signs"></i></div><div class="empty-title">Página no encontrada</div><div class="empty-desc">La página que buscas no existe.</div></div>';
        }
      }
    } catch(e) {
      if (this._pageToken !== pageToken) return;
      container.innerHTML = `<div class="alert alert-danger m-4"><i class="fas fa-exclamation-circle me-2"></i>${e.message}</div>`;
      console.error(e);
    }
  },

  ensureSectionOpen(hash) {
    for (const [section, routes] of Object.entries(this.groupMap)) {
      if (routes.includes(hash)) {
        const group = document.getElementById(`group-${section}`);
        const btn = document.querySelector(`.sidebar-section-link[data-section="${section}"]`);
        if (group && group.classList.contains('closed')) {
          group.classList.remove('closed');
          if (btn) btn.querySelector('.sec-chevron')?.classList.add('open');
          localStorage.setItem(`section-${section}`, 'open');
        }
        break;
      }
    }
  },
};

class Navbar {
  render() {
    const user = Auth.getUser();
    if (!user) return;
    document.getElementById('nav-user-name').textContent = user.first_name || user.username;
    document.getElementById('nav-user-role').textContent = user.rol || '';
    const avatar = document.getElementById('navUserAvatar');
    if (avatar) avatar.textContent = (user.first_name || user.username || 'U').charAt(0).toUpperCase();

    const isAdmin = Auth.isAdmin();
    document.querySelectorAll('.nav-admin-only').forEach(el => el.style.display = isAdmin ? '' : 'none');
  }

  highlight(route) {
    document.querySelectorAll('.sidebar-link').forEach(a => a.classList.remove('active'));
    const link = document.querySelector(`.sidebar-link[data-route="${route}"]`);
    if (link) link.classList.add('active');
  }
}

document.addEventListener('DOMContentLoaded', () => App.init());
