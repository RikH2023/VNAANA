import { Compass, Settings, Sparkles } from 'lucide-react'
import { TOPICS, TOPIC_ICONS } from '../../data/topics'
import type { User } from '../../types'
import { Logo } from './Logo'
import { SearchField } from './SearchField'
import styles from './Navigation.module.css'

/* Desktop navigation. Below 820px it is replaced by MobileTopBar + MobileTabBar. */
export function Sidebar({ user }: { user: User }) {
  return (
    <aside className={styles.sidebar}>
      <Logo />
      <SearchField id="sidebar-search" />

      <nav aria-label="Main">
        <ul className={styles.mainNav}>
          <li>
            <a href="/" className={styles.navItem} aria-current="page">
              <Sparkles size={20} aria-hidden="true" />
              For You
              <span className={styles.activeDot} aria-hidden="true" />
            </a>
          </li>
          <li>
            <a href="#explore" className={styles.navItem}>
              <Compass size={20} aria-hidden="true" />
              Explore
            </a>
          </li>
        </ul>
      </nav>

      <section className={styles.topics} aria-labelledby="topics-heading">
        <div className={styles.topicsHeader}>
          <h2 id="topics-heading" className={styles.sectionTitle}>
            Topics
          </h2>
          <button type="button" className={styles.editLink}>
            Edit<span className="sr-only"> topics</span>
          </button>
        </div>
        <ul>
          {TOPICS.map((topic) => {
            const Icon = TOPIC_ICONS[topic]
            const following = user.followedTopics.includes(topic)
            return (
              <li key={topic}>
                <a href={`#topic-${topic.toLowerCase()}`} className={styles.topicRow}>
                  <span className={styles.topicIcon} aria-hidden="true">
                    <Icon size={16} />
                  </span>
                  <span className={styles.topicName}>{topic}</span>
                  {following && <span className={styles.following}>Following</span>}
                </a>
              </li>
            )
          })}
        </ul>
      </section>

      <div className={styles.profile}>
        <span className={styles.profileAvatar} aria-hidden="true">
          {user.initials}
        </span>
        <span className={styles.profileText}>
          <span className={styles.profileName}>{user.name}</span>
          <span className={styles.profileHandle}>@{user.username}</span>
        </span>
        <button type="button" className={styles.iconButton} aria-label="Settings">
          <Settings size={20} aria-hidden="true" />
        </button>
      </div>
    </aside>
  )
}
