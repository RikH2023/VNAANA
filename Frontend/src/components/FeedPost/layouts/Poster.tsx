import { useLayoutEffect, useRef, useState } from 'react'
import type { CSSProperties } from 'react'
import { Segments } from '../CarouselControls'
import { PostCarousel } from '../PostCarousel'
import { LocationPill, MoreMenu, PublisherName, TopicPill } from '../PostHeader'
import { usePost } from '../PostContext'
import { ReactionBar } from '../ReactionBar'
import { ReadMorePart, StoryImage, WhyPart } from '../parts/Parts'
import shared from './shared.module.css'
import styles from './Poster.module.css'

/*
 * Where the labels row starts and where its middle is, measured from the top of the card.
 * The text panel's height depends on the story, so this is measured, not fixed.
 * The arrows sit at the labels' height; the button column is centred on the image above them.
 */
function useLabelsPosition() {
  const bottomRef = useRef<HTMLDivElement>(null)
  const [position, setPosition] = useState<{ top: number; middle: number }>()

  useLayoutEffect(() => {
    const bottom = bottomRef.current
    const cover = bottom?.parentElement
    const labels = bottom?.firstElementChild as HTMLElement | null
    if (!bottom || !cover || !labels) return

    const measure = () => {
      const top = cover.clientHeight - bottom.offsetHeight
      setPosition({ top, middle: top + labels.offsetHeight / 2 })
    }
    measure()
    const observer = new ResizeObserver(measure)
    observer.observe(cover)
    observer.observe(bottom)
    return () => observer.disconnect()
  }, [])

  return { bottomRef, position }
}

/* 3. Full-bleed poster (Reels / Stories), light version: the image fills a tall card. */
export function PosterLayout() {
  const { story, carousel, titleId } = usePost()
  const { bottomRef, position } = useLabelsPosition()

  const positionVars = position && ({
    '--arrow-top': `${position.middle}px`,
    '--labels-top': `${position.top}px`,
  } as CSSProperties)

  // Part 1: the image with the labels and a white text panel at the bottom.
  // The labels belong to this part, so they swipe away with it.
  const cover = (
    <div className={styles.cover}>
      <StoryImage />
      <div ref={bottomRef} className={styles.bottom}>
        <div className={shared.pills}>
          <TopicPill />
          <LocationPill />
        </div>
        <div className={styles.panel}>
          <h2 id={titleId} className={styles.headline}>
            {story.title}
          </h2>
          <p className={styles.meta}>
            <PublisherName />
            <span className={styles.time}> · {story.publishedAgo}</span>
          </p>
          <p className={styles.summary}>{story.summary}</p>
        </div>
      </div>
    </div>
  )

  return (
    <div className={styles.poster} style={positionVars}>
      <PostCarousel
        className={styles.carousel}
        arrowPosition="pinned"
        // Keep the Why / Read more text clear of the progress bar and the button column
        partPadding={{ top: 48, right: 76 }}
        parts={[cover, <WhyPart />, <ReadMorePart />]}
        overlay={
          <>
            <Segments total={carousel.count} filled={carousel.index + 1} tone="light" className={styles.progress} />
            <div className={styles.rail}>
              <ReactionBar variant="floating" ask="round" kinds={['like', 'share']} likeIcon="heart" />
              <MoreMenu floating opens="left" />
            </div>
          </>
        }
      />
    </div>
  )
}
