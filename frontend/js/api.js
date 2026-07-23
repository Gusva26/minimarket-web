const API = {
  baseURL: (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost')
    ? `http://${window.location.hostname}:8000/api/`
    : 'https://minimarket-backend-t8ai.onrender.com/api/',

  _cacheMap: new Map(),

  clearCache() {
    this._cacheMap.clear();
  },

  async getToken() { return null; },

  async request(method, endpoint, data = null, isFormData = false, rawResponse = false) {
    // Clear cache on any data modification
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method.toUpperCase())) {
      this.clearCache();
    }

    // Direct live request to backend (Backend manages versioned caching)


    const config = {
      method,
      headers: !isFormData && data ? {'Content-Type': 'application/json'} : {},
      body: isFormData ? data : (data ? JSON.stringify(data) : undefined),
      credentials: 'include'
    };

    let response = await fetch(this.baseURL + endpoint, config);

    if (response.status === 401 && !endpoint.includes('auth/login') && !endpoint.includes('auth/refresh')) {
      try {
        const refreshRes = await fetch(this.baseURL + 'auth/refresh/', {
          method: 'POST',
          credentials: 'include',
        });
        if (refreshRes.ok) {
          response = await fetch(this.baseURL + endpoint, config);
        } else {
          localStorage.removeItem('logged_in');
          localStorage.removeItem('user');
          window.location.hash = '#/login';
          throw new Error('Sesión expirada');
        }
      } catch (err) {
        localStorage.removeItem('logged_in');
        localStorage.removeItem('user');
        window.location.hash = '#/login';
        throw new Error('Sesión expirada');
      }
    }

    if (rawResponse) return response;

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const json = await response.json();
      if (!response.ok) {
        if (json.detail) throw new Error(json.detail);
        if (json.error) throw new Error(json.error);
        if (typeof json === 'object') {
          const msgs = Object.entries(json).map(([k, v]) => {
            const val = Array.isArray(v) ? v.join(', ') : v;
            return `${k}: ${val}`;
          });
          throw new Error(msgs.join(' | '));
        }
        throw new Error(JSON.stringify(json));
      }

      // Save to memory cache for GET requests
      if (method.toUpperCase() === 'GET') {
        this._cacheMap.set(endpoint, {
          timestamp: Date.now(),
          data: json
        });
      }

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

