const API = {
  async request(method, path, body = null) {
    const token = localStorage.getItem('token');
    const opts = {
      method,
      headers: { ...(token ? { 'Authorization': `Bearer ${token}` } : {}) },
    };
    if (body !== null) {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(body);
    }
    const res = await fetch(`/api${path}`, opts);
    if (res.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/index.html';
      return;
    }
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
    return data;
  },
  get: (path) => API.request('GET', path),
  post: (path, body) => API.request('POST', path, body),
  put: (path, body) => API.request('PUT', path, body),
  delete: (path) => API.request('DELETE', path),

  async uploadFile(path, file) {
    const token = localStorage.getItem('token');
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`/api${path}`, {
      method: 'POST',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      body: formData,
    });
    if (res.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/index.html';
      return;
    }
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || `Upload failed (${res.status})`);
    return data;
  },
};

function requireAuth() {
  if (!localStorage.getItem('token')) {
    window.location.href = '/index.html';
  }
}

function showToast(msg, isError = false) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.className = `toast ${isError ? 'toast-error' : 'toast-success'} show`;
  setTimeout(() => t.classList.remove('show'), 3000);
}
