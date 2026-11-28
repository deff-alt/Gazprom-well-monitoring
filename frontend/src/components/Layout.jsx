import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import '../styles.css'

const NAV = [
  {
    to: '/', label: 'Дашборд', end: true,
    icon: <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/><rect x="13" y="13" width="8" height="8" rx="1.5"/></svg>,
  },
  {
    to: '/wells', label: 'Скважины',
    icon: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 21h18M5 21l6-17 6 17M8 12h8M9 8h6M13 4l6 17M4 14h7"/></svg>,
  },
  {
    to: '/localities', label: 'Месторождения',
    icon: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m3 8 9-5 9 5-9 5-9-5Z M3 13l9 5 9-5M3 18l9 5 9-5"/></svg>,
  },
  {
    to: '/promysels', label: 'Промыслы',
    icon: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 21h18M5 21V11l5 3V9l5 3V5l4 2v14M8 17h1m4 0h1m4 0h1M14 5V2"/></svg>,
  },
  {
    to: '/users', label: 'Пользователи', adminOnly: true,
    icon: <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="8" r="3.5"/><path d="M2 21v-2a7 7 0 0 1 14 0v2M17 4a3.5 3.5 0 0 1 0 7m2 3a5 5 0 0 1 3 4.5V21"/></svg>,
  },
]

function LogoutIcon() {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 17l5-5-5-5M15 12H3m9-8h7a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-7"/></svg>
}

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  const visibleNav = NAV.filter(item => !item.adminOnly || user?.role === 'admin')

  return (
    <main className="placeholder-screen dashboard-shell">
      <div className="placeholder-glow glow-a" />
      <div className="placeholder-glow glow-b" />
      <div className="placeholder-industrial" aria-hidden="true" />

      <header className="placeholder-header">
        <a className="placeholder-brand" href="/" aria-label="Газпром добыча Краснодар">
          <img src="/images/gazprom-logo-white.png" alt="Газпром" />
          <span className="brand-product"><b>ДОБЫЧА</b><b>КРАСНОДАР</b></span>
        </a>
        <div className="placeholder-user">
          <span className="user-avatar">{(user?.username || 'П').slice(0, 1).toUpperCase()}</span>
          <span className="user-meta">
            <b>{user?.username || 'Пользователь'}</b>
            <small>{user?.role === 'admin' ? 'Администратор' : 'Пользователь системы'}</small>
          </span>
          <span className="user-divider" aria-hidden="true" />
          <button className="logout-button" onClick={handleLogout} aria-label="Выйти из системы">
            <LogoutIcon />
            <span>Выйти</span>
          </button>
        </div>
      </header>

      <nav className="wm-nav" aria-label="Главная навигация">
        {visibleNav.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => 'wm-nav-link' + (isActive ? ' active' : '')}
          >
            <span className="wm-nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="industrial-horizon" aria-hidden="true" />
      <section className="wm-content">
        {children}
      </section>

      <footer className="placeholder-footer">
        <span>© 2026 Газпром добыча Краснодар</span>
        <span>Энергия для будущего <i /> <b>v1.0</b></span>
      </footer>
    </main>
  )
}
