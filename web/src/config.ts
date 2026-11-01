// URL de la API (issue #9). En dev apunta al uvicorn local; en producción se
// puede sobreescribir con VITE_API_URL (ver .env.example).
export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

// Centro aproximado de pipeline/config.py:BBOX ([-16.75, 28.10, -16.25, 28.60]).
export const MAP_CENTER: [number, number] = [28.35, -16.5]
export const MAP_DEFAULT_ZOOM = 11

// Superficie oficial reportada (pipeline/config.py:REPORTED_AREA_HA), para
// comparar contra el total detectado en el panel de estadísticas.
export const REPORTED_AREA_HA = 14_751
