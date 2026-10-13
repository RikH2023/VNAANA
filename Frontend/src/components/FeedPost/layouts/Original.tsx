import { PostCarousel } from '../PostCarousel'
import { PostHeader } from '../PostHeader'
import { ReactionBar } from '../ReactionBar'
import { StepTabs } from '../StepTabs'
import { ReadMorePart, WhatHappenedPart, WhyPart } from '../parts/Parts'
import styles from './Original.module.css'

/* 1. Original: header, 3-part carousel, step tabs, reactions. */
export function OriginalLayout() {
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
      <StepTabs />
      <footer className={styles.footer}>
        <ReactionBar kinds={['like', 'dislike', 'notInterested', 'share', 'save']} ask="pill" />
      </footer>
    </>
  )
}
