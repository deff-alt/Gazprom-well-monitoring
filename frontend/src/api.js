const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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