import { ChevronLeft, ChevronRight } from 'lucide-react'
import { PART_LABELS, usePost } from './PostContext'
import styles from './CarouselControls.module.css'

/*
 * Arrows and progress indicators for the story carousel.
 * They all read the shared carousel state, so they can be placed anywhere in the post.
 */

/* Arrows that float over the carousel */
export function CarouselArrows() {
  const { carousel } = usePost()
  return (
    // data-text-part: part 2 is scrolling text, so the arrows get a solid bar on small screens.
    // Part 3 doesn't need one: its chat input makes room for the arrow.
    <div className={styles.arrows} data-text-part={!carousel.isFirst && !carousel.isLast}>
      <button
        type="button"
        className={`${styles.arrow} ${styles.prev}`}
        onClick={carousel.prev}
        aria-label={`Previous: ${PART_LABELS[carousel.index - 1] ?? ''}`}
        hidden={carousel.isFirst}
      >
        <ChevronLeft size={22} aria-hidden="true" />
      </button>
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
export function PartDots() {
  const { carousel } = usePost()
  return (
    <span className={styles.dots} aria-hidden="true">
      {Array.from({ length: carousel.count }, (_, i) => (
        <span key={i} className={styles.dot} data-active={i === carousel.index} />
      ))}
    </span>
  )
}

type SegmentsProps = {
  total: number
  filled: number
  className?: string
}

/* A row of bars on a dark background. Used by the briefing card. */
export function Segments({ total, filled, className = '' }: SegmentsProps) {
  return (
    <span className={`${styles.segments} ${className}`} aria-hidden="true">
      {Array.from({ length: total }, (_, i) => (
        <span key={i} className={styles.segment} data-on={i < filled} />
      ))}
    </span>
  )
}
