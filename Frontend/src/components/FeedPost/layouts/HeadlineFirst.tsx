import { PartDots } from '../CarouselControls'
import { PostCarousel } from '../PostCarousel'
import { PostHeader } from '../PostHeader'
import { ReactionBar } from '../ReactionBar'
import { ReadMorePart, WhatHappenedPart, WhyPart } from '../parts/Parts'
import shared from './shared.module.css'
import styles from './HeadlineFirst.module.css'

/*
 * 2. Headline first: the same as Instagram Style, but in part 1 the headline
 * and summary come before the image. Text and image swipe away together.
 */
export function HeadlineFirstLayout() {
  return (
    <>
      <PostHeader />
      <PostCarousel
        className={styles.carousel}
        showCounter
        // Room for the "1 / 3" pill above the text and the Why / Read more panels
        partPadding={{ top: 52 }}
        parts={[<WhatHappenedPart textFirst />, <WhyPart density="full" />, <ReadMorePart density="full" />]}
      />
      <div className={shared.dotsRow}>
        <PartDots />
      </div>
      <footer className={shared.actionsFooter}>
        <ReactionBar kinds={['like', 'share']} likeIcon="heart" ask="pill" />
      </footer>
    </>
  )
}
