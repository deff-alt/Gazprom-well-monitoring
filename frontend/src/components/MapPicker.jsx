import { useEffect, useRef } from 'react'

export default function MapPicker({ latitude, longitude, onChange }) {
  const mapRef = useRef(null)
  const markerRef = useRef(null)
  const containerRef = useRef(null)

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return
    const lat = latitude || 55.7558
    const lng = longitude || 37.6173
    const map = L.map(containerRef.current).setView([lat, lng], latitude ? 8 : 4)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap',
    }).addTo(map)
    mapRef.current = map

    if (latitude && longitude) {
      markerRef.current = L.marker([latitude, longitude]).addTo(map)
    }

    map.on('click', (e) => {
      const { lat, lng } = e.latlng
      if (markerRef.current) markerRef.current.setLatLng([lat, lng])
      else markerRef.current = L.marker([lat, lng]).addTo(map)
      onChange({ latitude: lat.toFixed(6), longitude: lng.toFixed(6) })
    })

    return () => { map.remove(); mapRef.current = null; markerRef.current = null }
  }, [])

  return (
    <div>
      <div
        ref={containerRef}
        style={{ height: 260, borderRadius: 12, overflow: 'hidden', border: '1px solid rgba(207,239,255,.4)' }}
      />
      <small style={{ color: '#b8d9f1', fontSize: 11 }}>
        Кликните на карте, чтобы поставить точку
      </small>
    </div>
  )
}