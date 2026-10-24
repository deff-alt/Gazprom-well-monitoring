import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import '../styles.css'

function UserIcon() {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="3.5"/><path d="M4.5 20c.5-4 3-6 7.5-6s7 2 7.5 6z"/></svg>
}
function LockIcon() {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/><path d="M12 14v3"/></svg>
}
function EyeIcon({ visible }) {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.5 12s3.3-6 9.5-6 9.5 6 9.5 6-3.3 6-9.5 6-9.5-6-9.5-6z"/><circle cx="12" cy="12" r="2.7"/>{visible && <path d="M4 4l16 16"/>}</svg>
}

export default function Login() {
  const { login, user } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => { if (user) navigate('/', { replace: true }) }, [user, navigate])

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      await login(username, password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.message || 'Не удалось войти в систему')
    } finally {
      setBusy(false)
    }
  }

  return <main className="auth-screen">
    <div className="auth-background" aria-hidden="true" />
    <header className="auth-header">
      <a className="gazprom-brand" href="/login" aria-label="Газпром — Well Monitor">
        <img src="/images/gazprom-logo-white.png" alt="Газпром" />
      </a>
      <div className="brand-slogan"><span /> <p>ЭНЕРГИЯ<br/>ДЛЯ БУДУЩЕГО</p></div>
    </header>

    <section className="auth-center" aria-labelledby="login-title">
      <div className="auth-card">
        <h1 id="login-title">Well Monitor</h1>
        <p className="auth-subtitle">Вход в систему</p>
        <form onSubmit={submit}>
          <label className="sr-only" htmlFor="username">Логин</label>
          <div className="auth-input-wrap"><UserIcon/><input id="username" name="username" autoFocus autoComplete="username" placeholder="Логин" value={username} onChange={e => setUsername(e.target.value)} required /></div>
          <label className="sr-only" htmlFor="password">Пароль</label>
          <div className="auth-input-wrap"><LockIcon/><input id="password" name="password" type={showPassword ? 'text' : 'password'} autoComplete="current-password" placeholder="Пароль" value={password} onChange={e => setPassword(e.target.value)} required /><button className="password-toggle" type="button" onClick={() => setShowPassword(v => !v)} aria-label={showPassword ? 'Скрыть пароль' : 'Показать пароль'}><EyeIcon visible={showPassword}/></button></div>
          {error && <div className="auth-error" role="alert">{error}</div>}
          <button className="auth-submit" type="submit" disabled={busy}>{busy ? 'Выполняется вход…' : 'Войти'} <span aria-hidden="true">→</span></button>
        </form>
        <div className="demo-access"><span/>Демо: <b>admin / admin123</b><span/></div>
      </div>
    </section>
    <footer className="auth-footer"><span>WELL MONITOR</span><i/> СИСТЕМА ПРОМЫШЛЕННОГО МОНИТОРИНГА <small>© 2026</small></footer>
  </main>
}
