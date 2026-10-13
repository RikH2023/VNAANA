import { PartDots } from '../CarouselControls'
import { PostCarousel } from '../PostCarousel'
import { PostHeader } from '../PostHeader'
import { ReactionBar } from '../ReactionBar'
import { ReadMorePart, WhatHappenedPart, WhyPart } from '../parts/Parts'
import shared from './shared.module.css'
import styles from './InstagramStyle.module.css'

/*
 * 1. Instagram Style: top bar with labels and a ⋯ menu ("Not interested"),
 * 3-part carousel, progress dots, then like / share / Ask Nova.
 */
export function InstagramStyleLayout() {
  return (
    <>
      <PostHeader />
      <PostCarousel
        className={styles.carousel}
        showCounter
        // Room for the "1 / 3" pill above the Why / Read more panels
        partPadding={{ top: 52 }}
        parts={[<WhatHappenedPart />, <WhyPart density="full" />, <ReadMorePart density="full" />]}
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
