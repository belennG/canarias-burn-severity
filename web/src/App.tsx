import type { FeatureCollection } from "geojson"
import { useEffect, useState } from "react"
import { API_URL, IS_STATIC_BUILD, SEVERITY_URL } from "./config"
import Compare from "./Compare"
import SeverityMap from "./SeverityMap"
import StatsPanel from "./StatsPanel"

type Status = "cargando" | "ok" | "error"
type Tab = "mapa" | "comparar"

export default function App() {
  const [status, setStatus] = useState<Status>("cargando")
  const [data, setData] = useState<FeatureCollection | null>(null)
  const [tab, setTab] = useState<Tab>("mapa")

  useEffect(() => {
    fetch(SEVERITY_URL)
      .then((res) => {
        if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
        return res.json()
      })
      .then((geojson: FeatureCollection) => {
        setData(geojson)
        setStatus("ok")
      })
      .catch(() => setStatus("error"))
  }, [])

  return (
    <div className="app">
      <header>
        <h1>Severidad del incendio — Tenerife, agosto 2023</h1>
      </header>
      <nav className="tabs">
        <button className={tab === "mapa" ? "active" : ""} onClick={() => setTab("mapa")}>
          Mapa
        </button>
        <button className={tab === "comparar" ? "active" : ""} onClick={() => setTab("comparar")}>
          Antes / después
        </button>
      </nav>
      {status === "cargando" && <p className="status">Cargando polígonos…</p>}
      {status === "error" && (
        <p className="status status-error">
          {IS_STATIC_BUILD
            ? "No se pudieron cargar los datos estáticos."
            : `No se pudo conectar con la API (${API_URL}). ¿Está corriendo uvicorn?`}
        </p>
      )}
      {status === "ok" && data && tab === "mapa" && (
        <div className="map-wrapper">
          <SeverityMap data={data} />
          <StatsPanel />
        </div>
      )}
      {status === "ok" && data && tab === "comparar" && <Compare />}
    </div>
  )
}
