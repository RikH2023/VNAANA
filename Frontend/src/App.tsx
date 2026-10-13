import { useCallback, useRef, useState } from 'react'
import { BriefingCard } from './components/BriefingCard/BriefingCard'
import { FeedPost } from './components/FeedPost/FeedPost'
import { DEFAULT_LAYOUT, isPostLayoutKey, isWideLayout } from './components/FeedPost/layouts'
import type { PostLayoutKey } from './components/FeedPost/layouts'
import { LayoutSwitcher } from './components/LayoutSwitcher/LayoutSwitcher'
import { MobileTabBar, MobileTopBar } from './components/Navigation/MobileBars'
import { Sidebar } from './components/Navigation/Sidebar'
import { briefingMeta, sampleStories, sampleUser } from './data/sampleStories'
import { readStorage, writeStorage } from './lib/storage'
import styles from './App.module.css'

const LAYOUT_STORAGE_KEY = 'vnaana.postLayout'
// Session storage: the briefing comes back in a new browser session, like a new morning notification.
const BRIEFING_STORAGE_KEY = 'vnaana.briefingDismissed'

function loadLayout(): PostLayoutKey {
  const saved = readStorage(LAYOUT_STORAGE_KEY)
  return isPostLayoutKey(saved) ? saved : DEFAULT_LAYOUT
}

export default function App() {
  const [layout, setLayout] = useState<PostLayoutKey>(loadLayout)
  const [openedIds, setOpenedIds] = useState<Set<string>>(() => new Set())
  const [briefingDismissed, setBriefingDismissed] = useState(
    () => readStorage(BRIEFING_STORAGE_KEY, 'session') === 'true',
  )
  const feedRef = useRef<HTMLElement>(null)

  const changeLayout = (next: PostLayoutKey) => {
    setLayout(next)
    writeStorage(LAYOUT_STORAGE_KEY, next)
  }

  const dismissBriefing = () => {
    setBriefingDismissed(true)
    writeStorage(BRIEFING_STORAGE_KEY, 'true', 'session')
    // The close button disappears, so move keyboard focus to the feed.
    feedRef.current?.focus()
  }

  const markOpened = useCallback((storyId: string) => {
    setOpenedIds((ids) => (ids.has(storyId) ? ids : new Set(ids).add(storyId)))
  }, [])

  const forYouCount = sampleStories.filter((story) => story.feedReason === 'forYou').length
  const wide = isWideLayout(layout)

  return (
    <div className={styles.app}>
      <a href="#feed" className={styles.skipLink}>
        Skip to feed
      </a>
      <Sidebar user={sampleUser} />
      <MobileTopBar />

      {/*
        The feed scrolls on its own and snaps to one post at a time:
        every post sits in a full-height "slide".
      */}
      <main ref={feedRef} id="feed" className={styles.feed} tabIndex={-1} aria-label="For You feed">
        <div className={styles.intro}>
          <div className={styles.column} data-wide={wide}>
            <LayoutSwitcher value={layout} onChange={changeLayout} />
            {!briefingDismissed && (
              <BriefingCard
                firstName={sampleUser.firstName}
                forYouCount={forYouCount}
                dontMissCount={sampleStories.length - forYouCount}
                openedCount={openedIds.size}
                readTime={briefingMeta.readTime}
                updatedAt={briefingMeta.updatedAt}
                onDismiss={dismissBriefing}
              />
            )}
          </div>
        </div>

        {sampleStories.map((story) => (
          <div key={story.id} className={styles.slide}>
            <div className={styles.column} data-wide={wide}>
              <FeedPost story={story} layout={layout} onOpened={markOpened} />
            </div>
          </div>
        ))}

        <footer className={styles.feedEnd}>
          <p>You’re all caught up for this morning.</p>
        </footer>
      </main>

      <MobileTabBar />
    </div>
  )
}
