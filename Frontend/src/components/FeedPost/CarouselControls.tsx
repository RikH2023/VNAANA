import type { ReactNode } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { PART_LABELS, usePost } from './PostContext'
import styles from './CarouselControls.module.css'

/*
 * Arrows and progress indicators for the story carousel.
 * They all read the shared carousel state, so any layout can place them anywhere.
 */

type ArrowsProps = {
  /** "overlay" floats over the carousel; "inline" sits in a normal row. */
  placement?: 'overlay' | 'inline'
  /** Optional content shown between the two arrows. */
  children?: ReactNode
}

export function CarouselArrows({ placement = 'overlay', children }: ArrowsProps) {
  const { carousel } = usePost()
  return (
    // data-text-part: part 2 is scrolling text, so the overlay gets a solid bar on small screens.
    // Part 3 doesn't need one: its chat input makes room for the arrow.
    <div
      className={`${styles.arrows} ${styles[placement]}`}
      data-part={carousel.index}
      data-text-part={!carousel.isFirst && !carousel.isLast}
    >
      <button
        type="button"
        className={`${styles.arrow} ${styles.prev}`}
        onClick={carousel.prev}
        aria-label={`Previous: ${PART_LABELS[carousel.index - 1] ?? ''}`}
        hidden={carousel.isFirst}
      >
        <ChevronLeft size={22} aria-hidden="true" />
      </button>
      {children}
      <button
        type="button"
        className={`${styles.arrow} ${styles.next}`}
        onClick={carousel.next}
        aria-label={`Next: ${PART_LABELS[carousel.index + 1] ?? ''}`}
        hidden={carousel.isLast}
      >
        <ChevronRight size={22} aria-hidden="true" />
      </button>
    </div>
  )
}

export function CounterPill() {
  const { carousel } = usePost()
  return (
    <span className={styles.counter} aria-hidden="true">
      {carousel.index + 1} / {carousel.count}
    </span>
  )
}

/* Visual-only dots; the carousel announces the part to screen readers. */
export function PartDots({ tone = 'light' }: { tone?: 'light' | 'onImage' }) {
  const { carousel } = usePost()
  return (
    <span className={`${styles.dots} ${styles[tone]}`} aria-hidden="true">
      {Array.from({ length: carousel.count }, (_, i) => (
        <span key={i} className={styles.dot} data-active={i === carousel.index} />
      ))}
    </span>
  )
}

type SegmentsProps = {
  total: number
  filled: number
  /** "dark" for dark backgrounds (briefing card), "light" for light ones (Poster) */
  tone?: 'dark' | 'light'
  className?: string
}

/* A row of bars. Used by the Poster layout and the briefing card. */
export function Segments({ total, filled, tone = 'dark', className = '' }: SegmentsProps) {
  return (
    <span className={`${styles.segments} ${className}`} data-tone={tone} aria-hidden="true">
      {Array.from({ length: total }, (_, i) => (
        <span key={i} className={styles.segment} data-on={i < filled} />
      ))}
    </span>
  )
}
