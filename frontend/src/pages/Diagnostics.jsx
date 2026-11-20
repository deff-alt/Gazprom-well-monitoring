import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import { api } from '../api'
import { useAuth } from '../auth'

export default function Diagnostics() {
  const { user } = useAuth()
  const [model, setModel] = useState(null)
  const [wells, setWells] = useState([])
  const [wellId, setWellId] = useState('')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const canTrain = user?.role === 'admin'
  const canPredict = ['admin','engineer','kipia_engineer','mechanical_engineer','geologist'].includes(user?.role)
  const load = async () => { try { const [m,w] = await Promise.all([api.mlStatus(),api.listWell()]); setModel(m); setWells(w); if (!wellId && w[0]) setWellId(String(w[0].id)) } catch(e) { setError(e.message) } }
  useEffect(()=>{load()},[])
  const train = async () => { setBusy(true); setError(''); setMessage(''); try { const r=await api.trainModel(); setMessage(`Модель обучена на ${r.samples} точках телеметрии.`); await load() } catch(e){setError(e.message)} finally{setBusy(false)} }
  const predict = async () => { if(!wellId)return; setBusy(true); setError(''); setMessage(''); try { const r=await api.predictWell(wellId); setMessage(r.is_anomaly ? `Обнаружено отклонение: ${Math.round(r.anomaly_score*100)}%. ${r.alert_created?'Алерт добавлен в журнал.':''}` : `Отклонений не обнаружено. Оценка аномальности: ${Math.round(r.anomaly_score*100)}%.`); } catch(e){setError(e.message)} finally{setBusy(false)} }
  return <Layout><div className="page-heading"><div><div className="eyebrow">MACHINE LEARNING</div><h1 className="wm-page-title">Предиктивная диагностика</h1><p className="wm-page-subtitle">Обучение модели и запуск анализа телеметрии скважин.</p></div></div>
    <div className="diagnostic-grid"><section className="wm-card model-card"><div className="model-icon">⌁</div><div className="eyebrow">АНАЛИТИЧЕСКОЕ ЯДРО</div><h2>Isolation Forest</h2><p>Алгоритм выявляет нетипичные сочетания технологических параметров без необходимости заранее размечать каждый тип неисправности.</p><div className="model-status"><i className={model?.trained?'online':''}></i><span>{model?.trained?'Модель обучена':'Модель не обучена'}</span></div><div className="model-meta"><div><small>Обучающих точек</small><b>{model?.training_samples || '—'}</b></div><div><small>Последнее обучение</small><b>{model?.trained_at ? new Date(model.trained_at).toLocaleString('ru-RU') : '—'}</b></div></div>{canTrain ? <button className="wm-btn wm-btn-primary" onClick={train} disabled={busy}>{busy?'Выполняется…':'Обучить / переобучить модель'}</button> : <small className="permission-note">Переобучение доступно администратору.</small>}</section>
    <section className="wm-card predict-card"><div className="eyebrow">РУЧНОЙ ИНФЕРЕНС</div><h2>Проверить скважину</h2><p>Модель анализирует последнюю доступную точку телеметрии и при обнаружении аномалии создаёт событие в журнале.</p><label>Выберите скважину</label><select value={wellId} onChange={e=>setWellId(e.target.value)}>{wells.map(w=><option key={w.id} value={w.id}>{w.well_number} · {w.locality_name}</option>)}</select><button className="wm-btn wm-btn-primary" disabled={busy || !model?.trained || !wellId || !canPredict} onClick={predict}>{busy?'Анализ…':'Запустить диагностику →'}</button>{!model?.trained&&<small className="permission-note">Сначала необходимо обучить модель на телеметрии.</small>}{!canPredict&&<small className="permission-note">Запуск диагностики недоступен для вашей роли.</small>}</section></div>
    {message&&<div className="result-banner">✓ {message}</div>}{error&&<div className="wm-error">{error}</div>}
    <div className="wm-card method-note"><h3>Как интерпретировать результат</h3><p>Оценка аномальности — это внутренний индикатор отклонения модели, а не вероятность аварии и не прогноз времени до отказа. Для промышленного применения потребуется историческая разметка инцидентов, валидация на независимой выборке и настройка порогов совместно с технологами.</p></div>
  </Layout>
}
