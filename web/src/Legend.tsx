import { SEVERITY_CLASSES, SEVERITY_COLORS } from "./severity"

export default function Legend() {
  return (
    <div className="legend">
      <strong>Severidad</strong>
      <ul>
        {SEVERITY_CLASSES.map((label) => (
          <li key={label}>
            <span className="legend-swatch" style={{ backgroundColor: SEVERITY_COLORS[label] }} />
            {label}
          </li>
        ))}
      </ul>
    </div>
  )
}
