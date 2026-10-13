import { PartDots } from '../CarouselControls'
import { PostCarousel } from '../PostCarousel'
import { Byline, LocationPill, TopicPill } from '../PostHeader'
import { usePost } from '../PostContext'
import { AskNovaInput, ReactionBar } from '../ReactionBar'
import { ReadMorePart, StoryImage, WhyPart } from '../parts/Parts'
import shared from './shared.module.css'
import styles from './Split.module.css'

/* 4. Split (desktop): carousel on the left, text and actions on the right. Stacks on narrow screens. */
export function SplitLayout() {
  const { story, titleId } = usePost()
  return (
    <div className={styles.split}>
      <PostCarousel
        className={styles.media}
        // The dots sit at the top; keep the Why / Read more text below them
        partPadding={{ top: 52 }}
        parts={[<StoryImage />, <WhyPart />, <ReadMorePart />]}
        overlay={
          <div className={styles.dots}>
            <PartDots tone="onImage" />
          </div>
        }
      />
      <div className={styles.content}>
        <div className={shared.pills}>
          <TopicPill />
          <LocationPill />
        </div>
        <h2 id={titleId} className={`${shared.headline} ${styles.headline}`}>
          {story.title}
        </h2>
        <p className={shared.summary}>{story.summary}</p>
        <Byline />
        <div className={styles.actions}>
          <ReactionBar
            className={styles.reactions}
            variant="labelled"
            kinds={['like', 'dislike', 'notInterested', 'share']}
            ask={null}
          />
          <AskNovaInput placeholder="Ask Nova about this story…" />
        </div>
      </div>
    </div>
  )
}
