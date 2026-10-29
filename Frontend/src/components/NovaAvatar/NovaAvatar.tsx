import { Smile } from 'lucide-react'
import styles from './NovaAvatar.module.css'

/* Nova, the virtual news anchor: an accent circle with a simple face. */
export function NovaAvatar({ size = 52 }: { size?: number }) {
  return (
    <span className={styles.avatar} style={{ width: size, height: size }} aria-hidden="true">
      <Smile size={Math.round(size * 0.55)} strokeWidth={2} />
    </span>
  )
}
