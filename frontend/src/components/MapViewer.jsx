import { useEffect, useRef } from 'react'

const STATUS_COLORS = {
  active: '#22c55e',
  in_repair: '#f59e0b',
  suspended: '#94a3b8',
  plugged: '#ef4444',
}

function makeIcon(status) {
  const color = STATUS_COLORS[status] || '#3b82f6'
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="40" viewBox="0 0 28 40">
    <path d="M14 0C6.27 0 0 6.27 0 14c0 10.5 14 26 14 26s14-15.5 14-26C28 6.27 21.73 0 14 0z" fill="${color}" stroke="#fff" stroke-width="3"/>
    <circle cx="14" cy="14" r="5" fill="#fff"/>
  </svg>`
  return L.divIcon({
    html: svg,
    className: '',
    iconSize: [28, 40],
    iconAnchor: [14, 40],
    popupAnchor: [0, -36],
  })
}

export default function MapViewer({ wells, selectedId, onSelect }) {
  const containerRef = useRef(null)
  const mapRef = useRef(null)
  const markersRef = useRef({})

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    const center = wells.length > 0 && wells[0].latitude
      ? [wells[0].latitude, wells[0].longitude]
      : [45.25, 38.95]

    const map = L.map(containerRef.current).setView(center, wells.length > 0 ? 9 : 4)

        // Карта OSM без подписей (базовый слой)
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map)

    // Подписи на русском (прозрачный слой поверх)
    L.tileLayer('https://tile.openstreetmap.de:8002/tiles/1.0.0/labels/ru,en/{z}/{x}/{y}.png', {
      maxZoom: 19,
      pane: 'overlayPane',
    }).addTo(map)

    mapRef.current = map

    return () => {
      map.remove()
      mapRef.current = null
      markersRef.current = {}
    }
  }, [])

  useEffect(() => {
    if (!mapRef.current) return
    const map = mapRef.current

    Object.values(markersRef.current).forEach(m => m.remove())
    markersRef.current = {}

    wells.forEach(w => {
      if (!w.latitude || !w.longitude) return
      const marker = L.marker([w.latitude, w.longitude], { icon: makeIcon(w.status) })
        .addTo(map)
        .bindPopup(`<b>Скважина ${w.well_number}</b><br/>${w.promysel_name || '—'}`)
        .on('click', () => onSelect(w))
      markersRef.current[w.id] = marker
    })

    if (wells.length > 0) {
      const coords = wells
        .filter(w => w.latitude && w.longitude)
        .map(w => [w.latitude, w.longitude])
      if (coords.length > 0) map.fitBounds(coords, { padding: [40, 40] })
    }
  }, [wells, onSelect])

  useEffect(() => {
    if (!selectedId || !mapRef.current) return
    const marker = markersRef.current[selectedId]
    if (marker) {
      marker.openPopup()
      mapRef.current.panTo(marker.getLatLng())
    }
  }, [selectedId])

  return (
    <div
      ref={containerRef}
      style={{
        height: '100%',
        minHeight: 420,
        borderRadius: 14,
        overflow: 'hidden',
        border: '1px solid rgba(189,234,255,.25)',
      }}
    />
  )
}