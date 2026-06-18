const Auth = {
  async login(username, password) {
    const data = await API.post('auth/login/', {username, password});
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
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

  isAuthenticated() { return !!localStorage.getItem('access_token'); },

  isAdmin() { const u = this.getUser(); return u && (u.is_admin || u.is_superuser); },

  async logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.hash = '#/login';
  },

  async init() {
    if (this.isAuthenticated()) {
      await this.loadUser();
    }
  }
};
