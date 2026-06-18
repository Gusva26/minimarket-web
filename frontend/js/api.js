const API = {
  baseURL: (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost')
    ? 'http://127.0.0.1:8000/api/'
    : 'https://<tudjango>.onrender.com/api/',

  async getToken() { return localStorage.getItem('access_token'); },

  async request(method, endpoint, data = null, isFormData = false, rawResponse = false) {
    const token = localStorage.getItem('access_token');
    const config = {
      method,
      headers: { ...(!isFormData && data ? {'Content-Type': 'application/json'} : {}), ...(token ? {'Authorization': `Bearer ${token}`} : {}) },
      body: isFormData ? data : (data ? JSON.stringify(data) : undefined),
    };

    let response = await fetch(this.baseURL + endpoint, config);

    if (response.status === 401 && token) {
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        const refreshRes = await fetch(this.baseURL + 'auth/refresh/', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({refresh})
        });
        if (refreshRes.ok) {
          const {access} = await refreshRes.json();
          localStorage.setItem('access_token', access);
          config.headers['Authorization'] = `Bearer ${access}`;
          response = await fetch(this.baseURL + endpoint, config);
        } else {
          localStorage.clear();
          window.location.hash = '#/login';
          throw new Error('Sesión expirada');
        }
      } else {
        localStorage.clear();
        window.location.hash = '#/login';
        throw new Error('Sesión expirada');
      }
    }

    if (rawResponse) return response;

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const json = await response.json();
      if (!response.ok) throw new Error(json.detail || JSON.stringify(json));
      return json;
    }
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response;
  },

  get: (e, r) => API.request('GET', e, null, false, r),
  post: (e, d, r) => API.request('POST', e, d, false, r),
  put: (e, d, r) => API.request('PUT', e, d, false, r),
  patch: (e, d, r) => API.request('PATCH', e, d, false, r),
  delete: (e, r) => API.request('DELETE', e, null, false, r),
  upload: (e, d) => API.request('POST', e, d, true),
};
