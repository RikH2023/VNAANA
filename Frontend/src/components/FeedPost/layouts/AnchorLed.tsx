import { NovaAvatar } from '../../NovaAvatar/NovaAvatar'
import { PartDots } from '../CarouselControls'
import { PostCarousel } from '../PostCarousel'
import { Byline, LocationPill, TopicPill } from '../PostHeader'
import { usePost } from '../PostContext'
import { AskNovaInput, ReactionBar } from '../ReactionBar'
import { ReadMorePart, StoryImage, WhyPart } from '../parts/Parts'
import shared from './shared.module.css'
import styles from './AnchorLed.module.css'

/* 7. Anchor-led: Nova explains why it picked the story before you see it. */
export function AnchorLedLayout() {
  const { story, titleId } = usePost()
  return (
    <>
      <div className={styles.strip}>
        <NovaAvatar size={40} />
        <p>
          <span className={styles.stripLabel}>Why Nova picked this</span>
          {story.whyPicked}
        </p>
      </div>
      <PostCarousel
        className={styles.carousel}
        partPadding={{ top: 56 }}
        parts={[<StoryImage />, <WhyPart />, <ReadMorePart />]}
        overlay={
          <div className={`${shared.pills} ${styles.pills}`}>
            <TopicPill />
            <LocationPill />
          </div>
        }
      />
      <div className={styles.meta}>
        <Byline />
        <PartDots />
      </div>
      <div className={styles.body}>
        <h2 id={titleId} className={shared.headline}>
          {story.title}
        </h2>
        <p className={shared.summary}>{story.summary}</p>
      </div>
      <ReactionBar
        className={styles.reactions}
        kinds={['like', 'dislike', 'notInterested', 'share', 'save']}
        ask={null}
      />
      <div className={styles.ask}>
        <AskNovaInput placeholder="Ask Nova: what does this mean for me?" fallbackQuestion="What does this mean for me?" />
      </div>
    </>
  )
}
