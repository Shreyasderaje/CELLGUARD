import { Menu } from 'lucide-react'

export default function Header({ activePage, onMenu, apiStatus }) {
  const statusLabel = apiStatus === 'connected' ? 'API CONNECTED' : apiStatus === 'offline' ? 'API OFFLINE' : 'CONNECTING TO API'
  return <header className="topbar"><button className="icon-button mobile-menu" onClick={onMenu} aria-label="Open navigation"><Menu size={20} /></button><div className="breadcrumbs"><span>CELLGUARD</span><span className="crumb-separator">/</span><strong>{activePage}</strong></div><div className="topbar-actions"><span className={`connection-status ${apiStatus}`}><b>LOCAL DEMO</b><span aria-hidden="true">·</span>{statusLabel}</span></div></header>
}
