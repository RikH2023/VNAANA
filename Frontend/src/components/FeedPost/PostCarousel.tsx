import type { CSSProperties, ReactNode } from 'react'
import { CarouselArrows, CounterPill } from './CarouselControls'
import { PART_LABELS, usePost } from './PostContext'
import styles from './PostCarousel.module.css'

type PartPadding = { top?: number; right?: number; bottom?: number }

type Props = {
  /** One element per part: What happened, Why it matters, Read more. */
  parts: ReactNode[]
  /** Layout class that sets the size (--parts-h) and shape. */
  className?: string
  arrows?: 'overlay' | 'none'
  showCounter?: boolean
  /** Extra things drawn on top (pills, progress bars…). */
  overlay?: ReactNode
  /** Extra room inside the text parts, e.g. to clear overlays. */
  partPadding?: PartPadding
}

/*
 * The side-to-side story carousel. Every part has the same height,
 * so moving between parts never changes the size of the post.
 * Arrow keys and touch swipes work when it has focus / is touched.
 */
export function PostCarousel({ parts, className = '', arrows = 'overlay', showCounter = false, overlay, partPadding }: Props) {
  const { story, carousel, partIds } = usePost()

  const paddingVars = {
    '--part-pad-top': partPadding?.top && `${partPadding.top}px`,
    '--part-pad-right': partPadding?.right && `${partPadding.right}px`,
    '--part-pad-bottom': partPadding?.bottom && `${partPadding.bottom}px`,
  } as CSSProperties

  return (
    <div className={`${styles.wrap} ${className}`} data-arrows={arrows}>
      <div
        className={styles.viewport}
        style={paddingVars}
        role="region"
        aria-roledescription="carousel"
        aria-label={`${story.title}, in ${carousel.count} parts. Use the left and right arrow keys to move.`}
        tabIndex={0}
        {...carousel.keyHandlers}
        {...carousel.swipeHandlers}
      >
        <div className={styles.track} style={{ transform: `translateX(${carousel.index * -100}%)` }}>
          {parts.map((part, i) => (
            <div
              key={partIds[i]}
              id={partIds[i]}
              className={styles.slide}
              role="group"
              aria-roledescription="part"
              aria-label={`${i + 1} of ${carousel.count}: ${PART_LABELS[i]}`}
              inert={i !== carousel.index}
            >
              {part}
            </div>
          ))}
        </div>
      </div>

      {overlay}
      {showCounter && <CounterPill />}
      {arrows === 'overlay' && <CarouselArrows />}

      <p className="sr-only" aria-live="polite">
        Part {carousel.index + 1} of {carousel.count}: {PART_LABELS[carousel.index]}
      </p>
    </div>
  )
}
