import { useAuth } from '../auth'
import '../styles.css'

export default function Dashboard() {
  const { user, logout } = useAuth()
  return <main className="placeholder-screen">
    <div className="placeholder-glow glow-a"/><div className="placeholder-glow glow-b"/>
    <header className="placeholder-header">
      <a className="placeholder-brand" href="/" aria-label="Well Monitor"><img src="/images/gazprom-logo-white.png" alt="Газпром"/><span>WELL MONITOR</span></a>
      <div className="placeholder-user"><span className="user-avatar">{(user?.username || 'П').slice(0,1).toUpperCase()}</span><span><b>{user?.username || 'Пользователь'}</b><small>{user?.role || 'Пользователь системы'}</small></span><button onClick={logout}>Выйти <span>↗</span></button></div>
    </header>
    <section className="placeholder-content">
      <div className="placeholder-badge"><i/> РАБОЧЕЕ ПРОСТРАНСТВО</div>
      <div className="placeholder-symbol" aria-hidden="true"><svg viewBox="0 0 120 120"><path d="M60 10 103 35v50L60 110 17 85V35z"/><path d="M60 31v36m0 0-16-16m16 16 16-16M38 81h44"/></svg></div>
      <p className="placeholder-eyebrow">WELL MONITOR · INDUSTRIAL INTELLIGENCE</p>
      <h1>Ваша энергия.<br/><em>Под контролем.</em></h1>
      <p className="placeholder-description">Мы готовим рабочее пространство для мониторинга скважин и промышленного оборудования. Здесь появятся ключевые показатели, аналитика и события в реальном времени.</p>
      <div className="coming-soon"><span className="coming-icon">✦</span><span><b>Система готовится к запуску</b><small>Интерфейс мониторинга скоро будет доступен</small></span><span className="coming-pulse"/></div>
      <button className="placeholder-logout" onClick={logout}>Вернуться ко входу <span>→</span></button>
    </section>
    <div className="placeholder-industrial" aria-hidden="true"/>
    <footer className="placeholder-footer"><span>© 2026 Well Monitor</span><span>ЭНЕРГИЯ ДЛЯ БУДУЩЕГО <i/> <b>v1.0</b></span></footer>
  </main>
}
