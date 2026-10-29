import { useEffect, useRef } from 'react'
import type { KeyboardEvent, TouchEvent } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { LocationPill, MoreMenu, PublisherName, TopicPill } from '../PostHeader'
import { usePost } from '../PostContext'
import { ReactionBar } from '../ReactionBar'
import { ReadMorePart, StoryImage, WhyPart } from '../parts/Parts'
import shared from './shared.module.css'
import styles from './Flipbook.module.css'

const SWIPE_MIN_PX = 40

/*
 * 4. Flipbook: the post is a small book with two spreads.
 *   Spread 1: image | headline, summary and actions.
 *   Spread 2: Why it matters | Read more + Ask Nova chat.
 * The right page is one leaf: the headline on its front, "Why it matters" on its back.
 * Turning it over the spine in the middle shows spread 2. On narrow screens the
 * pages stack and the bottom half folds up over the top one instead.
 *
 * The arrows sit together in a row centred below the book.
 *
 * The shared carousel has 3 parts; here part 1 is spread 1 and parts 2 and 3 are spread 2.
 */
export function FlipbookLayout() {
  const { story, carousel, titleId } = usePost()
  const turned = carousel.index > 0
  const touchStart = useRef<{ x: number; y: number } | null>(null)
  const backRef = useRef<HTMLButtonElement>(null)
  const forwardRef = useRef<HTMLButtonElement>(null)
  const arrowClicked = useRef(false)

  const turnForward = () => carousel.goTo(1)
  const turnBack = () => carousel.goTo(0)

  // The clicked arrow becomes disabled, so move focus to the other one
  useEffect(() => {
    if (!arrowClicked.current) return
    arrowClicked.current = false
    const enabledArrow = turned ? backRef.current : forwardRef.current
    enabledArrow?.focus({ preventScroll: true })
  }, [turned])

  const onArrowClick = (turn: () => void) => () => {
    arrowClicked.current = true
    turn()
  }

  const onKeyDown = (event: KeyboardEvent) => {
    if ((event.target as HTMLElement).closest('input, textarea')) return
    if (event.key === 'ArrowRight' && !turned) {
      event.preventDefault()
      turnForward()
    } else if (event.key === 'ArrowLeft' && turned) {
      event.preventDefault()
      turnBack()
    }
  }

  const onTouchStart = (event: TouchEvent) => {
    const touch = event.touches[0]
    touchStart.current = { x: touch.clientX, y: touch.clientY }
  }

  // Only clearly horizontal swipes turn the page, so the pages can still scroll
  const onTouchEnd = (event: TouchEvent) => {
    const start = touchStart.current
    touchStart.current = null
    if (!start) return
    const touch = event.changedTouches[0]
    const dx = touch.clientX - start.x
    const dy = touch.clientY - start.y
    if (Math.abs(dx) < SWIPE_MIN_PX || Math.abs(dx) < Math.abs(dy)) return
    if (dx < 0) turnForward()
    else turnBack()
  }

  return (
    <div className={styles.flipbook}>
      <div
        className={styles.book}
        data-turned={turned}
        role="region"
        aria-roledescription="carousel"
        aria-label={`${story.title}, a book of two spreads. Use the left and right arrow keys to turn the page.`}
        tabIndex={0}
        onKeyDown={onKeyDown}
        onTouchStart={onTouchStart}
        onTouchEnd={onTouchEnd}
      >
        {/* Spread 1, left page: covered by the leaf once it is turned */}
        <div className={styles.imagePage} aria-hidden={turned}>
          <StoryImage className={styles.image} />
        </div>

        {/* Spread 2, right page: lies under the leaf until it is turned */}
        <div className={styles.readMorePage} inert={!turned}>
          <ReadMorePart density="full" />
        </div>

        <div className={styles.leaf}>
          <div className={`${styles.face} ${styles.front}`} inert={turned}>
            <div className={styles.content}>
              <div className={styles.top}>
                <div className={shared.pills}>
                  <TopicPill />
                  <LocationPill />
                </div>
                <div className={styles.menu}>
                  <MoreMenu />
                </div>
              </div>
              <div>
                <h2 id={titleId} className={`${shared.headline} ${styles.headline}`}>
                  {story.title}
                </h2>
                <p className={styles.meta}>
                  <PublisherName />
                  <span className={styles.time}> · {story.publishedAgo}</span>
                </p>
                <p className={`${shared.summary} ${styles.summary}`}>{story.summary}</p>
              </div>
              <ReactionBar className={styles.actions} kinds={['like', 'share']} likeIcon="heart" ask="pill" />
            </div>
          </div>
          <div className={`${styles.face} ${styles.back}`} inert={!turned}>
            <WhyPart density="full" />
          </div>
        </div>

        <p className="sr-only" aria-live="polite">
          {turned ? 'Pages 3 and 4 of 4: Why it matters, Read more' : 'Pages 1 and 2 of 4: the story'}
        </p>
      </div>

      <div className={styles.turns}>
        <button
          ref={backRef}
          type="button"
          className={styles.turnBack}
          onClick={onArrowClick(turnBack)}
          disabled={!turned}
          aria-label="Previous page: the story"
        >
          <ChevronLeft size={22} aria-hidden="true" />
        </button>
        <button
          ref={forwardRef}
          type="button"
          className={styles.turnForward}
          onClick={onArrowClick(turnForward)}
          disabled={turned}
          aria-label="Next page: Why it matters and Read more"
        >
          <ChevronRight size={22} aria-hidden="true" />
        </button>
      </div>
    </div>
  )
}
