import { Anchor } from 'lucide-react'
import styles from './Navigation.module.css'

export function Logo() {
  return (
    <a href="/" className={styles.logo} aria-label="Virtual News Anchor – home">
      <span className={styles.logoMark} aria-hidden="true">
        <Anchor size={20} strokeWidth={2.4} />
      </span>
      <span className={styles.wordmark} aria-hidden="true">
        Virtual News
        <br />
        Anchor
      </span>
    </a>
  )
}
