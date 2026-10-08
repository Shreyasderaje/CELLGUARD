import { CircleHelp, X } from 'lucide-react'
import { navigation } from '../data/navigation'

export default function Sidebar({ activePage, setActivePage, open, onClose, apiStatus }) {
  const sections = [...new Set(navigation.map((item) => item.section))]
  const statusLabel = apiStatus === 'connected' ? 'API connected' : apiStatus === 'offline' ? 'API offline' : 'Connecting to API'
  return <>
    {open && <button className="mobile-scrim" aria-label="Close navigation" onClick={onClose} />}
    <aside className={`sidebar ${open ? 'sidebar-open' : ''}`}>
      <div className="brand-lockup"><div className="brand-mark"><span /><span /><span /></div><div><strong>CELLGUARD</strong><small>AI QUALITY INTELLIGENCE</small></div><button className="icon-button sidebar-close" onClick={onClose} aria-label="Close menu"><X size={18} /></button></div>
      <div className="workspace-select"><div className="workspace-icon">CG</div><div><strong>LOCAL DEMO</strong><small>{statusLabel.toUpperCase()}</small></div></div>
      <nav className="side-nav" aria-label="Main navigation">{sections.map((section) => <div className="nav-section" key={section}><span className="nav-section-title">{section}</span>{navigation.filter((item) => item.section === section).map(({ label, icon: Icon }) => <button key={label} className={`nav-item ${activePage === label ? 'active' : ''}`} onClick={() => { setActivePage(label); onClose() }}><Icon size={19} strokeWidth={1.8} /><span>{label}</span></button>)}</div>)}</nav>
      <div className="sidebar-bottom"><div className="system-card"><div className="system-card-head"><span className={apiStatus === 'connected' ? 'online-dot' : 'status-marker'} />{statusLabel}</div><div className="system-card-copy">Synthetic factory telemetry</div></div><button className="help-link"><CircleHelp size={17} />Help & documentation</button></div>
    </aside>
  </>
}
