// URL de la API (issue #9), solo para `npm run dev`. El build de producción
// (issue #12, Netlify) no tiene ninguna API corriendo: usa en cambio los
// archivos estáticos de public/ que genera pipeline/export_static.py.
export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000"
export const IS_STATIC_BUILD = import.meta.env.PROD

export const SEVERITY_URL = IS_STATIC_BUILD ? "/severity.geojson" : `${API_URL}/severity`
export const STATS_URL = IS_STATIC_BUILD ? "/stats.json" : `${API_URL}/severity/stats`
export const IMAGE_BEFORE_URL = IS_STATIC_BUILD
  ? "/imagery/rgb_before.jpg"
  : `${API_URL}/imagery/rgb_before.png`
export const IMAGE_AFTER_URL = IS_STATIC_BUILD
  ? "/imagery/rgb_after.jpg"
  : `${API_URL}/imagery/rgb_after.png`

// Centro aproximado de pipeline/config.py:BBOX ([-16.75, 28.10, -16.25, 28.60]).
export const MAP_CENTER: [number, number] = [28.35, -16.5]
export const MAP_DEFAULT_ZOOM = 11

// Superficie oficial reportada (pipeline/config.py:REPORTED_AREA_HA), para
// comparar contra el total detectado en el panel de estadísticas.
export const REPORTED_AREA_HA = 14_751
