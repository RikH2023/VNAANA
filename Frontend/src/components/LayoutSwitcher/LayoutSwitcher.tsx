import { POST_LAYOUTS } from '../FeedPost/layouts'
import type { PostLayoutKey } from '../FeedPost/layouts'
import styles from './LayoutSwitcher.module.css'

type Props = {
  value: PostLayoutKey
  onChange: (layout: PostLayoutKey) => void
}

/* Segmented control that switches every post in the feed to another layout. */
export function LayoutSwitcher({ value, onChange }: Props) {
  const keys = Object.keys(POST_LAYOUTS) as PostLayoutKey[]
  return (
    <fieldset className={styles.switcher}>
      <legend className={styles.legend}>Post layout</legend>
      <div className={styles.options}>
        {keys.map((key) => (
          <label key={key} className={styles.option}>
            <input
              type="radio"
              name="post-layout"
              className="sr-only"
              value={key}
              checked={value === key}
              onChange={() => onChange(key)}
            />
            <span className={styles.label}>{POST_LAYOUTS[key].label}</span>
          </label>
        ))}
      </div>
    </fieldset>
  )
}
