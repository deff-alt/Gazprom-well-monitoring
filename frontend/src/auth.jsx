import { createContext, useContext, useEffect, useState } from 'react'
import { me, login as apiLogin, refresh as apiRefresh } from './api'

const AuthCtx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const at = localStorage.getItem('access_token')
    if (!at) { setLoading(false); return }
    me(at)
      .then(setUser)
      .catch(async () => {
        const rt = localStorage.getItem('refresh_token')
        if (!rt) { setLoading(false); return }
        try {
          const t = await apiRefresh(rt)
          localStorage.setItem('access_token', t.access_token)
          localStorage.setItem('refresh_token', t.refresh_token)
          setUser(await me(t.access_token))
        } catch {
          localStorage.clear()
        } finally {
          setLoading(false)
        }
      })
      .finally(() => setLoading(false))
  }, [])

  const login = async (username, password) => {
    const t = await apiLogin(username, password)
    localStorage.setItem('access_token', t.access_token)
    localStorage.setItem('refresh_token', t.refresh_token)
    const u = await me(t.access_token)
    setUser(u)
    return u
  }

  const logout = () => {
    localStorage.clear()
    setUser(null)
  }

  return <AuthCtx.Provider value={{ user, loading, login, logout }}>{children}</AuthCtx.Provider>
}

export const useAuth = () => useContext(AuthCtx)