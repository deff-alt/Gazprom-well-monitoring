import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '../components/Layout'
import { api } from '../api'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

const STATUS_LABELS = {
  active: 'В работе',
  in_repair: 'В ремонте',
  suspended: 'Приостановлена',
  plugged: 'Ликвидирована',
}

const TYPE_LABELS = {
  PRODUCTION: 'Добывающая',
  INJECTION: 'Нагнетательная',
  EXPLORATION: 'Разведочная',
}

export default function WellDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [well, setWell] = useState(null)
  const [telemetry, setTelemetry] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        const [w, t] = await Promise.all([
          api.getWell(id),
          api.listTelemetry(id, '7d', 0, 500),
        ])
        setWell(w)
        setTelemetry((t.items || []).reverse())
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  if (loading) return <Layout><div className="wm-empty">Загрузка…</div></Layout>
  if (error) return <Layout><div className="wm-error">{error}</div></Layout>
  if (!well) return <Layout><div className="wm-empty">Скважина не найдена</div></Layout>

  const chartData = telemetry.map(p => ({
    ts: new Date(p.ts).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }),
    pressure: p.pressure_before_choke ? Number(p.pressure_before_choke) : null,
    water: p.water_cut ? Number(p.water_cut) : null,
    vib: p.vibration ? Number(p.vibration) : null,
  }))

  return (
    <Layout>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12, marginBottom: 20 }}>
        <div>
          <button className="wm-btn" onClick={() => navigate(-1)} style={{ marginBottom: 10, padding: '6px 12px', fontSize: 12 }}>
            ← Назад
          </button>
          <h1 className="wm-page-title" style={{ marginBottom: 4 }}>Скважина {well.well_number}</h1>
          <p className="wm-page-subtitle" style={{ marginBottom: 0 }}>
            {well.locality_name} · {well.promysel_name || '—'} · <span className={`wm-badge wm-badge-${well.status}`}>{STATUS_LABELS[well.status] || well.status}</span>
          </p>
        </div>
        <button className="wm-btn wm-btn-primary" onClick={() => navigate('/wells')}>
          Все скважины
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 14, marginBottom: 18 }}>
        <InfoCard label="Тип" value={TYPE_LABELS[well.type] || well.type} />
        <InfoCard label="Глубина" value={well.depth ? `${well.depth} м` : '—'} />
        <InfoCard label="Пластовое давление" value={well.reservoir_pressure ? `${well.reservoir_pressure} МПа` : '—'} />
        <InfoCard label="Температура" value={well.temperature ? `${well.temperature} °C` : '—'} />
        <InfoCard label="Инвентарный номер" value={well.inventory_number || '—'} />
        <InfoCard label="Сдача в эксплуатацию" value={well.commissioning_date || '—'} />
        <InfoCard label="Буферное давление" value={well.buffer_pressure ? `${well.buffer_pressure} МПа` : '—'} />
        <InfoCard label="Расчётный срок" value={well.planned_lifetime ? `${well.planned_lifetime} лет` : '—'} />
      </div>

      <div className="wm-card" style={{ padding: 20, marginBottom: 16 }}>
        <h3 style={{ margin: '0 0 16px', fontSize: 15, color: '#eaf8ff', fontWeight: 700 }}>
          Телеметрия за 7 дней ({telemetry.length} точек)
        </h3>
        {chartData.length === 0 ? (
          <div className="wm-empty">Нет данных телеметрии</div>
        ) : (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(189,234,255,.15)" />
              <XAxis dataKey="ts" tick={{ fill: '#9dc7e6', fontSize: 10 }} interval="preserveStartEnd" />
              <YAxis yAxisId="left" tick={{ fill: '#9dc7e6', fontSize: 11 }} />
              <YAxis yAxisId="right" orientation="right" tick={{ fill: '#9dc7e6', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#002b4f', border: '1px solid rgba(189,234,255,.4)', borderRadius: 8, color: '#fff' }}
              />
              <Line yAxisId="left" type="monotone" dataKey="pressure" stroke="#3b82f6" strokeWidth={2} dot={false} name="Давление до штуцера, МПа" />
              <Line yAxisId="right" type="monotone" dataKey="water" stroke="#f59e0b" strokeWidth={2} dot={false} name="Обводнённость, %" />
              <Line yAxisId="right" type="monotone" dataKey="vib" stroke="#a855f7" strokeWidth={2} dot={false} name="Вибрация, мм/с" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="wm-card" style={{ padding: 20 }}>
        <h3 style={{ margin: '0 0 12px', fontSize: 15, color: '#eaf8ff', fontWeight: 700 }}>Алерты по скважине</h3>
        <div className="wm-empty" style={{ padding: '24px 0' }}>
          Алерты появятся после запуска ML-модуля
        </div>
      </div>
    </Layout>
  )
}

function InfoCard({ label, value }) {
  return (
    <div className="wm-card" style={{ padding: 16 }}>
      <div style={{ fontSize: 10, letterSpacing: 1, textTransform: 'uppercase', color: '#9dc7e6', fontWeight: 700, marginBottom: 6 }}>
        {label}
      </div>
      <div style={{ fontSize: 16, color: '#fff', fontWeight: 700 }}>{value}</div>
    </div>
  )
}