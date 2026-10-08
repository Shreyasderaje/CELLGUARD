import { useEffect, useMemo, useState } from 'react'
import { Activity, AlertTriangle, CalendarDays, Clock3, Factory, Gauge, LoaderCircle, Search, ShieldAlert } from 'lucide-react'
import { motion } from 'framer-motion'
import { fetchTelemetryHistory } from '../api/telemetry'
import TimeSeriesChart from '../components/TimeSeriesChart'

const parameterCharts = [
  { key: 'average_current', title: 'Average current', unit: ' A', color: '#42c9d5' },
  { key: 'average_temperature', title: 'Average temperature', unit: ' °C', color: '#e9ad62' },
  { key: 'average_pressure', title: 'Average pressure', unit: ' bar', color: '#70d6a8' },
  { key: 'average_welding_time', title: 'Average welding time', unit: ' s', color: '#8eaeff' },
]

function shortTimestamp(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
}

function SummaryCard({ label, value, detail, icon: Icon, tone }) {
  return <article className="metric-card glass-card time-summary-card"><div className="metric-top"><span>{label}</span><span className={`metric-icon ${tone}`}><Icon size={18} /></span></div><div className="metric-value">{value}</div><div className="metric-foot">{detail}</div></article>
}

function HistoryState({ type, message }) {
  const loading = type === 'loading'
  const Icon = loading ? LoaderCircle : type === 'error' ? AlertTriangle : Clock3
  return <section className={`panel glass-card time-history-state ${type}`} role={type === 'error' ? 'alert' : 'status'}><span className="time-state-icon"><Icon className={loading ? 'time-state-spinner' : ''} size={22} /></span><div><strong>{loading ? 'Loading historical records' : type === 'error' ? 'History unavailable' : 'No matching records'}</strong><p>{message}</p></div></section>
}

export default function QualityTimeMachine() {
  const [filters, setFilters] = useState({ startDate: '', endDate: '', machineId: 'ALL' })
  const [dateBounds, setDateBounds] = useState({ minimum: '', maximum: '' })
  const [history, setHistory] = useState(null)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    fetchTelemetryHistory({ signal: controller.signal })
      .then((payload) => {
        setHistory(payload)
        const minimum = payload.earliest_timestamp?.slice(0, 10) ?? ''
        const maximum = payload.latest_timestamp?.slice(0, 10) ?? ''
        setDateBounds({ minimum, maximum })
        setFilters((current) => ({ ...current, startDate: minimum, endDate: maximum }))
        setStatus('ready')
      })
      .catch((requestError) => {
        if (requestError.name !== 'AbortError') {
          setError(requestError.message || 'The factory history could not be loaded.')
          setStatus('error')
        }
      })
    return () => controller.abort()
  }, [])

  const summary = useMemo(() => {
    const points = history?.time_series ?? []
    const defects = points.reduce((total, point) => total + point.defect_count, 0)
    const inspected = history?.record_count ?? 0
    return {
      inspected,
      defects,
      rate: inspected ? (defects / inspected) * 100 : 0,
      range: inspected ? `${shortTimestamp(history.earliest_timestamp)} – ${shortTimestamp(history.latest_timestamp)}` : 'No matching dates',
    }
  }, [history])

  function updateFilter(key, value) {
    setFilters((current) => ({ ...current, [key]: value }))
  }

  async function applyFilters(event) {
    event.preventDefault()
    if (filters.startDate && filters.endDate && filters.startDate > filters.endDate) {
      setError('Start date must be on or before the end date.')
      setStatus('error')
      setHistory(null)
      return
    }
    setStatus('loading')
    setError('')
    setHistory(null)
    try {
      const payload = await fetchTelemetryHistory(filters)
      setHistory(payload)
      setStatus('ready')
    } catch (requestError) {
      setError(requestError.message || 'The selected history could not be loaded.')
      setStatus('error')
    }
  }

  const points = history?.time_series ?? []
  const machines = history?.available_machines ?? ['M01', 'M02', 'M03', 'M04']

  return <motion.div className="page-content time-machine-page" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .2 }}>
    <section className="welcome-row time-machine-welcome"><div><div className="eyebrow"><span className="eyebrow-line" />HISTORICAL ANALYTICS · QUALITY TRENDS</div><h1>Quality Time Machine</h1><p className="page-description">Explore recorded quality and process patterns across the available dataset.</p></div></section>

    <div className="time-data-disclosure"><AlertTriangle size={17} /><span><strong>Synthetic demonstration data — not real production history.</strong> Timestamps are generated at ten-minute intervals for this dataset.</span></div>

    <form className="panel glass-card time-filter-panel" onSubmit={applyFilters}>
      <div className="panel-heading"><div><div className="panel-kicker">HISTORY FILTERS</div><h2>Select a time window and machine</h2></div><span className="time-range-note"><CalendarDays size={15} /> Dataset dates {dateBounds.minimum || '—'} to {dateBounds.maximum || '—'}</span></div>
      <div className="time-filter-controls">
        <label className="time-filter-field"><span>Start date</span><input type="date" required value={filters.startDate} min={dateBounds.minimum || undefined} max={dateBounds.maximum || undefined} onChange={(event) => updateFilter('startDate', event.target.value)} /></label>
        <label className="time-filter-field"><span>End date</span><input type="date" required value={filters.endDate} min={dateBounds.minimum || undefined} max={dateBounds.maximum || undefined} onChange={(event) => updateFilter('endDate', event.target.value)} /></label>
        <label className="time-filter-field machine-filter"><span>Machine</span><select value={filters.machineId} onChange={(event) => updateFilter('machineId', event.target.value)}><option value="ALL">All machines</option>{machines.map((machine) => <option key={machine} value={machine}>{machine}</option>)}</select></label>
        <button className="time-apply-button" type="submit" disabled={status === 'loading'}><Search size={17} />Apply Filters</button>
      </div>
    </form>

    {status === 'loading' && <HistoryState type="loading" message="Reading matching records and calculating time buckets from the factory CSV." />}
    {status === 'error' && <HistoryState type="error" message={error} />}

    {status === 'ready' && history && <>
      <section className="metric-grid time-summary-grid" aria-label="Filtered history summary">
        <SummaryCard label="Inspected records" value={summary.inspected.toLocaleString()} detail="Matching CSV records" icon={Factory} tone="cyan" />
        <SummaryCard label="Defects" value={summary.defects.toLocaleString()} detail="Records marked Defect" icon={ShieldAlert} tone="amber" />
        <SummaryCard label="Defect rate" value={`${summary.rate.toFixed(2)}%`} detail="Defects ÷ inspected records" icon={Activity} tone="green" />
        <SummaryCard label="Matched date range" value={history.record_count ? summary.range : '—'} detail={history.bucket_interval ? `Bucketed ${history.bucket_interval}` : 'No matching records'} icon={CalendarDays} tone="blue" />
      </section>

      {history.record_count === 0 && <HistoryState type="empty" message="No records match the selected dates and machine. Adjust the filters to explore another range." />}

      <TimeSeriesChart title="Defect rate over time" description="Share of inspected records marked as defective in each time bucket." points={points} series={[{ dataKey: 'defect_rate', label: 'Defect rate', color: '#ee8f8f' }]} unit="%" interval={history.bucket_interval} zeroBaseline />
      <TimeSeriesChart title="Defects and inspected records" description="Compare defect counts with total inspected batches in each time bucket." points={points} series={[{ dataKey: 'defect_count', label: 'Defects', color: '#ee8f8f' }, { dataKey: 'total_inspected', label: 'Inspected records', color: '#48cbd5' }]} unit=" records" interval={history.bucket_interval} zeroBaseline />

      <section className="time-parameter-section"><div className="time-section-heading"><div><div className="panel-kicker">PROCESS TELEMETRY</div><h2>Average process parameters over time</h2></div><span>Values are averages of records in each bucket</span></div><div className="time-parameter-grid">{parameterCharts.map((chart) => <TimeSeriesChart key={chart.key} title={chart.title} points={points} series={[{ dataKey: chart.key, label: chart.title, color: chart.color }]} unit={chart.unit} interval={history.bucket_interval} />)}</div></section>
      <footer className="time-machine-footer"><span>{history.data_source}</span><span>{history.earliest_timestamp ? `Actual matching records: ${history.earliest_timestamp} to ${history.latest_timestamp}` : 'No timestamps matched these filters.'}</span></footer>
    </>}
  </motion.div>
}
