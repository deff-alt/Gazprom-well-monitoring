import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, CartesianGrid } from 'recharts'
import { useMemo } from 'react'

const STATUS_LABELS = {
  active: 'В работе',
  in_repair: 'В ремонте',
  suspended: 'Приостановлена',
  plugged: 'Ликвидирована',
}

const STATUS_COLORS = {
  active: '#20c985',
  in_repair: '#e6ad3b',
  suspended: '#7da9cb',
  plugged: '#d87582',
}

export default function ChartsBlock({ wells, totalWells = 0 }) {
  const statusData = useMemo(() => {
    const counts = { active: 0, in_repair: 0, suspended: 0, plugged: 0 }
    wells.forEach(w => { counts[w.status] = (counts[w.status] || 0) + 1 })
    return Object.entries(counts)
      .filter(([, count]) => count > 0)
      .map(([status, count]) => ({ name: STATUS_LABELS[status] || status, value: count, color: STATUS_COLORS[status] || '#8ba8c5' }))
  }, [wells])

  const promyselData = useMemo(() => {
    const byPromysel = {}
    wells.forEach(w => {
      const key = w.promysel_name || 'Не указан'
      byPromysel[key] = (byPromysel[key] || 0) + 1
    })
    return Object.entries(byPromysel).map(([name, count]) => ({ name, count }))
  }, [wells])

  return (
    <div className="charts-grid">
      <section className="wm-card chart-card">
        <h3 className="panel-title">
          <span className="panel-title-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M4 20h16M6 17v-5h4v5m4 0V7h4v10M8 12V5h8"/><circle cx="8" cy="5" r="2"/><circle cx="16" cy="7" r="2"/></svg></span>
          Скважины по промыслам
        </h3>
        {promyselData.length ? (
          <ResponsiveContainer width="100%" height={204}>
            <BarChart data={promyselData} margin={{ top: 10, right: 12, left: -10, bottom: 0 }}>
              <CartesianGrid stroke="rgba(157,211,246,.13)" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: '#e2f3ff', fontSize: 11 }} axisLine={{ stroke: 'rgba(174,220,255,.45)' }} tickLine={false} />
              <YAxis allowDecimals={false} tick={{ fill: '#c2def2', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: 'rgba(77,183,255,.08)' }} contentStyle={{ background: 'rgba(2,43,83,.96)', border: '1px solid rgba(189,234,255,.4)', borderRadius: 9, color: '#fff' }} />
              <Bar dataKey="count" name="Скважины" fill="#3b9fd5" radius={[5, 5, 0, 0]} maxBarSize={68} />
            </BarChart>
          </ResponsiveContainer>
        ) : <div className="chart-empty">Нет данных по промыслам</div>}
      </section>

      <section className="wm-card chart-card">
        <h3 className="panel-title">
          <span className="panel-title-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 3v9h9A9 9 0 1 1 12 3Zm3-1a10 10 0 0 1 8 8h-8V2Z"/></svg></span>
          Распределение по статусам
        </h3>
        {statusData.length ? (
          <div className="status-chart-wrap">
            <ResponsiveContainer width="100%" height={204}>
              <PieChart>
                <Pie data={statusData} dataKey="value" nameKey="name" cx="36%" cy="50%" innerRadius={48} outerRadius={76} paddingAngle={2} stroke="rgba(3,39,76,.65)" strokeWidth={2}>
                  {statusData.map((entry, idx) => <Cell key={idx} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ background: 'rgba(2,43,83,.96)', border: '1px solid rgba(189,234,255,.4)', borderRadius: 9, color: '#fff' }} />
                <Legend layout="vertical" align="right" verticalAlign="middle" iconType="circle" iconSize={9} wrapperStyle={{ color: '#eaf8ff', fontSize: 12, lineHeight: '30px', paddingRight: 8 }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="status-chart-center"><b>{totalWells}</b><span>скважин</span></div>
          </div>
        ) : <div className="chart-empty">Нет данных о статусах</div>}
      </section>
    </div>
  )
}
