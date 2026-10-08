function formatTimestamp(value, interval) {
  const timestamp = new Date(value)
  if (Number.isNaN(timestamp.getTime())) return value
  if (interval === '1D') {
    return timestamp.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
  }
  return timestamp.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
  })
}

export default function TimeSeriesChart({ title, description, points, series, unit, interval, zeroBaseline = false }) {
  const width = 760
  const height = 280
  const margin = { top: 18, right: 18, bottom: 48, left: 66 }
  const plotWidth = width - margin.left - margin.right
  const plotHeight = height - margin.top - margin.bottom
  const values = points.flatMap((point) => series.map(({ dataKey }) => point[dataKey] == null ? Number.NaN : Number(point[dataKey])).filter(Number.isFinite))

  if (!points.length || !values.length) {
    return <section className="panel glass-card time-machine-chart" aria-label={title}>
      <div className="panel-heading"><div><div className="panel-kicker">HISTORICAL TREND</div><h2>{title}</h2></div></div>
      {description && <p className="time-chart-description">{description}</p>}
      <div className="time-chart-empty" role="status">No records are available for this chart in the selected range.</div>
    </section>
  }

  const dataMin = Math.min(...values)
  const dataMax = Math.max(...values)
  const range = dataMax - dataMin
  const padding = range === 0 ? Math.max(Math.abs(dataMax) * 0.08, 1) : range * 0.12
  const yMin = zeroBaseline ? Math.min(0, dataMin) : dataMin - padding
  const yMax = Math.max(yMin + 1, dataMax + padding)
  const y = (value) => margin.top + ((yMax - value) / (yMax - yMin)) * plotHeight
  const x = (index) => margin.left + (points.length < 2 ? plotWidth / 2 : (index / (points.length - 1)) * plotWidth)
  const yTicks = Array.from({ length: 5 }, (_, index) => yMin + ((yMax - yMin) * index) / 4).reverse()
  const xTickIndexes = Array.from(new Set(Array.from({ length: Math.min(points.length, 5) }, (_, index) => Math.round((index * (points.length - 1)) / Math.max(Math.min(points.length, 5) - 1, 1)))))

  return <section className="panel glass-card time-machine-chart">
    <div className="panel-heading"><div><div className="panel-kicker">HISTORICAL TREND</div><h2>{title}</h2></div></div>
    {description && <p className="time-chart-description">{description}</p>}
    <div className="time-chart-legend" aria-label="Chart legend">{series.map((item) => <span key={item.dataKey}><i style={{ backgroundColor: item.color }} />{item.label}</span>)}</div>
    <div className="time-chart-svg-wrap">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${title}; horizontal axis shows time and vertical axis shows ${unit}`}>
        {yTicks.map((tick, index) => <g key={`y-${index}`}>
          <line x1={margin.left} x2={width - margin.right} y1={y(tick)} y2={y(tick)} className="time-chart-gridline" />
          <text x={margin.left - 9} y={y(tick) + 4} textAnchor="end" className="time-chart-axis-text">{tick.toFixed(0)}{unit}</text>
        </g>)}
        <line x1={margin.left} x2={margin.left} y1={margin.top} y2={height - margin.bottom} className="time-chart-axis-line" />
        <line x1={margin.left} x2={width - margin.right} y1={height - margin.bottom} y2={height - margin.bottom} className="time-chart-axis-line" />
        {series.map((item) => {
          let drawing = false
          const path = points.map((point, index) => {
            const value = point[item.dataKey] == null ? Number.NaN : Number(point[item.dataKey])
            if (!Number.isFinite(value)) {
              drawing = false
              return ''
            }
            const command = `${drawing ? 'L' : 'M'}${x(index).toFixed(1)},${y(value).toFixed(1)}`
            drawing = true
            return command
          }).join(' ')
          return <g key={item.dataKey}>
            <path d={path} fill="none" stroke={item.color} strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />
            {points.map((point, index) => {
              const value = point[item.dataKey] == null ? Number.NaN : Number(point[item.dataKey])
              if (!Number.isFinite(value)) return null
              const detail = `${item.label}: ${value.toFixed(2)}${unit} at ${new Date(point.timestamp).toLocaleString()}`
              return <circle key={`${item.dataKey}-${point.timestamp}`} cx={x(index)} cy={y(value)} r="3.2" fill={item.color} stroke="#0b1724" strokeWidth="1.5"><title>{detail}</title></circle>
            })}
          </g>
        })}
        {xTickIndexes.map((index) => <g key={`x-${index}`}>
          <line x1={x(index)} x2={x(index)} y1={height - margin.bottom} y2={height - margin.bottom + 4} className="time-chart-axis-line" />
          <text x={x(index)} y={height - margin.bottom + 19} textAnchor="middle" className="time-chart-axis-text">{formatTimestamp(points[index].timestamp, interval)}</text>
        </g>)}
        <text x="16" y={height / 2} transform={`rotate(-90 16 ${height / 2})`} textAnchor="middle" className="time-chart-axis-title">{unit}</text>
        <text x={margin.left + plotWidth / 2} y={height - 5} textAnchor="middle" className="time-chart-axis-title">Time</text>
      </svg>
    </div>
  </section>
}
