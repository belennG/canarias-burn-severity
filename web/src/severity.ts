// Mismos colores y orden de clases que pipeline/calculate_severity.py
// (SEVERITY_COLORS / config.SEVERITY_THRESHOLDS). Python y el navegador no
// comparten código, así que esta paleta se mantiene a mano en los dos lados.
export const SEVERITY_COLORS: Record<string, string> = {
  "Rebrote alto": "#1a9641",
  "Rebrote bajo": "#a6d96a",
  "No quemado": "#f7f7b0",
  "Severidad baja": "#fee08b",
  "Severidad moderada-baja": "#fdae61",
  "Severidad moderada-alta": "#f46d43",
  "Severidad alta": "#a50026",
}

export const SEVERITY_CLASSES = Object.keys(SEVERITY_COLORS)

export interface SeverityProperties {
  class_id: number
  severity: string
  area_ha: number
}

export interface SeverityStats {
  class_id: number
  severity: string
  polygon_count: number
  area_ha: number
}

// Mismas clases "quemadas" que pipeline/validate.py:BURNED_CLASSES (todo lo
// que no sea "No quemado" o rebrote de vegetación sana).
export const BURNED_CLASSES = [
  "Severidad baja",
  "Severidad moderada-baja",
  "Severidad moderada-alta",
  "Severidad alta",
]
