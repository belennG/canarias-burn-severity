import type { Feature, FeatureCollection } from "geojson"
import type { Layer, StyleFunction } from "leaflet"
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet"
import { MAP_CENTER, MAP_DEFAULT_ZOOM } from "./config"
import { SEVERITY_COLORS, type SeverityProperties } from "./severity"

interface SeverityMapProps {
  data: FeatureCollection
}

const style: StyleFunction = (feature) => {
  const severity = (feature as Feature<never, SeverityProperties>).properties.severity
  return {
    color: "#444",
    weight: 0.3,
    fillColor: SEVERITY_COLORS[severity] ?? "#999",
    fillOpacity: 0.75,
  }
}

function onEachFeature(feature: Feature, layer: Layer) {
  const { severity, area_ha } = feature.properties as SeverityProperties
  // useGrouping explícito: "auto" (el default) no pone separador de miles en
  // números de 4 cifras en es-ES (1048,9 en vez de 1.048,9).
  const area = area_ha.toLocaleString("es-ES", { useGrouping: true })
  layer.bindPopup(`${severity}<br>${area} ha`)
}

export default function SeverityMap({ data }: SeverityMapProps) {
  return (
    <MapContainer center={MAP_CENTER} zoom={MAP_DEFAULT_ZOOM} className="map">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <GeoJSON data={data} style={style} onEachFeature={onEachFeature} />
    </MapContainer>
  )
}
