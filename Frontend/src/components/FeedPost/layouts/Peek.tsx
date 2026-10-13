import { useEffect, useRef } from 'react'
import { CarouselArrows, PartDots } from '../CarouselControls'
import { Byline, LocationPill, MoreButton, TopicPill } from '../PostHeader'
import { PART_LABELS, usePost } from '../PostContext'
import { ReactionBar } from '../ReactionBar'
import { ReadMorePart, StoryImage, WhyPart } from '../parts/Parts'
import shared from './shared.module.css'
import styles from './Peek.module.css'

/* Scroll position at which each card is snapped into place */
function cardPositions(track: HTMLElement) {
  const cards = Array.from(track.children) as HTMLElement[]
  return cards.map((card) => card.offsetLeft - cards[0].offsetLeft)
}

/*
 * A horizontally scrolling track where the next part peeks in from the right.
 * Uses native scroll-snap, and keeps the shared carousel state in sync:
 * arrows / dots / keys scroll the track, and scrolling by hand updates the state.
 */
function PeekTrack() {
  const { story, carousel, partIds } = usePost()
  const trackRef = useRef<HTMLDivElement>(null)
  const settleTimer = useRef<number | undefined>(undefined)

  // State → scroll position
  useEffect(() => {
    const track = trackRef.current
    if (!track) return
    const maxScroll = track.scrollWidth - track.clientWidth
    const left = Math.min(cardPositions(track)[carousel.index], maxScroll)
    if (Math.abs(track.scrollLeft - left) > 2) track.scrollTo({ left, behavior: 'smooth' })
  }, [carousel.index])

  // Scroll position → state (once scrolling has settled)
  const onScroll = () => {
    window.clearTimeout(settleTimer.current)
    settleTimer.current = window.setTimeout(() => {
      const track = trackRef.current
      if (!track) return
      const positions = cardPositions(track)
      const atEnd = track.scrollLeft >= track.scrollWidth - track.clientWidth - 4
      const distance = (i: number) => Math.abs(positions[i] - track.scrollLeft)
      const nearest = atEnd
        ? positions.length - 1
        : positions.reduce((best, _, i) => (distance(i) < distance(best) ? i : best), 0)
      if (nearest !== carousel.index) carousel.goTo(nearest)
    }, 120)
  }

  useEffect(() => () => window.clearTimeout(settleTimer.current), [])

  const parts = [<StoryImage />, <WhyPart />, <ReadMorePart />]

  return (
    <>
      <div
        ref={trackRef}
        className={styles.track}
        role="region"
        aria-roledescription="carousel"
        aria-label={`${story.title}, in ${carousel.count} parts. Use the left and right arrow keys to move.`}
        tabIndex={0}
        onScroll={onScroll}
        {...carousel.keyHandlers}
      >
        {parts.map((part, i) => (
          <div
            key={partIds[i]}
            id={partIds[i]}
            className={styles.card}
            role="group"
            aria-roledescription="part"
            aria-label={`${i + 1} of ${carousel.count}: ${PART_LABELS[i]}`}
          >
            {part}
          </div>
        ))}
      </div>
      <p className="sr-only" aria-live="polite">
        Part {carousel.index + 1} of {carousel.count}: {PART_LABELS[carousel.index]}
      </p>
    </>
  )
}

/* 6. Peek carousel (LinkedIn document style). */
export function PeekLayout() {
  const { story, titleId } = usePost()
  return (
    <>
      <header className={shared.header}>
        <Byline />
        <div className={shared.headerEnd}>
          <TopicPill />
          <MoreButton />
        </div>
      </header>
      <div className={styles.body}>
        <h2 id={titleId} className={shared.headline}>
          {story.title}
        </h2>
        <p className={shared.summary}>{story.summary}</p>
      </div>
      <PeekTrack />
      <div className={styles.controls}>
        <LocationPill />
        <PartDots />
        <CarouselArrows placement="inline" />
      </div>
      <footer className={shared.footer}>
        <ReactionBar kinds={['like', 'dislike', 'notInterested', 'share', 'save']} ask="short" className={styles.bar} />
      </footer>
    </>
  )
}
