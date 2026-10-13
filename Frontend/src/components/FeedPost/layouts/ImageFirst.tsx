import { PartDots } from '../CarouselControls'
import { PostCarousel } from '../PostCarousel'
import { Byline, LocationPill, MoreButton, TopicPill } from '../PostHeader'
import { usePost } from '../PostContext'
import { AskNovaButton, ReactionBar } from '../ReactionBar'
import { ReadMorePart, StoryImage, WhyPart } from '../parts/Parts'
import shared from './shared.module.css'
import styles from './ImageFirst.module.css'

/* 2. Image first (Instagram): big image, reactions right under it, then the text. */
export function ImageFirstLayout() {
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
      <PostCarousel
        className={styles.carousel}
        showCounter
        // Room for the "1 / 3" pill above the Why / Read more panels
        partPadding={{ top: 50 }}
        parts={[<StoryImage />, <WhyPart />, <ReadMorePart />]}
      />
      <ReactionBar
        className={styles.reactions}
        kinds={['like', 'dislike', 'notInterested', 'share', 'save']}
        ask={null}
        trailing={<PartDots />}
      />
      <div className={styles.body}>
        <h2 id={titleId} className={shared.headline}>
          {story.title}
        </h2>
        <p className={shared.summary}>{story.summary}</p>
      </div>
      <footer className={shared.footerSpread}>
        <LocationPill />
        <AskNovaButton variant="pill" />
      </footer>
    </>
  )
}
