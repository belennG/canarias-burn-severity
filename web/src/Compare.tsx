import { useState } from "react"
import { IMAGE_AFTER_URL, IMAGE_BEFORE_URL } from "./config"

export default function Compare() {
  const [position, setPosition] = useState(50)

  return (
    <div className="compare">
      <div className="compare-images">
        <img src={IMAGE_BEFORE_URL} alt="Antes del incendio" />
        <div className="compare-after" style={{ clipPath: `inset(0 0 0 ${position}%)` }}>
          <img src={IMAGE_AFTER_URL} alt="Después del incendio" />
        </div>
        <div className="compare-handle" style={{ left: `${position}%` }} />
        <span className="compare-label compare-label-left">Antes</span>
        <span className="compare-label compare-label-right">Después</span>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        value={position}
        onChange={(e) => setPosition(Number(e.target.value))}
        className="compare-slider"
        aria-label="Deslizar entre antes y después"
      />
    </div>
  )
}
