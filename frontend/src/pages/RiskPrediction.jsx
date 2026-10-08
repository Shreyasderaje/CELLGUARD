import { useState } from 'react'
import { Activity, AlertTriangle, Gauge, LoaderCircle, ShieldAlert, Thermometer, Timer, Zap } from 'lucide-react'
import { motion } from 'framer-motion'
import { predictRisk } from '../api/risk'

const initialParameters = {
  current: '230',
  voltage: '27',
  temperature: '120',
  pressure: '4.2',
  welding_time: '2.8',
  speed: '12',
}

const parameterFields = [
  { key: 'current', label: 'Current', unit: 'A', icon: Zap },
  { key: 'voltage', label: 'Voltage', unit: 'V', icon: Activity },
  { key: 'temperature', label: 'Temperature', unit: '°C', icon: Thermometer },
  { key: 'pressure', label: 'Pressure', unit: 'bar', icon: Gauge },
  { key: 'welding_time', label: 'Welding time', unit: 's', icon: Timer },
  { key: 'speed', label: 'Speed', unit: 'mm/s', icon: Activity },
]

const riskStyles = {
  LOW: { color: '#48d4a3', border: '#32836666', background: '#18382f66' },
  MEDIUM: { color: '#e9b66e', border: '#9b744466', background: '#392f2366' },
  HIGH: { color: '#ee9292', border: '#9b474766', background: '#3b252966' },
}

function RiskInputForm({ values, onChange, onSubmit, loading }) {
  return <form className="panel glass-card root-cause-form" onSubmit={onSubmit}>
    <div className="panel-heading"><div><div className="panel-kicker">PROCESS INPUT</div><h2>Welding parameters</h2></div><span className="parameter-count">06 PARAMETERS</span></div>
    <p className="root-cause-form-intro">Enter process readings to estimate the batch defect risk. Values must be zero or greater.</p>
    <div className="parameter-grid">{parameterFields.map(({ key, label, unit, icon: Icon }) => <label className="parameter-field" key={key}><span className="parameter-label"><Icon size={17} />{label} <span>({unit})</span></span><input type="number" min="0" step="any" required value={values[key]} onChange={(event) => onChange(key, event.target.value)} aria-label={`${label} (${unit})`} /></label>)}</div>
    <button type="submit" className="root-cause-submit" disabled={loading}>{loading ? <><LoaderCircle className="root-cause-spinner" size={19} /> Analyzing risk…</> : <><ShieldAlert size={19} /> Analyze Risk</>}</button>
    <p className="root-cause-form-note">Estimated probability from the existing trained Random Forest model.</p>
  </form>
}

function RiskResult({ result }) {
  const level = String(result.risk_level ?? 'UNKNOWN').toUpperCase()
  const style = riskStyles[level] ?? { color: '#aabaca', border: '#53657966', background: '#172536' }
  const probability = Number(result.risk_probability)
  const contributors = Array.isArray(result.contributors) ? result.contributors : []

  return <div className="root-cause-result-stack">
    <article className="panel glass-card root-cause-result" style={{ borderColor: style.border }}>
      <div className="panel-kicker">DEFECT RISK ASSESSMENT</div>
      <div className="result-class-row"><span className="root-cause-class-icon" style={{ color: style.color, borderColor: style.border }}><ShieldAlert size={24} /></span><div><div className="risk-score" style={{ color: style.color, font: '800 clamp(30px, 4vw, 42px)/1.1 Manrope, sans-serif', letterSpacing: '-1px' }}>{Number.isFinite(probability) ? `${probability.toFixed(2)}%` : 'Unavailable'}</div><span className="risk-level-badge" style={{ display: 'inline-block', marginTop: 8, padding: '5px 8px', border: `1px solid ${style.border}`, borderRadius: 6, color: style.color, background: style.background, fontSize: 11, fontWeight: 700, letterSpacing: '.6px' }}>{level} RISK</span></div></div>
      <div className="root-confidence-track"><span style={{ width: `${Number.isFinite(probability) ? Math.max(0, Math.min(probability, 100)) : 0}%`, background: style.color }} /></div>
      <p className="root-cause-form-note">Estimated defect probability from the trained model.</p>
    </article>
    <section className="panel glass-card root-cause-evidence"><div className="panel-heading"><div><div className="panel-kicker">TOP MODEL FEATURES</div><h2>Global feature importance</h2></div><span className="evidence-count">{contributors.length} contributors</span></div>
      {contributors.length ? <div className="evidence-list">{contributors.map((item, index) => <article className="evidence-item" key={`${item.parameter}-${index}`}><span className="evidence-marker"><Activity size={17} /></span><div className="evidence-copy"><strong>{item.parameter.replaceAll('_', ' ')}</strong><span>Importance <b>{Number(item.importance).toFixed(3)}</b> · submitted value <b>{Number(item.value).toFixed(2)}</b></span></div></article>)}</div> : <p className="root-cause-form-note">No contributor data was returned by the model.</p>}
      <div className="root-cause-disclaimer"><AlertTriangle size={16} /><span>Contributor rankings show global model feature importance. They are not case-specific causal explanations and do not indicate whether a feature raises or lowers risk.</span></div>
    </section>
  </div>
}

export default function RiskPrediction() {
  const [values, setValues] = useState(initialParameters)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function updateValue(key, value) {
    setValues((previous) => ({ ...previous, [key]: value }))
  }

  async function submitAnalysis(event) {
    event.preventDefault()
    const processParameters = Object.fromEntries(Object.entries(values).map(([key, value]) => [key, Number(value)]))
    const invalidField = Object.entries(processParameters).find(([, value]) => !Number.isFinite(value) || value < 0)
    if (invalidField) {
      const label = parameterFields.find(({ key }) => key === invalidField[0])?.label ?? invalidField[0]
      setError(`${label} must be a finite number greater than or equal to zero.`)
      setResult(null)
      return
    }

    setLoading(true)
    setError('')
    setResult(null)
    try {
      setResult(await predictRisk(processParameters))
    } catch (requestError) {
      setError(requestError.message || 'Risk prediction could not be completed.')
    } finally {
      setLoading(false)
    }
  }

  return <motion.div className="page-content root-cause-page" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} transition={{ duration: .22 }}>
    <section className="welcome-row root-cause-welcome"><div><div className="eyebrow"><span className="eyebrow-line" />PROCESS DIAGNOSTICS · PREDICT</div><h1>Risk Prediction</h1><p className="page-description">Estimate defect probability from current welding process conditions.</p></div><div className="root-cause-status"><span className="online-dot" /> MODEL READY</div></section>
    <section className="root-cause-layout"><RiskInputForm values={values} onChange={updateValue} onSubmit={submitAnalysis} loading={loading} />
      <div className="root-cause-output" aria-live="polite">
        {loading && <article className="panel glass-card root-cause-state"><span className="root-state-icon"><LoaderCircle className="root-cause-spinner" size={25} /></span><h2>Calculating defect risk</h2><p>Running the entered process conditions through the existing risk model.</p><div className="root-loading-line"><span /></div></article>}
        {!loading && error && <article className="panel glass-card root-cause-state root-cause-error" role="alert"><span className="root-state-icon"><AlertTriangle size={24} /></span><h2>Risk prediction unavailable</h2><p>{error}</p></article>}
        {!loading && !error && !result && <article className="panel glass-card root-cause-state"><span className="root-state-icon"><Gauge size={25} /></span><h2>Risk assessment</h2><p>Submit six process readings to see the estimated defect probability and model feature rankings.</p></article>}
        {!loading && !error && result && <RiskResult result={result} />}
      </div>
    </section>
  </motion.div>
}
