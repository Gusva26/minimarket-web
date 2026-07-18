const Auth = {
  async login(username, password) {
    const data = await API.post('auth/login/', {username, password});
    localStorage.setItem('logged_in', 'true');
    await this.loadUser();
    return true;
  },

  async loadUser() {
    try {
      const user = await API.get('auth/me/');
      localStorage.setItem('user', JSON.stringify(user));
      return user;
    } catch { return null; }
  },

  getUser() {
    try { return JSON.parse(localStorage.getItem('user')); } catch { return null; }
  },

  isAuthenticated() { return localStorage.getItem('logged_in') === 'true'; },

  isAdmin() { const u = this.getUser(); return u && (u.is_admin || u.is_superuser); },

  async logout() {
    try {
      await API.post('auth/logout/');
    } catch (e) {
      console.error("Logout error:", e);
    }
    localStorage.removeItem('logged_in');
    localStorage.removeItem('user');
    window.location.hash = '#/login';
  },

  async init() {
    if (this.isAuthenticated()) {
      const user = await this.loadUser();
      if (!user) {
        localStorage.removeItem('logged_in');
        localStorage.removeItem('user');
        window.location.hash = '#/login';
      }
    }
  }
};
