import { Compass, LayoutGrid, Sparkles, User } from 'lucide-react'
import { Logo } from './Logo'
import { SearchField } from './SearchField'
import styles from './Navigation.module.css'

/* Top bar for screens under 820px: logo + search. */
export function MobileTopBar() {
  return (
    <header className={styles.topBar}>
      <Logo />
      <SearchField id="mobile-search" />
    </header>
  )
}

const TABS = [
  { label: 'For You', href: '/', Icon: Sparkles, current: true },
  { label: 'Explore', href: '#explore', Icon: Compass },
  { label: 'Topics', href: '#topics', Icon: LayoutGrid },
  { label: 'Profile', href: '#profile', Icon: User },
]

/* Bottom tab bar for screens under 820px. */
export function MobileTabBar() {
  return (
    <nav className={styles.tabBar} aria-label="Main">
      <ul>
        {TABS.map(({ label, href, Icon, current }) => (
          <li key={label}>
            <a href={href} className={styles.tab} aria-current={current ? 'page' : undefined}>
              <Icon size={22} aria-hidden="true" />
              {label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  )
}
