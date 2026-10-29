const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function authHeaders() {
  const token = localStorage.getItem('access_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
      ...(options.headers || {}),
    },
  })
  if (res.status === 401) {
    localStorage.clear()
    window.location.href = '/login'
    throw new Error('Сессия истекла')
  }
  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {}
    throw new Error(detail)
  }
  if (res.status === 204) return null
  return res.json()
}

// ===== AUTH (совместимость с auth.jsx) =====
export async function login(username, password) {
  const r = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!r.ok) throw new Error('Неверный логин или пароль')
  return r.json()
}
export async function me(accessToken) {
  const r = await fetch(`${BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  })
  if (!r.ok) throw new Error('unauthorized')
  return r.json()
}
export async function refresh(refreshToken) {
  const r = await fetch(`${BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  })
  if (!r.ok) throw new Error('refresh failed')
  return r.json()
}

// ===== CRUD helpers =====
export const api = {
  listWell:    () => request('/wells'),
  getWell:     (id) => request(`/wells/${id}`),
  createWell:  (data) => request('/wells', { method: 'POST', body: JSON.stringify(data) }),
  updateWell:  (id, data) => request(`/wells/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteWell:  (id) => request(`/wells/${id}`, { method: 'DELETE' }),

  listLocalities:   () => request('/localities'),
  createLocality:   (data) => request('/localities', { method: 'POST', body: JSON.stringify(data) }),
  updateLocality:   (id, data) => request(`/localities/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteLocality:   (id) => request(`/localities/${id}`, { method: 'DELETE' }),

  listPromysels:    () => request('/promysels'),
  createPromysel:   (data) => request('/promysels', { method: 'POST', body: JSON.stringify(data) }),
  updatePromysel:   (id, data) => request(`/promysels/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deletePromysel:   (id) => request(`/promysels/${id}`, { method: 'DELETE' }),
  listUsers:    () => request('/users'),
  createUser:   (data) => request('/users', { method: 'POST', body: JSON.stringify(data) }),
  updateUser:   (id, data) => request(`/users/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteUser:   (id) => request(`/users/${id}`, { method: 'DELETE' }),
}