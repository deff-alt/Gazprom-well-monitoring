import { useEffect, useMemo, useState } from 'react'
import Layout from '../components/Layout'
import { useAuth } from '../auth'
import { api } from '../api'

const ROLES = {
  admin: 'Администратор',
  engineer: 'Инженер-технолог',
  head: 'Начальник промысла',
  operator: 'Оператор',
}

const EMPTY_FORM = {
  username: '',
  full_name: '',
  password: '',
  role: 'operator',
  promysel_id: '',
}

export default function Users() {
  const { user: me } = useAuth()

  const [items, setItems] = useState([])
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
      const [u, p] = await Promise.all([api.listUsers(), api.listPromysels()])
      setItems(u)
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
    if (!q) return items
    return items.filter(i =>
      i.username.toLowerCase().includes(q) ||
      (i.full_name || '').toLowerCase().includes(q) ||
      (ROLES[i.role] || i.role).toLowerCase().includes(q) ||
      (i.promysel_name || '').toLowerCase().includes(q)
    )
  }, [items, search])

  const openCreate = () => {
    setEditingId(null)
    setForm(EMPTY_FORM)
    setModalError('')
    setModalOpen(true)
  }

  const openEdit = (item) => {
    setEditingId(item.id)
    setForm({
      username: item.username,
      full_name: item.full_name || '',
      password: '',
      role: item.role,
      promysel_id: item.promysel_id || '',
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

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setModalError('')
    try {
      const payload = {
        full_name: form.full_name,
        role: form.role,
        promysel_id: form.promysel_id ? Number(form.promysel_id) : null,
      }
      if (editingId) {
        if (form.password) payload.password = form.password
        await api.updateUser(editingId, payload)
      } else {
        await api.createUser({
          username: form.username,
          password: form.password,
          ...payload,
        })
      }
      await reload()
      closeModal()
    } catch (e) {
      setModalError(e.message)
    } finally {
      setSaving(false)
    }
  }

  const toggleActive = async (item) => {
    try {
      await api.updateUser(item.id, { is_active: !item.is_active })
      await reload()
    } catch (e) {
      alert(e.message)
    }
  }

  const handleDelete = async (item) => {
    if (!window.confirm(`Удалить пользователя «${item.username}»?`)) return
    try {
      await api.deleteUser(item.id)
      await reload()
    } catch (e) {
      alert(e.message)
    }
  }

  return (
    <Layout>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: 12, marginBottom: 20 }}>
        <div>
          <h1 className="wm-page-title">Пользователи</h1>
          <p className="wm-page-subtitle">Всего: {items.length}</p>
        </div>
        <button className="wm-btn wm-btn-primary" onClick={openCreate}>+ Добавить пользователя</button>
      </div>

      <div className="wm-toolbar">
        <input
          className="wm-field"
          style={{
            height: 40, maxWidth: 320, padding: '0 12px', borderRadius: 10,
            border: '1px solid rgba(207,239,255,.55)',
            background: 'rgba(255,255,255,.08)', color: '#fff',
          }}
          placeholder="Поиск по логину, ФИО, роли, промыслу…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {error && <div className="wm-error">{error}</div>}

      <div className="wm-card">
        {loading ? (
          <div className="wm-empty">Загрузка…</div>
        ) : filtered.length === 0 ? (
          <div className="wm-empty">{search ? 'Ничего не найдено' : 'Пользователей пока нет'}</div>
        ) : (
          <table className="wm-table">
            <thead>
              <tr>
                <th>Логин</th>
                <th>ФИО</th>
                <th>Роль</th>
                <th>Промысел</th>
                <th>Статус</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => {
                const isSelf = item.id === me?.id
                return (
                  <tr key={item.id}>
                    <td><b>{item.username}</b>{isSelf && <span style={{ marginLeft: 6, fontSize: 10, color: '#b8d9f1' }}>(вы)</span>}</td>
                    <td>{item.full_name || '—'}</td>
                    <td>{ROLES[item.role] || item.role}</td>
                    <td>{item.promysel_name || '—'}</td>
                    <td>
                      <span className={'wm-badge ' + (item.is_active ? 'wm-badge-active' : 'wm-badge-plugged')}>
                        {item.is_active ? 'Активен' : 'Заблокирован'}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                      <button
                        className="wm-btn"
                        style={{ padding: '6px 12px', fontSize: 12 }}
                        onClick={() => openEdit(item)}
                      >
                        Ред.
                      </button>
                      {!isSelf && (
                        <>
                          <button
                            className="wm-btn"
                            style={{ padding: '6px 12px', fontSize: 12, marginLeft: 6 }}
                            onClick={() => toggleActive(item)}
                          >
                            {item.is_active ? 'Блок' : 'Разблок'}
                          </button>
                          <button
                            className="wm-btn wm-btn-danger"
                            style={{ padding: '6px 12px', fontSize: 12, marginLeft: 6 }}
                            onClick={() => handleDelete(item)}
                          >
                            Удал.
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      {modalOpen && (
        <div className="wm-modal-backdrop" onClick={closeModal}>
          <div className="wm-modal" onClick={(e) => e.stopPropagation()}>
            <h3>{editingId ? 'Редактировать пользователя' : 'Новый пользователь'}</h3>
            {modalError && <div className="wm-error">{modalError}</div>}
            <form onSubmit={handleSubmit} className="wm-form-grid">
              <div className="wm-field wm-form-full">
                <label>Логин *</label>
                <input
                  value={form.username}
                  onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
                  required
                  disabled={!!editingId}
                />
              </div>
              <div className="wm-field wm-form-full">
                <label>ФИО</label>
                <input
                  value={form.full_name}
                  onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))}
                />
              </div>
              <div className="wm-field wm-form-full">
                <label>{editingId ? 'Новый пароль (оставьте пустым, чтобы не менять)' : 'Пароль *'}</label>
                <input
                  type="password"
                  value={form.password}
                  onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                  required={!editingId}
                  minLength={6}
                />
              </div>
              <div className="wm-field">
                <label>Роль *</label>
                <select
                  value={form.role}
                  onChange={e => setForm(f => ({ ...f, role: e.target.value }))}
                  required
                  disabled={editingId === me?.id}
                >
                  <option value="operator">Оператор</option>
                  <option value="engineer">Инженер-технолог</option>
                  <option value="head">Начальник промысла</option>
                  <option value="admin">Администратор</option>
                </select>
              </div>
              <div className="wm-field">
                <label>Промысел (для начальника обязателен)</label>
                <select
                  value={form.promysel_id}
                  onChange={e => setForm(f => ({ ...f, promysel_id: e.target.value }))}
                >
                  <option value="">— не указан —</option>
                  {promysels.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
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