import { Activity } from 'lucide-react'
import { motion } from 'framer-motion'
import { navigation } from '../data/navigation'

export default function PlaceholderPage({ page }) {
  const item = navigation.find((entry) => entry.label === page)
  const Icon = item?.icon ?? Activity
  return <motion.div className="placeholder-page glass-card" key={page} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} transition={{ duration: .22 }}><div className="placeholder-icon"><Icon size={24} /></div><div className="panel-kicker">LOCAL DEMO · API NOT CONNECTED</div><h1>{page}</h1><p>This section is a frontend placeholder. No CELLGUARD service data is connected.</p><span className="coming-soon">Frontend foundation</span></motion.div>
}
