import { BadgeCheck, Ellipsis, MapPin } from 'lucide-react'
import { TOPIC_ICONS } from '../../data/topics'
import { usePost } from './PostContext'
import styles from './PostHeader.module.css'

/*
 * Small pieces that describe a post (who, when, what, where).
 * The Original layout uses the full <PostHeader>; other layouts
 * combine the pieces in their own way.
 */

export function PublisherAvatar({ size = 40 }: { size?: number }) {
  const { story } = usePost()
  return (
    <span className={styles.avatar} style={{ width: size, height: size }} aria-hidden="true">
      {story.publisher.initials}
    </span>
  )
}

export function PublisherName() {
  const { story } = usePost()
  return (
    <span className={styles.publisher}>
      {story.publisher.name}
      {story.publisher.verified && (
        <span className={styles.verified} role="img" aria-label="Verified publisher">
          <BadgeCheck size={16} aria-hidden="true" />
        </span>
      )}
    </span>
  )
}

/* Avatar + publisher + "By author · time" in one compact block. */
export function Byline({ showTime = true, onDark = false }: { showTime?: boolean; onDark?: boolean }) {
  const { story } = usePost()
  return (
    <div className={`${styles.byline} ${onDark ? styles.onDark : ''}`}>
      <PublisherAvatar />
      <div className={styles.who}>
        <PublisherName />
        <span className={styles.meta}>
          By {story.author}
          {showTime && ` · ${story.publishedAgo}`}
        </span>
      </div>
    </div>
  )
}

export function TagPill() {
  const { story } = usePost()
  const forYou = story.feedReason === 'forYou'
  return (
    <span className={`${styles.tag} ${forYou ? styles.forYou : styles.dontMiss}`}>
      {forYou ? 'For you' : 'Don’t miss'}
    </span>
  )
}

export function TopicPill() {
  const { story } = usePost()
  const Icon = TOPIC_ICONS[story.topic]
  return (
    <span className={styles.pill}>
      <Icon size={14} aria-hidden="true" />
      {story.topic}
    </span>
  )
}

export function LocationPill() {
  const { story } = usePost()
  if (!story.location) return null
  return (
    <span className={styles.pill}>
      <MapPin size={14} aria-hidden="true" />
      <span className="sr-only">Location: </span>
      {story.location}
    </span>
  )
}

export function MoreButton() {
  return (
    <button type="button" className={styles.iconButton} aria-label="More options">
      <Ellipsis size={20} aria-hidden="true" />
    </button>
  )
}

/* The full header used by the Original layout. */
export function PostHeader() {
  const { story } = usePost()
  return (
    <header className={styles.header}>
      <PublisherAvatar size={44} />
      <div className={styles.who}>
        <PublisherName />
        <span className={styles.meta}>By {story.author}</span>
        <span className={styles.meta}>
          {story.publishedAgo} · {story.topic}
          {story.location && (
            <span className={styles.location}>
              {' · '}
              <MapPin size={13} aria-hidden="true" />
              {story.location}
            </span>
          )}
        </span>
      </div>
      <div className={styles.end}>
        <TagPill />
        <MoreButton />
      </div>
    </header>
  )
}
