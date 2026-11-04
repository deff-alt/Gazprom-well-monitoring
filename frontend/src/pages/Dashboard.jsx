import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import KpiCards from '../components/KpiCards'
import MapViewer from '../components/MapViewer'
import WellSidePanel from '../components/WellSidePanel'
import ChartsBlock from '../components/ChartsBlock'
import { api } from '../api'

export default function Dashboard() {
  const [kpi, setKpi] = useState(null)
  const [wells, setWells] = useState([])
  const [selectedWell, setSelectedWell] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        const [k, w] = await Promise.all([
          api.dashboardKpi(),
          api.dashboardWellsMap(),
        ])
        setKpi(k)
        setWells(w)
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return <Layout><div className="wm-empty">Загрузка дашборда…</div></Layout>
  }

  if (error) {
    return <Layout><div className="wm-error">{error}</div></Layout>
  }

  return (
    <Layout>
      <div style={{ marginBottom: 20 }}>
        <h1 className="wm-page-title">Дашборд</h1>
        <p className="wm-page-subtitle">
          Сводная информация по фонду скважин. Кликните на скважину на карте, чтобы увидеть подробности.
        </p>
      </div>

      <KpiCards kpi={kpi} />

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 2fr) minmax(280px, 1fr)', gap: 14, marginBottom: 18 }}>
        <div style={{ minHeight: 420 }}>
          <MapViewer
            wells={wells}
            selectedId={selectedWell?.id}
            onSelect={setSelectedWell}
          />
        </div>
        <div style={{ minHeight: 420 }}>
          <WellSidePanel well={selectedWell} onClose={() => setSelectedWell(null)} />
        </div>
      </div>

      <ChartsBlock wells={wells} />

      <div className="wm-card" style={{ padding: 18 }}>
        <h3 style={{ margin: '0 0 12px', fontSize: 14, color: '#eaf8ff', fontWeight: 700 }}>
          Последние алерты
        </h3>
        <div className="wm-empty" style={{ padding: '30px 20px' }}>
          Алерты появятся после запуска ML-модуля.
          <br/>
          <span style={{ fontSize: 11, opacity: 0.7 }}>
            Сейчас можно посмотреть страницу «Скважины» для просмотра фонда.
          </span>
        </div>
      </div>
    </Layout>
  )
}