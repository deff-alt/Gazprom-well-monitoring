import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import { api } from '../api'
import { useAuth } from '../auth'

const SEVERITY = { critical: 'Критический', warning: 'Предупреждение', info: 'Информация' }
const STATUS = { new: 'Новый', in_progress: 'В работе', resolved: 'Закрыт', dismissed: 'Отклонён' }
const PARAM = { pressure_before_choke: 'Давление до штуцера', temperature_before_choke: 'Температура до штуцера', pressure_after_choke: 'Давление после штуцера', temperature_after_choke: 'Температура после штуцера', bottomhole_pressure: 'Забойное давление', flow_rate_gas: 'Дебит газа', flow_rate_liquid: 'Дебит жидкости', water_cut: 'Обводнённость', vibration: 'Вибрация' }

export default function Alerts() {
  const { user } = useAuth()
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [severity, setSeverity] = useState('')
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const canWork = user?.role !== 'operator'
  const load = async () => {
    setLoading(true); setError('')
    try { const data = await api.listAlerts({ severity, status }); setItems(data.items || []); setTotal(data.total || 0) }
    catch (e) { setError(e.message) } finally { setLoading(false) }
  }
  useEffect(() => { load() }, [severity, status])
  const update = async (item, nextStatus) => {
    try { await api.updateAlert(item.id, { status: nextStatus, resolution_comment: nextStatus === 'resolved' ? 'Обработано ответственным сотрудником' : '' }); await load() }
    catch (e) { setError(e.message) }
  }
  return <Layout>
    <div className="page-heading"><div><div className="eyebrow">ЦЕНТР СОБЫТИЙ</div><h1 className="wm-page-title">Алерты и инциденты</h1><p className="wm-page-subtitle">Контроль отклонений, назначение ответственных и обработка событий диагностики.</p></div><button className="wm-btn" onClick={load}>↻ Обновить</button></div>
    <div className="alert-summary-grid">
      <div className="metric-card"><span>Всего событий</span><b>{total}</b><small>По выбранным фильтрам</small></div>
      <div className="metric-card metric-warning"><span>Новые</span><b>{items.filter(x=>x.status==='new').length}</b><small>Ожидают реакции</small></div>
      <div className="metric-card metric-info"><span>В работе</span><b>{items.filter(x=>x.status==='in_progress').length}</b><small>Назначен ответственный</small></div>
      <div className="metric-card metric-good"><span>Закрытые</span><b>{items.filter(x=>x.status==='resolved').length}</b><small>Устранённые события</small></div>
    </div>
    <section className="wm-card alerts-card">
      <div className="section-toolbar"><div><h2>Журнал событий</h2><p>Последние зарегистрированные отклонения</p></div><div className="filter-row"><select value={severity} onChange={e=>setSeverity(e.target.value)}><option value="">Все уровни</option><option value="critical">Критические</option><option value="warning">Предупреждения</option><option value="info">Информация</option></select><select value={status} onChange={e=>setStatus(e.target.value)}><option value="">Все статусы</option><option value="new">Новые</option><option value="in_progress">В работе</option><option value="resolved">Закрытые</option><option value="dismissed">Отклонённые</option></select></div></div>
      {error && <div className="wm-error">{error}</div>}
      {loading ? <div className="wm-empty">Загрузка событий…</div> : items.length === 0 ? <div className="empty-state"><span>✓</span><b>Событий пока нет</b><small>Когда диагностический модуль обнаружит отклонение, оно появится в этом журнале.</small></div> : <div className="table-scroll"><table className="wm-table alerts-table"><thead><tr><th>Событие</th><th>Скважина</th><th>Параметр</th><th>Оценка</th><th>Время</th><th>Статус</th><th>Действия</th></tr></thead><tbody>{items.map(a=><tr key={a.id}><td><span className={`severity-dot ${a.severity}`}></span><b>{SEVERITY[a.severity] || a.severity}</b><small className="cell-sub">№ {a.id}</small></td><td><b>{a.well_number}</b><small className="cell-sub">{a.locality_name || 'Месторождение не указано'}</small></td><td>{PARAM[a.parameter] || a.parameter}</td><td><span className="score-pill">{a.anomaly_score == null ? '—' : `${Math.round(a.anomaly_score*100)}%`}</span></td><td>{a.created_at ? new Date(a.created_at).toLocaleString('ru-RU') : '—'}</td><td><span className={`status-pill ${a.status}`}>{STATUS[a.status] || a.status}</span></td><td><div className="table-actions">{canWork && a.status==='new' && <button className="wm-btn wm-btn-small" onClick={()=>update(a,'in_progress')}>В работу</button>}{canWork && a.status==='in_progress' && <button className="wm-btn wm-btn-primary wm-btn-small" onClick={()=>update(a,'resolved')}>Закрыть</button>}</div></td></tr>)}</tbody></table></div>}
    </section>
  </Layout>
}
