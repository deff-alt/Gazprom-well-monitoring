import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import '../styles.css'

const NAV = [
  { to: '/', label: 'Дашборд', end: true },
  { to: '/wells', label: 'Скважины' },
  { to: '/localities', label: 'Месторождения' },
  { to: '/promysels', label: 'Промыслы' },
  { to: '/users', label: 'Пользователи', adminOnly: true },
]

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  // Фильтруем пункты меню: пункты с adminOnly видны только админу
  const visibleNav = NAV.filter(item => !item.adminOnly || user?.role === 'admin')

  return (
    <main className="placeholder-screen">
      <div className="placeholder-glow glow-a" />
      <div className="placeholder-glow glow-b" />

      <header className="placeholder-header">
        <a className="placeholder-brand" href="/" aria-label="Well Monitor">
          <img src="/images/gazprom-logo-white.png" alt="Газпром" />
          <span>WELL MONITOR</span>
        </a>
        <div className="placeholder-user">
          <span className="user-avatar">{(user?.username || 'П').slice(0, 1).toUpperCase()}</span>
          <span>
            <b>{user?.username || 'Пользователь'}</b>
            <small>{user?.role || 'Пользователь системы'}</small>
          </span>
          <button onClick={handleLogout}>Выйти <span>↗</span></button>
        </div>
      </header>

      <nav className="wm-nav">
        {visibleNav.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => 'wm-nav-link' + (isActive ? ' active' : '')}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <section className="wm-content">
        {children}
      </section>

      <footer className="placeholder-footer">
        <span>© 2026 Well Monitor</span>
        <span>ЭНЕРГИЯ ДЛЯ БУДУЩЕГО <i /> <b>v1.0</b></span>
      </footer>
    </main>
  )
}