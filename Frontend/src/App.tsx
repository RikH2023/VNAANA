import { LoginPage } from './components/LoginPage/LoginPage'
import { MobileTabBar, MobileTopBar } from './components/Navigation/MobileBars'
import { Sidebar } from './components/Navigation/Sidebar'
import { briefingMeta, sampleStories, sampleUser } from './data/sampleStories'
import { useHash } from './hooks/useHash'
import { readStorage, writeStorage } from './utils/storage'
import styles from './App.module.css'

// Session storage: the briefing comes back in a new browser session, like a new morning notification.
const BRIEFING_STORAGE_KEY = 'vnaana.briefingDismissed'

// Temporarily focus this branch on authentication
export default function App() {
  return <LoginPage />
}
