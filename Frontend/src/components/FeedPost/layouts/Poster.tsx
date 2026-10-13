import { CarouselArrows, Segments } from '../CarouselControls'
import { PostCarousel } from '../PostCarousel'
import { Byline, LocationPill, TopicPill } from '../PostHeader'
import { usePost } from '../PostContext'
import { ReactionBar } from '../ReactionBar'
import { ReadMorePart, StoryImage, WhyPart } from '../parts/Parts'
import shared from './shared.module.css'
import styles from './Poster.module.css'

const HINTS = ['Swipe for why it matters →', 'Swipe for the full story →', '← Back to the story']

/* 4. Full-bleed poster (Reels / Stories): the image fills a tall card. */
export function PosterLayout() {
  const { story, carousel, titleId } = usePost()

  const cover = (
    <div className={styles.cover}>
      <StoryImage />
      <div className={styles.panel}>
        <Byline onDark />
        <h2 id={titleId} className={styles.headline}>
          {story.title}
        </h2>
        <p className={styles.summary}>{story.summary}</p>
      </div>
    </div>
  )

  return (
    <div className={styles.poster}>
      <PostCarousel
        className={styles.carousel}
        arrows="none"
        // Keep the Why / Read more text clear of the overlays below
        partPadding={{ top: 76, right: 76, bottom: 84 }}
        parts={[cover, <WhyPart />, <ReadMorePart />]}
        overlay={
          <>
            <div className={styles.top}>
              <Segments total={carousel.count} filled={carousel.index + 1} className={styles.progress} />
              <div className={shared.pills}>
                <TopicPill />
                <LocationPill />
              </div>
            </div>
            <ReactionBar
              className={styles.rail}
              variant="floating"
              ask="round"
              kinds={['like', 'dislike', 'notInterested', 'share']}
            />
            <div className={styles.strip}>
              <CarouselArrows placement="inline">
                <span className={styles.hint} aria-hidden="true">
                  {HINTS[carousel.index]}
                </span>
              </CarouselArrows>
            </div>
          </>
        }
      />
    </div>
  )
}
