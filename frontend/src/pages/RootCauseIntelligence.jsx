import { useState } from 'react'
import { Activity, AlertTriangle, CheckCircle2, CircleHelp, Gauge, LoaderCircle, Thermometer, Timer, Zap } from 'lucide-react'
import { motion } from 'framer-motion'
import { analyzeRootCause } from '../api/rootCause'

const initialParameters = {
  current: '190',
  voltage: '24.5',
  temperature: '85',
  pressure: '4.5',
  welding_time: '3.2',
  speed: '12',
}

const parameterFields = [
  { key: 'current', label: 'Welding current', icon: Zap },
  { key: 'voltage', label: 'Welding voltage', icon: Activity },
  { key: 'temperature', label: 'Temperature', icon: Thermometer },
  { key: 'pressure', label: 'Welding pressure', icon: Gauge },
  { key: 'welding_time', label: 'Welding time', icon: Timer },
  { key: 'speed', label: 'Welding speed', icon: Activity },
]

const classLabels = {
  Burn_Through: 'Burn Through',
  Incomplete_Weld: 'Incomplete Weld',
}

function displayClass(value) {
  return classLabels[value] ?? value?.replaceAll('_', ' ')
}

function ParameterForm({ values, onChange, onSubmit, loading }) {
  return <form className="panel glass-card root-cause-form" onSubmit={onSubmit}>
    <div className="panel-heading"><div><div className="panel-kicker">PROCESS INPUT</div><h2>Weld parameters</h2></div><span className="parameter-count">06 PARAMETERS</span></div>
    <p className="root-cause-form-intro">Enter process readings for the batch under review. All six values are required.</p>
    <div className="parameter-grid">{parameterFields.map(({ key, label, icon: Icon }) => <label className="parameter-field" key={key}><span className="parameter-label"><Icon size={17} />{label}</span><input type="number" min="0" step="any" required value={values[key]} onChange={(event) => onChange(key, event.target.value)} aria-label={label} /></label>)}</div>
    <button type="submit" className="root-cause-submit" disabled={loading}>{loading ? <><LoaderCircle className="root-cause-spinner" size={19} /> Analyzing process…</> : <><Activity size={19} /> Analyze Process</>}</button>
    <p className="root-cause-form-note">The analysis uses the trained CELLGUARD classifier and its configured process baselines.</p>
  </form>
}

function EvidencePanel({ evidence }) {
  return <section className="panel glass-card root-cause-evidence"><div className="panel-heading"><div><div className="panel-kicker">PROCESS EVIDENCE</div><h2>Baseline deviations</h2></div><span className="evidence-count">{evidence.length} {evidence.length === 1 ? 'signal' : 'signals'}</span></div>
    {evidence.length ? <div className="evidence-list">{evidence.map((item, index) => <article className="evidence-item" key={`${item.parameter}-${index}`}><span className="evidence-marker"><AlertTriangle size={17} /></span><div className="evidence-copy"><strong>{item.description}</strong><span>{item.parameter.replaceAll('_', ' ')} · observed <b>{Number(item.value).toFixed(2)}</b> · baseline <b>{Number(item.baseline).toFixed(2)}</b></span></div></article>)}</div> : <div className="no-evidence"><CheckCircle2 size={20} /><span>No mapped parameter deviations were detected against the configured baseline.</span></div>}
  </section>
}

function AnalysisResult({ result }) {
  const confidence = Number(result.confidence)
  const hasConfidence = Number.isFinite(confidence) && confidence >= 0 && confidence <= 1
  const evidence = Array.isArray(result.evidence) ? result.evidence : []
  return <div className="root-cause-result-stack">
    <article className="panel glass-card root-cause-result"><div className="panel-kicker">MOST LIKELY DEFECT PATTERN</div><div className="result-class-row"><span className="root-cause-class-icon"><CircleHelp size={24} /></span><h2>{displayClass(result.predicted_cause)}</h2></div>
      {hasConfidence && <div className="confidence-block"><div className="confidence-label"><span>Model confidence</span><strong>{(confidence * 100).toFixed(1)}%</strong></div><div className="root-confidence-track"><span style={{ width: `${confidence * 100}%` }} /></div><small>Maximum class probability returned by the existing model.</small></div>}
      <div className="explanation-block"><div className="panel-kicker">MODEL EXPLANATION</div><p>{result.explanation}</p></div>
      <div className="root-cause-disclaimer"><AlertTriangle size={16} /><span>Predicted defect pattern and contributing signals are estimates, not proof of physical cause.</span></div>
    </article>
    <EvidencePanel evidence={evidence} />
  </div>
}

export default function RootCauseIntelligence() {
  const [values, setValues] = useState(initialParameters)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function updateValue(key, value) {
    setValues((previous) => ({ ...previous, [key]: value }))
  }

  async function submitAnalysis(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const processParameters = Object.fromEntries(Object.entries(values).map(([key, value]) => [key, Number(value)]))
      setResult(await analyzeRootCause(processParameters))
    } catch (requestError) {
      setError(requestError.message || 'Root-cause analysis could not be completed.')
    } finally {
      setLoading(false)
    }
  }

  return <motion.div className="page-content root-cause-page" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} transition={{ duration: .22 }}>
    <section className="welcome-row root-cause-welcome"><div><div className="eyebrow"><span className="eyebrow-line" />PROCESS DIAGNOSTICS · EXPLAIN</div><h1>Root Cause Intelligence</h1><p className="page-description">Relate welding process conditions to the most likely defect pattern.</p></div><div className="root-cause-status"><span className="online-dot" /> MODEL READY</div></section>
    <section className="root-cause-layout"><ParameterForm values={values} onChange={updateValue} onSubmit={submitAnalysis} loading={loading} />
      <div className="root-cause-output" aria-live="polite">
        {loading && <article className="panel glass-card root-cause-state"><span className="root-state-icon"><LoaderCircle className="root-cause-spinner" size={25} /></span><h2>Analyzing process data</h2><p>Comparing the entered conditions with learned defect patterns and configured baselines.</p><div className="root-loading-line"><span /></div></article>}
        {!loading && error && <article className="panel glass-card root-cause-state root-cause-error" role="alert"><span className="root-state-icon"><AlertTriangle size={24} /></span><h2>Analysis unavailable</h2><p>{error}</p></article>}
        {!loading && !error && !result && <article className="panel glass-card root-cause-state"><span className="root-state-icon"><CircleHelp size={25} /></span><h2>Analysis results</h2><p>Submit six process readings to see the predicted defect pattern and any baseline deviations.</p></article>}
        {!loading && !error && result && <AnalysisResult result={result} />}
      </div>
    </section>
  </motion.div>
}
