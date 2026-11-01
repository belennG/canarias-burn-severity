import type { FeatureCollection } from "geojson"
import { useEffect, useState } from "react"
import { API_URL } from "./config"
import Legend from "./Legend"
import SeverityMap from "./SeverityMap"

type Status = "cargando" | "ok" | "error"

export default function App() {
  const [status, setStatus] = useState<Status>("cargando")
  const [data, setData] = useState<FeatureCollection | null>(null)

  useEffect(() => {
    fetch(`${API_URL}/severity`)
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
      {status === "cargando" && <p className="status">Cargando polígonos…</p>}
      {status === "error" && (
        <p className="status status-error">
          No se pudo conectar con la API ({API_URL}). ¿Está corriendo <code>uvicorn</code>?
        </p>
      )}
      {status === "ok" && data && (
        <div className="map-wrapper">
          <SeverityMap data={data} />
          <Legend />
        </div>
      )}
    </div>
  )
}
