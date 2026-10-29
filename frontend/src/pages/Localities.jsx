import { useEffect, useMemo, useState } from 'react'
import Layout from '../components/Layout'
import MapPicker from '../components/MapPicker'
import { useAuth } from '../auth'
import { api } from '../api'

const EMPTY = {
  name: '', region: '', field_type: '', discovery_year: '',
  area_km2: '', latitude: '', longitude: '',
}

const FIELD_TYPES = ['газовое', 'газоконденсатное', 'нефтегазовое', 'нефтяное']

export default function Localities() {
  const { user } = useAuth()
  const canEdit = user?.role === 'admin' || user?.role === 'engineer'
  const canDelete = user?.role === 'admin'

  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')

  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [saving, setSaving] = useState(false)
  const [modalError, setModalError] = useState('')

  const reload = async () => {
    setLoading(true); setError('')
    try { setItems(await api.listLocalities()) }
    catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }
  useEffect(() => { reload() }, [])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return items
    return items.filter(i =>
      i.name.toLowerCase().includes(q) || i.region.toLowerCase().includes(q)
    )
  }, [items, search])

  const openCreate = () => {
    setEditingId(null); setForm(EMPTY); setModalError(''); setModalOpen(true)
  }
  const openEdit = (i) => {
    setEditingId(i.id)
    setForm({
      name: i.name, region: i.region, field_type: i.field_type || '',
      discovery_year: i.discovery_year ?? '', area_km2: i.area_km2 ?? '',
      latitude: i.latitude ?? '', longitude: i.longitude ?? '',
    })
    setModalError(''); setModalOpen(true)
  }
  const closeModal = () => { setModalOpen(false); setEditingId(null); setForm(EMPTY); setModalError('') }

  const submit = async (e) => {
    e.preventDefault(); setSaving(true); setModalError('')
    try {
      const num = v => v === '' || v == null ? null : Number(v)
      const payload = {
        name: form.name, region: form.region,
        field_type: form.field_type || null,
        discovery_year: num(form.discovery_year),
        area_km2: num(form.area_km2),
        latitude: num(form.latitude),
        longitude: num(form.longitude),
      }
      if (editingId) await api.updateLocality(editingId, payload)
      else await api.createLocality(payload)
      await reload(); closeModal()
    } catch (e) { setModalError(e.message) }
    finally { setSaving(false) }
  }

  const del = async (i) => {
    if (!window.confirm(`Удалить месторождение «${i.name}»?`)) return
    try { await api.deleteLocality(i.id); await reload() }
    catch (e) { alert(e.message) }
  }

  return (
    <Layout>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 12, marginBottom: 20 }}>
        <div>
          <h1 className="wm-page-title">Месторождения</h1>
          <p className="wm-page-subtitle">Всего: {items.length}</p>
        </div>
        {canEdit && <button className="wm-btn wm-btn-primary" onClick={openCreate}>+ Добавить месторождение</button>}
      </div>

      <div className="wm-toolbar">
        <input className="wm-field" style={{ height: 40, maxWidth: 320, padding: '0 12px', borderRadius: 10, border: '1px solid rgba(207,239,255,.55)', background: 'rgba(255,255,255,.08)', color: '#fff' }}
          placeholder="Поиск по названию или региону…" value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      {error && <div className="wm-error">{error}</div>}

      <div className="wm-card">
        {loading ? <div className="wm-empty">Загрузка…</div>
          : filtered.length === 0 ? <div className="wm-empty">Ничего не найдено</div>
          : (
            <table className="wm-table">
              <thead>
                <tr>
                  <th>#</th><th>Название</th><th>Регион</th><th>Тип</th>
                  <th>Год</th><th>Площадь, км²</th><th>Координаты</th><th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(i => (
                  <tr key={i.id}>
                    <td>{i.id}</td>
                    <td><b>{i.name}</b></td>
                    <td>{i.region}</td>
                    <td>{i.field_type || '—'}</td>
                    <td>{i.discovery_year || '—'}</td>
                    <td>{i.area_km2 ?? '—'}</td>
                    <td>{i.latitude && i.longitude ? `${i.latitude}, ${i.longitude}` : '—'}</td>
                    <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                      {canEdit && <button className="wm-btn" style={{ padding: '6px 12px', fontSize: 12 }} onClick={() => openEdit(i)}>Ред.</button>}
                      {canDelete && <button className="wm-btn wm-btn-danger" style={{ padding: '6px 12px', fontSize: 12, marginLeft: 6 }} onClick={() => del(i)}>Удал.</button>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
      </div>

      {modalOpen && (
        <div className="wm-modal-backdrop" onClick={closeModal}>
          <div className="wm-modal" onClick={e => e.stopPropagation()}>
            <h3>{editingId ? 'Редактировать месторождение' : 'Новое месторождение'}</h3>
            {modalError && <div className="wm-error">{modalError}</div>}
            <form onSubmit={submit} className="wm-form-grid">
              <div className="wm-field wm-form-full">
                <label>Название *</label>
                <input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} required />
              </div>
              <div className="wm-field wm-form-full">
                <label>Регион *</label>
                <input value={form.region} onChange={e => setForm(f => ({ ...f, region: e.target.value }))} required />
              </div>
              <div className="wm-field">
                <label>Тип месторождения</label>
                <select value={form.field_type} onChange={e => setForm(f => ({ ...f, field_type: e.target.value }))}>
                  <option value="">— не указан —</option>
                  {FIELD_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div className="wm-field">
                <label>Год открытия</label>
                <input type="number" value={form.discovery_year} onChange={e => setForm(f => ({ ...f, discovery_year: e.target.value }))} />
              </div>
              <div className="wm-field">
                <label>Площадь, км²</label>
                <input type="number" step="0.01" value={form.area_km2} onChange={e => setForm(f => ({ ...f, area_km2: e.target.value }))} />
              </div>
              <div className="wm-field wm-form-full">
                <label>Координаты</label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                  <input placeholder="Широта" value={form.latitude} onChange={e => setForm(f => ({ ...f, latitude: e.target.value }))} />
                  <input placeholder="Долгота" value={form.longitude} onChange={e => setForm(f => ({ ...f, longitude: e.target.value }))} />
                </div>
              </div>
              <div className="wm-field wm-form-full">
                <MapPicker
                  latitude={form.latitude ? Number(form.latitude) : null}
                  longitude={form.longitude ? Number(form.longitude) : null}
                  onChange={({ latitude, longitude }) => setForm(f => ({ ...f, latitude, longitude }))}
                />
              </div>
              <div className="wm-modal-actions wm-form-full">
                <button type="button" className="wm-btn" onClick={closeModal} disabled={saving}>Отмена</button>
                <button type="submit" className="wm-btn wm-btn-primary" disabled={saving}>{saving ? 'Сохранение…' : (editingId ? 'Сохранить' : 'Создать')}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </Layout>
  )
}