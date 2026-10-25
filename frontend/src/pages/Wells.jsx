import { useEffect, useMemo, useState } from 'react'
import Layout from '../components/Layout'
import { useAuth } from '../auth'
import { api } from '../api'

const STATUS_LABELS = {
  active: 'В работе',
  in_repair: 'В ремонте',
  suspended: 'Приостановлена',
  plugged: 'Ликвидирована',
}

const TYPE_LABELS = {
  'Добывающая': 'Добывающая',
  'Нагнетательная': 'Нагнетательная',
  'Разведочная': 'Разведочная',
}

const EMPTY_FORM = {
  well_number: '',
  locality_id: '',
  promysel_id: '',
  type: 'Добывающая',
  status: 'active',
  location: '',
  depth: '',
  hanger_diameter: '',
  drilling_start_date: '',
  drilling_end_date: '',
  commissioning_date: '',
  inventory_number: '',
  reservoir_pressure: '',
  buffer_pressure: '',
  casing_pressure: '',
  temperature: '',
  choke_diameter: '',
  planned_lifetime: '',
}

export default function Wells() {
  const { user } = useAuth()
  const canEdit = user?.role === 'admin' || user?.role === 'engineer'
  const canDelete = user?.role === 'admin'

  const [wells, setWells] = useState([])
  const [localities, setLocalities] = useState([])
  const [promysels, setPromysels] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')

  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [modalError, setModalError] = useState('')

  const reload = async () => {
    setLoading(true)
    setError('')
    try {
      const [w, l, p] = await Promise.all([
        api.listWell(),
        api.listLocalities(),
        api.listPromysels(),
      ])
      setWells(w)
      setLocalities(l)
      setPromysels(p)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { reload() }, [])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return wells
    return wells.filter(w =>
      w.well_number.toLowerCase().includes(q) ||
      (w.locality_name || '').toLowerCase().includes(q) ||
      (w.promysel_name || '').toLowerCase().includes(q)
    )
  }, [wells, search])

  const openCreate = () => {
    setEditingId(null)
    setForm({ ...EMPTY_FORM, locality_id: localities[0]?.id || '', promysel_id: promysels[0]?.id || '' })
    setModalError('')
    setModalOpen(true)
  }

  const openEdit = (well) => {
    setEditingId(well.id)
    setForm({
      well_number: well.well_number,
      locality_id: well.locality_id || '',
      promysel_id: well.promysel_id || '',
      type: well.type,
      status: well.status,
      location: well.location || '',
      depth: well.depth ?? '',
      hanger_diameter: well.hanger_diameter ?? '',
      drilling_start_date: well.drilling_start_date || '',
      drilling_end_date: well.drilling_end_date || '',
      commissioning_date: well.commissioning_date || '',
      inventory_number: well.inventory_number || '',
      reservoir_pressure: well.reservoir_pressure ?? '',
      buffer_pressure: well.buffer_pressure ?? '',
      casing_pressure: well.casing_pressure ?? '',
      temperature: well.temperature ?? '',
      choke_diameter: well.choke_diameter ?? '',
      planned_lifetime: well.planned_lifetime ?? '',
    })
    setModalError('')
    setModalOpen(true)
  }

  const closeModal = () => {
    setModalOpen(false)
    setEditingId(null)
    setForm(EMPTY_FORM)
    setModalError('')
  }

  const handleField = (e) => {
    const { name, value } = e.target
    setForm(f => ({ ...f, [name]: value }))
  }

  const buildPayload = () => {
    const num = (v) => v === '' || v === null || v === undefined ? null : Number(v)
    const str = (v) => v === '' || v === null || v === undefined ? null : v
    return {
      well_number: form.well_number,
      locality_id: Number(form.locality_id),
      promysel_id: form.promysel_id ? Number(form.promysel_id) : null,
      type: form.type,
      status: form.status,
      location: str(form.location),
      depth: num(form.depth),
      hanger_diameter: num(form.hanger_diameter),
      drilling_start_date: str(form.drilling_start_date),
      drilling_end_date: str(form.drilling_end_date),
      commissioning_date: str(form.commissioning_date),
      inventory_number: str(form.inventory_number),
      reservoir_pressure: num(form.reservoir_pressure),
      buffer_pressure: num(form.buffer_pressure),
      casing_pressure: num(form.casing_pressure),
      temperature: num(form.temperature),
      choke_diameter: num(form.choke_diameter),
      planned_lifetime: num(form.planned_lifetime),
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setModalError('')
    try {
      const payload = buildPayload()
      if (editingId) {
        await api.updateWell(editingId, payload)
      } else {
        await api.createWell(payload)
      }
      await reload()
      closeModal()
    } catch (e) {
      setModalError(e.message)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (well) => {
    if (!window.confirm(`Удалить скважину ${well.well_number}? Все связанные события (ремонты, экспертизы, телеметрия) будут удалены безвозвратно.`)) return
    try {
      await api.deleteWell(well.id)
      await reload()
    } catch (e) {
      alert(e.message)
    }
  }

  return (
    <Layout>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 12, marginBottom: 20 }}>
        <div>
          <h1 className="wm-page-title">Скважины</h1>
          <p className="wm-page-subtitle">
            Всего: {wells.length} · активных: {wells.filter(w => w.status === 'active').length}
          </p>
        </div>
        {canEdit && (
          <button className="wm-btn wm-btn-primary" onClick={openCreate} disabled={!localities.length}>
            + Добавить скважину
          </button>
        )}
      </div>

      {!localities.length && !loading && (
        <div className="wm-error">
          Сначала создайте хотя бы одно месторождение — без него нельзя добавить скважину.
          {' '}<a href="/localities" style={{ color: '#b7f1ff', textDecoration: 'underline' }}>Перейти к месторождениям</a>
        </div>
      )}

      <div className="wm-toolbar">
        <input
          className="wm-field"
          style={{ height: 40, maxWidth: 320, padding: '0 12px', borderRadius: 10, border: '1px solid rgba(207,239,255,.55)', background: 'rgba(255,255,255,.08)', color: '#fff' }}
          placeholder="Поиск по номеру, месторождению, промыслу…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {error && <div className="wm-error">{error}</div>}

      <div className="wm-card">
        {loading ? (
          <div className="wm-empty">Загрузка…</div>
        ) : filtered.length === 0 ? (
          <div className="wm-empty">
            {search ? 'Ничего не найдено по запросу' : 'Скважин пока нет. Нажмите «Добавить скважину».'}
          </div>
        ) : (
          <table className="wm-table">
            <thead>
              <tr>
                <th>№</th>
                <th>Тип</th>
                <th>Статус</th>
                <th>Месторождение</th>
                <th>Промысел</th>
                <th>Глубина, м</th>
                <th>Давл. пласт., МПа</th>
                <th>Темп., °C</th>
                <th>Ввод</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(w => (
                <tr key={w.id}>
                  <td><b>{w.well_number}</b></td>
                  <td>{TYPE_LABELS[w.type] || w.type}</td>
                  <td><span className={`wm-badge wm-badge-${w.status}`}>{STATUS_LABELS[w.status] || w.status}</span></td>
                  <td>{w.locality_name}</td>
                  <td>{w.promysel_name || '—'}</td>
                  <td>{w.depth ?? '—'}</td>
                  <td>{w.reservoir_pressure ?? '—'}</td>
                  <td>{w.temperature ?? '—'}</td>
                  <td>{w.commissioning_date || '—'}</td>
                  <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                    {canEdit && (
                      <button className="wm-btn" style={{ padding: '6px 12px', fontSize: 12 }} onClick={() => openEdit(w)}>
                        Ред.
                      </button>
                    )}
                    {canDelete && (
                      <button className="wm-btn wm-btn-danger" style={{ padding: '6px 12px', fontSize: 12, marginLeft: 6 }} onClick={() => handleDelete(w)}>
                        Удал.
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {modalOpen && (
        <div className="wm-modal-backdrop" onClick={closeModal}>
          <div className="wm-modal" onClick={(e) => e.stopPropagation()}>
            <h3>{editingId ? `Редактировать скважину ${form.well_number}` : 'Новая скважина'}</h3>

            {modalError && <div className="wm-error">{modalError}</div>}

            <form onSubmit={handleSubmit} className="wm-form-grid">
              <div className="wm-field wm-form-full">
                <label>Номер скважины *</label>
                <input name="well_number" value={form.well_number} onChange={handleField} required disabled={!!editingId} />
              </div>

              <div className="wm-field">
                <label>Месторождение *</label>
                <select name="locality_id" value={form.locality_id} onChange={handleField} required>
                  <option value="">— выберите —</option>
                  {localities.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
                </select>
              </div>

              <div className="wm-field">
                <label>Промысел</label>
                <select name="promysel_id" value={form.promysel_id} onChange={handleField}>
                  <option value="">— не указан —</option>
                  {promysels.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
              </div>

              <div className="wm-field">
                <label>Тип</label>
                <select name="type" value={form.type} onChange={handleField}>
                  <option value="Добывающая">Добывающая</option>
                  <option value="Нагнетательная">Нагнетательная</option>
                  <option value="Разведочная">Разведочная</option>
                </select>
              </div>

              <div className="wm-field">
                <label>Статус</label>
                <select name="status" value={form.status} onChange={handleField}>
                  <option value="active">В работе</option>
                  <option value="in_repair">В ремонте</option>
                  <option value="suspended">Приостановлена</option>
                  <option value="plugged">Ликвидирована</option>
                </select>
              </div>

              <div className="wm-field wm-form-full">
                <label>Местоположение (координаты)</label>
                <input name="location" value={form.location} onChange={handleField} placeholder="45.1234, 38.5678" />
              </div>

              <div className="wm-field">
                <label>Глубина, м</label>
                <input name="depth" type="number" step="0.01" value={form.depth} onChange={handleField} />
              </div>

              <div className="wm-field">
                <label>Диаметр подвески, мм</label>
                <input name="hanger_diameter" type="number" step="0.01" value={form.hanger_diameter} onChange={handleField} />
              </div>

              <div className="wm-field">
                <label>Начало бурения</label>
                <input name="drilling_start_date" type="date" value={form.drilling_start_date} onChange={handleField} />
              </div>

              <div className="wm-field">
                <label>Окончание бурения</label>
                <input name="drilling_end_date" type="date" value={form.drilling_end_date} onChange={handleField} />
              </div>

              <div className="wm-field">
                <label>Сдача в эксплуатацию</label>
                <input name="commissioning_date" type="date" value={form.commissioning_date} onChange={handleField} />
              </div>

              <div className="wm-field">
                <label>Инвентарный номер</label>
                <input name="inventory_number" value={form.inventory_number} onChange={handleField} />
              </div>

              <div className="wm-field">
                <label>Пластовое давление, МПа</label>
                <input name="reservoir_pressure" type="number" step="0.01" value={form.reservoir_pressure} onChange={handleField} />
              </div>

              <div className="wm-field">
                <label>Буферное давление, МПа</label>
                <input name="buffer_pressure" type="number" step="0.01" value={form.buffer_pressure} onChange={handleField} />
              </div>

              <div className="wm-field">
                <label>Межколонное давление, МПа</label>
                <input name="casing_pressure" type="number" step="0.01" value={form.casing_pressure} onChange={handleField} />
              </div>

              <div className="wm-field">
                <label>Температура, °C</label>
                <input name="temperature" type="number" step="0.01" value={form.temperature} onChange={handleField} />
              </div>

              <div className="wm-field">
                <label>Диаметр штуцера, мм</label>
                <input name="choke_diameter" type="number" step="0.01" value={form.choke_diameter} onChange={handleField} />
              </div>

              <div className="wm-field">
                <label>Расчётный срок, лет</label>
                <input name="planned_lifetime" type="number" value={form.planned_lifetime} onChange={handleField} />
              </div>

              <div className="wm-modal-actions wm-form-full">
                <button type="button" className="wm-btn" onClick={closeModal} disabled={saving}>Отмена</button>
                <button type="submit" className="wm-btn wm-btn-primary" disabled={saving}>
                  {saving ? 'Сохранение…' : (editingId ? 'Сохранить' : 'Создать')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </Layout>
  )
}