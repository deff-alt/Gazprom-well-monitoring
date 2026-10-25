import Layout from '../components/Layout'
import { useAuth } from '../auth'

export default function Dashboard() {
  const { user } = useAuth()

  return (
    <Layout>
      <div className="placeholder-badge"><i /> РАБОЧЕЕ ПРОСТРАНСТВО</div>
      <div className="placeholder-symbol" aria-hidden="true">
        <svg viewBox="0 0 120 120">
          <path d="M60 10 103 35v50L60 110 17 85V35z" />
          <path d="M60 31v36m0 0-16-16m16 16 16-16M38 81h44" />
        </svg>
      </div>
      <p className="placeholder-eyebrow">WELL MONITOR · INDUSTRIAL INTELLIGENCE</p>
      <h1>Ваша энергия.<br /><em>Под контролем.</em></h1>
      <p className="placeholder-description">
        Рабочее пространство для мониторинга скважин и промышленного оборудования.
        Используйте меню сверху, чтобы перейти к управлению скважинами, месторождениями и промыслами.
      </p>

      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 22 }}>
        <a href="/wells" className="wm-btn wm-btn-primary">Перейти к скважинам →</a>
        <a href="/localities" className="wm-btn">Месторождения</a>
        <a href="/promysels" className="wm-btn">Промыслы</a>
      </div>

      <div className="coming-soon" style={{ marginTop: 28 }}>
        <span className="coming-icon">✦</span>
        <span>
          <b>Здравствуйте, {user?.full_name || user?.username}</b>
          <small>Роль: {user?.role || 'Пользователь'}</small>
        </span>
        <span className="coming-pulse" />
      </div>
    </Layout>
  )
}