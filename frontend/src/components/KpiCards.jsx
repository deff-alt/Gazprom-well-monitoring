export default function KpiCards({ kpi }) {
  if (!kpi) return null

  const items = [
    {
      label: 'Всего скважин',
      value: kpi.total_wells,
      hint: `Активных: ${kpi.active}`,
      color: '#3b82f6',
    },
    {
      label: 'В ремонте',
      value: kpi.in_repair,
      hint: `Приостановлено: ${kpi.suspended}`,
      color: '#f59e0b',
    },
    {
      label: 'Активные алерты',
      value: kpi.active_alerts,
      hint: kpi.active_alerts === 0 ? 'Всё в норме' : 'Требуют внимания',
      color: kpi.active_alerts > 0 ? '#ef4444' : '#22c55e',
    },
    {
      label: 'Средний дебит (24ч)',
      value: kpi.avg_gas_last_24h ? `${kpi.avg_gas_last_24h.toFixed(1)} м³/ч` : '—',
      hint: 'По всем скважинам',
      color: '#8b5cf6',
    },
  ]

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 14, marginBottom: 18 }}>
      {items.map(it => (
        <div
          key={it.label}
          className="wm-card"
          style={{ padding: 18, borderLeft: `4px solid ${it.color}` }}
        >
          <div style={{ fontSize: 11, letterSpacing: 1, textTransform: 'uppercase', color: '#9dc7e6', fontWeight: 700 }}>
            {it.label}
          </div>
          <div style={{ fontSize: 28, fontWeight: 800, color: '#fff', marginTop: 6, letterSpacing: '-0.5px' }}>
            {it.value}
          </div>
          <div style={{ fontSize: 11, color: '#b8d9f1', marginTop: 4 }}>
            {it.hint}
          </div>
        </div>
      ))}
    </div>
  )
}