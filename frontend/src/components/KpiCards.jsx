const ICONS = {
  total: <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M5 39h38M10 36l7-24 7 24M17 12h16l7 24M20 18l12 10M8 39v-6m32 6v-6M7 12l8 5m14-9 6 4"/></svg>,
  active: <svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="18"/><path d="m20 15 14 9-14 9V15Z"/></svg>,
  repair: <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M29 8a11 11 0 0 0-13 14L7 31a5 5 0 0 0 7 7l9-9A11 11 0 0 0 37 16l-7 7-7-7 6-8Z"/><path d="m29 29 10 10m-4-14 6 6"/></svg>,
  alerts: <svg viewBox="0 0 48 48" aria-hidden="true"><path d="M24 6 44 40H4L24 6Z"/><path d="M24 17v11m0 6v.5"/></svg>,
}

export default function KpiCards({ kpi }) {
  if (!kpi) return null

  const items = [
    { key: 'total', label: 'Всего скважин', value: kpi.total_wells ?? 0, color: 'blue' },
    { key: 'active', label: 'В работе', value: kpi.active ?? 0, color: 'green' },
    { key: 'repair', label: 'В ремонте', value: kpi.in_repair ?? 0, color: 'amber' },
    { key: 'alerts', label: 'Активные алерты', value: kpi.active_alerts ?? 0, color: 'red' },
  ]

  return (
    <div className="kpi-grid">
      {items.map(item => (
        <article key={item.key} className={`kpi-card kpi-${item.color}`}>
          <div className="kpi-icon">{ICONS[item.key]}</div>
          <span className="kpi-divider" aria-hidden="true" />
          <div className="kpi-copy">
            <div className="kpi-label">{item.label}</div>
            <div className="kpi-value">{item.value}</div>
          </div>
          <span className="kpi-glow" aria-hidden="true" />
        </article>
      ))}
    </div>
  )
}
