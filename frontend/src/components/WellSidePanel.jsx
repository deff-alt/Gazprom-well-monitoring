import { useNavigate } from 'react-router-dom'

const STATUS_LABELS = {
  active: 'В работе',
  in_repair: 'В ремонте',
  suspended: 'Приостановлена',
  plugged: 'Ликвидирована',
}

export default function WellSidePanel({ well, onClose }) {
  const navigate = useNavigate()

  if (!well) {
    return (
      <div className="wm-card" style={{ padding: 24, height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
        <div style={{ color: '#b8d9f1', fontSize: 13 }}>
          Выберите скважину на карте,<br/>чтобы увидеть подробности
        </div>
      </div>
    )
  }

  const rows = [
    ['Месторождение', well.locality_name || '—'],
    ['Промысел', well.promysel_name || '—'],
    ['Начальник промысла', well.head_name || '—'],
    ['Тип', well.type],
    ['Глубина', well.depth ? `${well.depth} м` : '—'],
    ['Пластовое давление', well.reservoir_pressure ? `${well.reservoir_pressure} МПа` : '—'],
    ['Температура', well.temperature ? `${well.temperature} °C` : '—'],
    ['Дата ввода', well.commissioning_date || '—'],
  ]

  return (
    <div className="wm-card" style={{ padding: 20, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
        <div>
          <div style={{ fontSize: 11, letterSpacing: 1, color: '#9dc7e6', fontWeight: 700 }}>СКВАЖИНА</div>
          <h2 style={{ margin: '4px 0 8px', fontSize: 24, color: '#fff', fontWeight: 800 }}>
            {well.well_number}
          </h2>
          <span className={`wm-badge wm-badge-${well.status}`}>
            {STATUS_LABELS[well.status] || well.status}
          </span>
        </div>
        {onClose && (
          <button onClick={onClose} className="wm-btn" style={{ padding: '4px 10px', fontSize: 12 }}>
            ✕
          </button>
        )}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 20 }}>
        {rows.map(([label, value]) => (
          <div key={label} style={{ display: 'flex', justifyContent: 'space-between', gap: 8, fontSize: 13 }}>
            <span style={{ color: '#9dc7e6' }}>{label}</span>
            <span style={{ color: '#fff', fontWeight: 600, textAlign: 'right' }}>{value}</span>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: 8 }}>
        <button
          className="wm-btn wm-btn-primary"
          onClick={() => navigate(`/wells/${well.id}`)}
          style={{ width: '100%', justifyContent: 'center' }}
        >
          Развернуть полностью →
        </button>
        <button
          className="wm-btn"
          onClick={() => navigate('/wells')}
          style={{ width: '100%', justifyContent: 'center' }}
        >
          Все скважины
        </button>
      </div>
    </div>
  )
}