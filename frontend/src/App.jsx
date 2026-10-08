import { useEffect, useState } from 'react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import PlaceholderPage from './pages/PlaceholderPage'
import { AnimatePresence, motion } from 'framer-motion'
import { Activity, Cpu, Factory, Search, ShieldAlert } from 'lucide-react'
import { fetchTelemetrySummary } from './api/telemetry'

const metricDefinitions = [
  { key: 'total_inspections', label: 'Total inspections', format: (value) => value.toLocaleString(), icon: Search, tone: 'cyan' },
  { key: 'defect_rate', label: 'Defect rate', format: (value) => `${value.toFixed(1)}%`, icon: Activity, tone: 'amber' },
  { key: 'high_risk_batches', label: 'High-risk batches', format: (value) => value.toLocaleString(), icon: ShieldAlert, tone: 'amber' },
  { key: 'active_workstations', label: 'Active workstations', format: (value) => value.toLocaleString(), icon: Cpu, tone: 'green' },
]

function MetricCard({ metric, value, index }) {
  const Icon = metric.icon
  return <motion.article className="metric-card glass-card" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .32, delay: index * .055 }}><div className="metric-top"><span>{metric.label}</span><span className={`metric-icon ${metric.tone}`}><Icon size={18} /></span></div><div className="metric-value">{value}</div><div className="metric-foot">Synthetic factory telemetry</div></motion.article>
}

function LoadingMetrics() {
  return <section className="metric-grid" aria-label="Loading telemetry" aria-busy="true">{metricDefinitions.map((metric) => <div className="metric-card glass-card telemetry-skeleton" key={metric.key}><span className="skeleton-label" /><span className="skeleton-value" /><span className="skeleton-caption">Loading CSV summary...</span></div>)}</section>
}

function MachineCards({ machines }) {
  return <div className="machine-grid">{machines.map((machine) => <motion.article className="machine-card machine-telemetry-card" key={machine.machine_id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}><div className="machine-card-top"><span className="machine-icon"><Factory size={19} /></span><strong>{machine.machine_id}</strong><span className={`machine-status ${machine.status.toLowerCase()}`}>{machine.status}</span></div><div className="machine-stats"><span>Batches <b>{machine.total_batches.toLocaleString()}</b></span><span>Defects <b>{machine.defect_count.toLocaleString()}</b></span><span>Defect rate <b>{machine.defect_rate.toFixed(1)}%</b></span></div></motion.article>)}</div>
}

function CommandCenter({ telemetry }) {
  const isLoading = telemetry.status === 'loading'
  const data = telemetry.data
  return <motion.div className="page-content" key="Command Center" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} transition={{ duration: .22 }}>
    <section className="welcome-row"><div><div className="eyebrow"><span className="eyebrow-line" />{telemetry.status === 'connected' ? 'API CONNECTED' : telemetry.status === 'offline' ? 'API OFFLINE' : 'CONNECTING TO API'}</div><h1>AI Quality Intelligence</h1><p className="page-description">CELLGUARD command center · Synthetic factory telemetry</p></div></section>
    {isLoading ? <LoadingMetrics /> : data ? <section className="metric-grid" aria-label="CELLGUARD telemetry summary">{metricDefinitions.map((metric, index) => <MetricCard key={metric.key} metric={metric} value={metric.format(data[metric.key])} index={index} />)}</section> : <section className="telemetry-error glass-card" role="alert"><div className="error-heading"><span className="status-marker" /><h2>Telemetry unavailable</h2></div><p>API OFFLINE. The CSV summary could not be loaded, so no live values are shown.</p><span className="error-detail">{telemetry.error}</span></section>}
    <section className="main-grid command-main-grid"><article className="panel glass-card"><div className="panel-heading"><div><div className="panel-kicker">WORKSTATION TELEMETRY</div><h2>Machine summary</h2></div>{data && <span className="baseline-badge"><i className="online-dot" />{data.active_workstations} active</span>}</div>{isLoading ? <div className="machine-loading">Loading machine summaries from the factory CSV...</div> : data ? <MachineCards machines={data.machines} /> : <div className="machine-loading">Machine data will appear when the API connection is restored.</div>}</article>
      <article className="panel glass-card source-panel"><div className="panel-kicker">DATA SOURCE</div><h2>Synthetic factory telemetry</h2><p>{data ? `${data.record_count.toLocaleString()} CSV records summarized from the local factory dataset.` : 'Values are read from the local factory CSV through the CELLGUARD API.'}</p><div className={`source-status ${telemetry.status === 'connected' ? 'connected' : ''}`}><span className={telemetry.status === 'connected' ? 'online-dot' : 'status-marker'} />{telemetry.status === 'connected' ? 'API CONNECTED' : telemetry.status === 'offline' ? 'API OFFLINE' : 'CONNECTING TO API'}</div></article>
    </section>
    <footer className="page-footer"><span>{data ? `${data.record_count.toLocaleString()} records from factory_process_data.csv` : 'No telemetry values are presented until the API responds'}</span><span>Data source: Synthetic factory telemetry</span></footer>
  </motion.div>
}

function App() {
  const [activePage, setActivePage] = useState('Command Center')
  const [menuOpen, setMenuOpen] = useState(false)
  const [telemetry, setTelemetry] = useState({ status: 'loading', data: null, error: null })

  useEffect(() => {
    const controller = new AbortController()
    fetchTelemetrySummary({ signal: controller.signal })
      .then((data) => setTelemetry({ status: 'connected', data, error: null }))
      .catch((error) => {
        if (error.name !== 'AbortError') {
          setTelemetry({ status: 'offline', data: null, error: error.message })
        }
      })
    return () => controller.abort()
  }, [])

  return <div className="app-shell"><Sidebar activePage={activePage} setActivePage={setActivePage} open={menuOpen} onClose={() => setMenuOpen(false)} apiStatus={telemetry.status} /><main className="main-area"><Header activePage={activePage} onMenu={() => setMenuOpen(true)} apiStatus={telemetry.status} /><div className="content-scroll"><AnimatePresence mode="wait">{activePage === 'Command Center' ? <CommandCenter key="Command Center" telemetry={telemetry} /> : <PlaceholderPage page={activePage} key={activePage} />}</AnimatePresence></div></main></div>
}

export default App
