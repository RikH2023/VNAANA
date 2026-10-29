import { useEffect, useRef, useState } from 'react'
import type { FocusEvent } from 'react'
import { BadgeCheck, Ellipsis, EyeOff, MapPin } from 'lucide-react'
import { TOPIC_ICONS } from '../../data/topics'
import { usePost } from './PostContext'
import styles from './PostHeader.module.css'

/*
 * Small pieces that describe a post (who, when, what, where).
 * The Instagram Style layout uses the full <PostHeader>; other layouts
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
export function Byline({ showTime = true }: { showTime?: boolean }) {
  const { story } = usePost()
  return (
    <div className={styles.byline}>
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

/*
 * "⋯" button with a small menu of post options.
 * Esc, clicking outside or tabbing away closes it.
 * `opens` sets the direction, so the menu is never cut off by the card edge.
 * `floating` gives the button the round white look of the Poster button column.
 */
export function MoreMenu({ opens = 'down', floating = false }: { opens?: 'down' | 'up' | 'left'; floating?: boolean }) {
  const { story, actions } = usePost()
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)
  const buttonRef = useRef<HTMLButtonElement>(null)
  const firstItemRef = useRef<HTMLButtonElement>(null)
  const menuId = `${story.id}-menu`

  useEffect(() => {
    if (!open) return
    firstItemRef.current?.focus()

    const onPointerDown = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false)
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setOpen(false)
        buttonRef.current?.focus()
      }
    }
    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('pointerdown', onPointerDown)
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [open])

  // Close when keyboard focus leaves the menu
  const onBlur = (event: FocusEvent) => {
    if (!rootRef.current?.contains(event.relatedTarget as Node)) setOpen(false)
  }

  return (
    <div ref={rootRef} className={styles.menuRoot} onBlur={onBlur}>
      <button
        ref={buttonRef}
        type="button"
        className={`${styles.iconButton} ${floating ? styles.floatingButton : ''}`}
        aria-label="More options"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls={open ? menuId : undefined}
        onClick={() => setOpen((value) => !value)}
      >
        <Ellipsis size={20} aria-hidden="true" />
      </button>
      {open && (
        <div id={menuId} role="menu" aria-label="Post options" className={styles.menu} data-opens={opens}>
          <button
            ref={firstItemRef}
            type="button"
            role="menuitem"
            className={styles.menuItem}
            onClick={() => {
              setOpen(false)
              actions.hide()
            }}
          >
            <EyeOff size={18} aria-hidden="true" />
            <span>
              <span className={styles.menuItemTitle}>Not interested</span>
              <span className={styles.menuItemHint}>Show fewer stories like this</span>
            </span>
          </button>
        </div>
      )}
    </div>
  )
}

/*
 * The top bar used by the Instagram Style layout:
 * byline, then the label pills (topic, location), then the ⋯ menu.
 */
export function PostHeader() {
  return (
    <header className={styles.header}>
      <div className={styles.headerByline}>
        <Byline />
      </div>
      <div className={styles.labels}>
        <TopicPill />
        <LocationPill />
      </div>
      <div className={styles.headerMenu}>
        <MoreMenu />
      </div>
    </header>
  )
}
