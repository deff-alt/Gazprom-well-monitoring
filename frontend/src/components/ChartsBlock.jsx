import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import { useMemo } from 'react'

const STATUS_LABELS = {
  active: 'В работе',
  in_repair: 'В ремонте',
  suspended: 'Приостановлена',
  plugged: 'Ликвидирована',
}

const STATUS_COLORS = {
  active: '#22c55e',
  in_repair: '#f59e0b',
  suspended: '#94a3b8',
  plugged: '#ef4444',
}

export default function ChartsBlock({ wells }) {
  // Данные для круговой диаграммы по статусам
  const statusData = useMemo(() => {
    const counts = { active: 0, in_repair: 0, suspended: 0, plugged: 0 }
    wells.forEach(w => { counts[w.status] = (counts[w.status] || 0) + 1 })
    return Object.entries(counts)
      .filter(([_, count]) => count > 0)
      .map(([status, count]) => ({
        name: STATUS_LABELS[status] || status,
        value: count,
        color: STATUS_COLORS[status] || '#888',
      }))
  }, [wells])

  // Данные для столбчатой диаграммы по промыслам
  const promyselData = useMemo(() => {
    const byPromysel = {}
    wells.forEach(w => {
      const key = w.promysel_name || 'Не указан'
      byPromysel[key] = (byPromysel[key] || 0) + 1
    })
    return Object.entries(byPromysel).map(([name, count]) => ({ name, count }))
  }, [wells])

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 14, marginBottom: 18 }}>
      <div className="wm-card" style={{ padding: 18 }}>
        <h3 style={{ margin: '0 0 12px', fontSize: 14, color: '#eaf8ff', fontWeight: 700 }}>
          Скважины по промыслам
        </h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={promyselData}>
            <XAxis dataKey="name" tick={{ fill: '#9dc7e6', fontSize: 11 }} />
            <YAxis allowDecimals={false} tick={{ fill: '#9dc7e6', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#003366', border: '1px solid rgba(189,234,255,.4)', borderRadius: 8, color: '#fff' }}
            />
            <Bar dataKey="count" fill="#3b82f6" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="wm-card" style={{ padding: 18 }}>
        <h3 style={{ margin: '0 0 12px', fontSize: 14, color: '#eaf8ff', fontWeight: 700 }}>
          Распределение по статусам
        </h3>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie data={statusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={{ fill: '#fff', fontSize: 11 }}>
              {statusData.map((entry, idx) => (
                <Cell key={idx} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{ background: '#003366', border: '1px solid rgba(189,234,255,.4)', borderRadius: 8, color: '#fff' }}
            />
            <Legend wrapperStyle={{ color: '#eaf8ff', fontSize: 11 }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}