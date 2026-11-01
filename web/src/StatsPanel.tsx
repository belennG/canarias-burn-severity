import { useEffect, useState } from "react"
import { REPORTED_AREA_HA, STATS_URL } from "./config"
import { BURNED_CLASSES, SEVERITY_COLORS, type SeverityStats } from "./severity"

// useGrouping explícito: "auto" (el default) no pone separador de miles en
// números de 4 cifras en es-ES (1048,9 en vez de 1.048,9).
const fmt = (n: number) => n.toLocaleString("es-ES", { maximumFractionDigits: 1, useGrouping: true })

export default function StatsPanel() {
  const [stats, setStats] = useState<SeverityStats[] | null>(null)

  useEffect(() => {
    fetch(STATS_URL)
      .then((res) => res.json())
      .then(setStats)
      .catch(() => setStats(null))
  }, [])

  if (!stats) return null

  const totalQuemadoHa = stats
    .filter((row) => BURNED_CLASSES.includes(row.severity))
    .reduce((sum, row) => sum + row.area_ha, 0)

  return (
    <div className="panel stats-panel">
      <strong>Severidad — hectáreas por clase</strong>
      <ul>
        {stats.map((row) => (
          <li key={row.class_id}>
            <span className="legend-swatch" style={{ backgroundColor: SEVERITY_COLORS[row.severity] }} />
            <span className="stats-label">{row.severity}</span>
            <span className="stats-value">{fmt(row.area_ha)} ha</span>
          </li>
        ))}
      </ul>
      <p className="stats-total">
        Total quemado: <strong>{fmt(totalQuemadoHa)} ha</strong>
        <br />
        ({((totalQuemadoHa / REPORTED_AREA_HA) * 100).toFixed(0)}% de las {fmt(REPORTED_AREA_HA)} ha
        reportadas oficialmente)
      </p>
    </div>
  )
}
