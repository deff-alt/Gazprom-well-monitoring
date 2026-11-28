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
    let mounted = true
    const load = async () => {
      try {
        const [k, w] = await Promise.all([
          api.dashboardKpi(),
          api.dashboardWellsMap(),
        ])
        if (!mounted) return
        setKpi(k)
        setWells(Array.isArray(w) ? w : [])
      } catch (e) {
        if (mounted) setError(e.message || 'Не удалось загрузить данные дашборда')
      } finally {
        if (mounted) setLoading(false)
      }
    }
    load()
    return () => { mounted = false }
  }, [])

  return (
    <Layout>
      <div className="dashboard-heading">
        <div>
          <h1 className="wm-page-title">Дашборд</h1>
          <p className="wm-page-subtitle">Сводная информация по фонду скважин</p>
        </div>
        <div className="dashboard-updated"><span className="live-indicator" /> Данные системы</div>
      </div>

      {loading ? (
        <div className="wm-card dashboard-state">Загрузка данных дашборда…</div>
      ) : error ? (
        <div className="wm-error dashboard-state">{error}</div>
      ) : (
        <>
          <KpiCards kpi={kpi} />

          <div className="dashboard-map-grid">
            <div className="dashboard-map-wrap">
              <MapViewer
                wells={wells}
                selectedId={selectedWell?.id}
                onSelect={setSelectedWell}
              />
            </div>
            <div className="dashboard-side-wrap">
              <WellSidePanel well={selectedWell} onClose={() => setSelectedWell(null)} />
            </div>
          </div>

          <ChartsBlock wells={wells} totalWells={kpi?.total_wells ?? wells.length} />
        </>
      )}
    </Layout>
  )
}
