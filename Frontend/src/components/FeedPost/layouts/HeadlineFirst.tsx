import { PartDots } from '../CarouselControls'
import { PostCarousel } from '../PostCarousel'
import { Byline, LocationPill, TopicPill } from '../PostHeader'
import { usePost } from '../PostContext'
import { ActionButton, ReactionBar } from '../ReactionBar'
import { ReadMorePart, StoryImage, WhyPart } from '../parts/Parts'
import shared from './shared.module.css'
import styles from './HeadlineFirst.module.css'

/* 3. Headline first (Threads / X): text leads, the image follows. */
export function HeadlineFirstLayout() {
  const { story, titleId } = usePost()
  return (
    <>
      <header className={shared.header}>
        <Byline />
        <ActionButton kind="notInterested" />
      </header>
      <div className={styles.text}>
        <div className={shared.pills}>
          <TopicPill />
          <LocationPill />
        </div>
        <h2 id={titleId} className={`${shared.headline} ${styles.headline}`}>
          {story.title}
        </h2>
        <p className={shared.summary}>{story.summary}</p>
      </div>
      <PostCarousel className={styles.carousel} parts={[<StoryImage />, <WhyPart />, <ReadMorePart />]} />
      <div className={styles.dots}>
        <PartDots />
      </div>
      <footer className={shared.footer}>
        <ReactionBar kinds={['like', 'dislike', 'share']} ask="pill" className={styles.bar} />
      </footer>
    </>
  )
}
