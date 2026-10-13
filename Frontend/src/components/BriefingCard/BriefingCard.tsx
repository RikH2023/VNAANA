import { X } from 'lucide-react'
import { Segments } from '../FeedPost/CarouselControls'
import { NovaAvatar } from '../NovaAvatar/NovaAvatar'
import styles from './BriefingCard.module.css'

type Props = {
  firstName: string
  forYouCount: number
  dontMissCount: number
  openedCount: number
  readTime: string
  updatedAt: string
  onDismiss: () => void
}

function plural(count: number, one: string, many: string) {
  return `${count} ${count === 1 ? one : many}`
}

/* Nova's greeting at the top of the feed, with a progress bar for today's stories. Can be dismissed. */
export function BriefingCard({ firstName, forYouCount, dontMissCount, openedCount, readTime, updatedAt, onDismiss }: Props) {
  const total = forYouCount + dontMissCount
  // White segments = stories opened + the one you're on now
  const filled = Math.min(openedCount + 1, total)

  return (
    <section className={styles.card} aria-labelledby="briefing-greeting">
      <NovaAvatar size={52} />
      <div className={styles.content}>
        <p className={styles.label}>Nova · your news anchor</p>
        <h1 id="briefing-greeting" className={styles.greeting}>
          Morning, {firstName}. {plural(forYouCount, 'story', 'stories')} picked for you, plus{' '}
          {dontMissCount} you shouldn’t miss.
        </h1>
        <div className={styles.progressRow}>
          <Segments total={total} filled={filled} className={styles.segments} />
          <p className={styles.meta}>
            <span className="sr-only">
              {openedCount} of {total} stories opened.{' '}
            </span>
            {readTime} · updated {updatedAt}
          </p>
        </div>
      </div>
      <button type="button" className={styles.dismiss} onClick={onDismiss} aria-label="Dismiss Nova’s briefing">
        <X size={20} aria-hidden="true" />
      </button>
    </section>
  )
}
