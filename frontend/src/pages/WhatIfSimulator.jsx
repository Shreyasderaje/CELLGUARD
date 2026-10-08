import { useEffect, useRef, useState } from 'react'
import { Activity, AlertTriangle, ArrowDownRight, ArrowUpRight, Gauge, LoaderCircle, RotateCcw, ShieldAlert, Thermometer, Timer, Zap } from 'lucide-react'
import { motion } from 'framer-motion'
import { predictRisk } from '../api/risk'

const initialBaseline = {
  current: '230',
  voltage: '27',
  temperature: '120',
  pressure: '4.2',
  welding_time: '2.8',
  speed: '12',
}

const parameterFields = [
  { key: 'current', label: 'Current', unit: 'A', step: '1', icon: Zap },
  { key: 'voltage', label: 'Voltage', unit: 'V', step: '0.5', icon: Activity },
  { key: 'temperature', label: 'Temperature', unit: '°C', step: '1', icon: Thermometer },
  { key: 'pressure', label: 'Pressure', unit: 'bar', step: '0.1', icon: Gauge },
  { key: 'welding_time', label: 'Welding time', unit: 's', step: '0.1', icon: Timer },
  { key: 'speed', label: 'Speed', unit: 'mm/s', step: '0.5', icon: Activity },
]

const levelStyles = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
}

function toNumericParameters(values, scenarioName) {
  const parameters = {}
  for (const { key, label } of parameterFields) {
    const value = values[key]
    const numericValue = Number(value)
    if (String(value).trim() === '' || !Number.isFinite(numericValue) || numericValue < 0) {
      throw new Error(`${scenarioName}: ${label} must be a finite number greater than or equal to zero.`)
    }
    parameters[key] = numericValue
  }
  return parameters
}

function displayValue(value) {
  if (String(value).trim() === '' || !Number.isFinite(Number(value))) return '—'
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function RiskResultCard({ title, result, tone }) {
  const level = String(result.risk_level ?? 'UNKNOWN').toUpperCase()
  const levelClass = levelStyles[level] ?? 'unknown'
  const probability = Number(result.risk_probability)
  return <article className={`panel glass-card whatif-result-card ${tone}`}>
    <div className="panel-kicker">{title}</div>
    <div className="whatif-result-score">{Number.isFinite(probability) ? `${probability.toFixed(2)}%` : 'Unavailable'}</div>
    <span className={`whatif-risk-level ${levelClass}`}>{level} RISK</span>
    <div className="whatif-risk-track" aria-hidden="true"><span className={levelClass} style={{ width: `${Number.isFinite(probability) ? Math.max(0, Math.min(probability, 100)) : 0}%` }} /></div>
    <p>Model-estimated defect probability</p>
  </article>
}

function ParameterDifference({ baseline, proposed }) {
  return <section className="panel glass-card whatif-difference-panel">
    <div className="panel-heading"><div><div className="panel-kicker">SCENARIO DELTA</div><h2>Parameter changes</h2></div><span className="whatif-difference-note">Proposed compared with baseline</span></div>
    <div className="whatif-difference-list">
      {parameterFields.map(({ key, label, unit }) => {
        const before = Number(baseline[key])
        const after = Number(proposed[key])
        const valid = String(baseline[key]).trim() !== '' && String(proposed[key]).trim() !== '' && Number.isFinite(before) && Number.isFinite(after)
        const difference = valid ? after - before : Number.NaN
        const changed = valid && difference !== 0
        return <div className="whatif-difference-row" key={key}>
          <strong>{label}</strong>
          <span><small>Baseline</small><b>{displayValue(baseline[key])} {unit}</b></span>
          <span><small>Proposed</small><b>{displayValue(proposed[key])} {unit}</b></span>
          <span className={`whatif-delta-value ${changed ? 'changed' : ''}`}><small>Change</small><b>{Number.isFinite(difference) ? `${difference > 0 ? '+' : ''}${difference.toFixed(2)} ${unit}` : '—'}</b></span>
        </div>
      })}
    </div>
  </section>
}

export default function WhatIfSimulator() {
  const [baseline, setBaseline] = useState({ ...initialBaseline })
  const [proposed, setProposed] = useState({ ...initialBaseline })
  const [comparison, setComparison] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const requestRef = useRef(null)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
      requestRef.current?.abort()
    }
  }, [])

  function updateParameter(setScenario, key, value) {
    setScenario((current) => ({ ...current, [key]: value }))
    setComparison(null)
    setError('')
  }

  function resetProposed() {
    if (loading) return
    setProposed({ ...baseline })
    setComparison(null)
    setError('')
  }

  async function simulate(event) {
    event.preventDefault()
    if (requestRef.current) return

    let baselineParameters
    let proposedParameters
    try {
      baselineParameters = toNumericParameters({ ...baseline }, 'Baseline')
      proposedParameters = toNumericParameters({ ...proposed }, 'Proposed scenario')
    } catch (validationError) {
      setError(validationError.message)
      setComparison(null)
      return
    }

    const controller = new AbortController()
    requestRef.current = controller
    setLoading(true)
    setError('')
    setComparison(null)
    try {
      const predictions = await Promise.allSettled([
        predictRisk(baselineParameters, { signal: controller.signal }),
        predictRisk(proposedParameters, { signal: controller.signal }),
      ])
      const failedPrediction = predictions.find((prediction) => prediction.status === 'rejected')
      if (failedPrediction) throw failedPrediction.reason
      const [baselinePrediction, proposedPrediction] = predictions
      if (mountedRef.current) {
        setComparison({ baselineResult: baselinePrediction.value, proposedResult: proposedPrediction.value, baselineParameters, proposedParameters })
      }
    } catch (requestError) {
      if (mountedRef.current && requestError.name !== 'AbortError') {
        setError(requestError.message || 'The risk comparison could not be completed.')
      }
    } finally {
      if (requestRef.current === controller) {
        requestRef.current = null
        if (mountedRef.current) setLoading(false)
      }
    }
  }

  const riskChange = comparison
    ? Number(comparison.proposedResult.risk_probability) - Number(comparison.baselineResult.risk_probability)
    : null
  const direction = riskChange === null || !Number.isFinite(riskChange) ? 'same' : riskChange > 0 ? 'increased' : riskChange < 0 ? 'decreased' : 'same'
  const DirectionIcon = direction === 'increased' ? ArrowUpRight : direction === 'decreased' ? ArrowDownRight : ShieldAlert

  return <motion.div className="page-content whatif-page" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .2 }}>
    <section className="welcome-row whatif-welcome"><div><div className="eyebrow"><span className="eyebrow-line" />PROCESS DIAGNOSTICS · SIMULATE</div><h1>What-If Simulator</h1><p className="page-description">Compare model-estimated defect risk for baseline and proposed welding conditions.</p></div></section>

    <div className="whatif-disclaimer"><AlertTriangle size={19} /><div><strong>Decision support simulation only</strong><p>This is a model-based simulation, not a physical manufacturing control. Predictions are estimates and do not guarantee defect prevention. Parameter values are not validated manufacturing recommendations. Feature importance is global and must not be treated as case-specific causality.</p></div></div>

    <form onSubmit={simulate}>
      <div className="whatif-scenarios">
        <section className="panel glass-card whatif-scenario-panel">
          <div className="whatif-scenario-heading"><span className="whatif-scenario-icon baseline"><Gauge size={19} /></span><div><div className="panel-kicker">REFERENCE CONDITIONS</div><h2>Baseline scenario</h2></div><span className="whatif-tag baseline-tag">BASELINE</span></div>
          <p className="whatif-panel-description">The comparison reference. Values are held fixed while the two predictions run.</p>
          <div className="whatif-parameter-grid">{parameterFields.map(({ key, label, unit, step, icon: Icon }) => <label className="parameter-field" key={key}><span className="parameter-label"><Icon size={16} />{label} <small>({unit})</small></span><input type="number" min="0" step={step} required value={baseline[key]} disabled={loading} onChange={(event) => updateParameter(setBaseline, key, event.target.value)} aria-label={`Baseline ${label} (${unit})`} /></label>)}</div>
        </section>

        <section className="panel glass-card whatif-scenario-panel proposed-panel">
          <div className="whatif-scenario-heading"><span className="whatif-scenario-icon proposed"><Activity size={19} /></span><div><div className="panel-kicker">TEST CONDITIONS</div><h2>Proposed scenario</h2></div><span className="whatif-tag proposed-tag">PROPOSED</span></div>
          <p className="whatif-panel-description">Adjust one or more values to compare their model-estimated risk score with the baseline.</p>
          <div className="whatif-parameter-grid">{parameterFields.map(({ key, label, unit, step, icon: Icon }) => <label className="parameter-field" key={key}><span className="parameter-label"><Icon size={16} />{label} <small>({unit})</small></span><input type="number" min="0" step={step} required value={proposed[key]} disabled={loading} onChange={(event) => updateParameter(setProposed, key, event.target.value)} aria-label={`Proposed ${label} (${unit})`} /></label>)}</div>
          <button className="whatif-reset-button" type="button" disabled={loading} onClick={resetProposed}><RotateCcw size={15} />Reset proposed values to baseline</button>
        </section>
      </div>

      <button className="root-cause-submit whatif-submit" type="submit" disabled={loading}>{loading ? <><LoaderCircle className="whatif-spinner" size={19} />Comparing both scenarios…</> : <><Activity size={19} />Simulate Comparison</>}</button>
    </form>

    {error && <section className="panel glass-card whatif-state error-state" role="alert"><span className="whatif-state-icon"><AlertTriangle size={22} /></span><div><strong>Comparison unavailable</strong><p>{error}</p></div></section>}
    {loading && <section className="panel glass-card whatif-state loading-state" role="status"><span className="whatif-state-icon"><LoaderCircle className="whatif-spinner" size={22} /></span><div><strong>Running two model predictions</strong><p>Comparing the same trained risk model with the submitted baseline and proposed values.</p></div></section>}

    {comparison && !loading && <section className="whatif-results" aria-live="polite">
      <div className="whatif-results-heading"><div><div className="panel-kicker">MODEL OUTPUTS</div><h2>Scenario risk comparison</h2></div><span>Calculated from both API responses</span></div>
      <div className="whatif-result-grid"><RiskResultCard title="Baseline estimated risk" result={comparison.baselineResult} tone="baseline-result" /><RiskResultCard title="Proposed estimated risk" result={comparison.proposedResult} tone="proposed-result" /></div>
      <article className={`panel glass-card whatif-change-card ${direction}`}>
        <span className="whatif-change-icon"><DirectionIcon size={23} /></span><div className="whatif-change-copy"><span>PROPOSED − BASELINE</span><strong>{Number.isFinite(riskChange) ? `${riskChange > 0 ? '+' : ''}${riskChange.toFixed(2)} percentage points` : 'Change unavailable'}</strong><small>Model-estimated risk {direction}.</small></div>
      </article>
      <ParameterDifference baseline={baseline} proposed={proposed} />
      <p className="whatif-result-note">The comparison reflects model outputs only. It does not establish that a parameter change caused the score difference or that the proposed settings are safe or effective in production.</p>
    </section>}
    {!comparison && !loading && !error && <section className="panel glass-card whatif-state initial-state" role="status"><span className="whatif-state-icon"><Gauge size={22} /></span><div><strong>Ready to simulate</strong><p>Review both parameter sets, then run the comparison to request actual baseline and proposed risk estimates.</p></div></section>}
  </motion.div>
}
