import { useEffect, useRef } from 'react'
import { ExternalLink, Info } from 'lucide-react'
import { NovaChatLog, NovaComposer } from '../NovaChat'
import { usePost } from '../PostContext'
import styles from './Parts.module.css'

/* The three parts of a story. FeedPost puts these inside a carousel. */

function StoryImage({ className = '' }: { className?: string }) {
  const { story } = usePost()
  return (
    <img
      className={`${styles.image} ${className}`}
      src={story.image.src}
      alt={story.image.alt}
      width={1200}
      height={800}
      draggable={false}
    />
  )
}

/* Part 1: headline and summary, then the image. They swipe away as one. */
export function WhatHappenedPart() {
  const { story, titleId } = usePost()
  return (
    <div className={styles.whatHappened}>
      <div className={styles.leadText}>
        <h2 id={titleId} className={styles.headline}>
          {story.title}
        </h2>
        <p className={styles.summary}>{story.summary}</p>
      </div>
      <StoryImage className={styles.leadImage} />
    </div>
  )
}

export function WhyPart() {
  const { story } = usePost()
  const { why, aiNote } = story
  return (
    <div className={styles.part}>
      <p className={styles.eyebrow}>Why it matters</p>
      <h3 className={styles.heading}>{why.heading}</h3>
      <ol className={styles.points}>
        {why.points.map((point, i) => (
          <li key={point.keyword} className={styles.point}>
            <span className={styles.number} aria-hidden="true">
              {i + 1}
            </span>
            <p>
              <strong>{point.keyword}.</strong> {point.text}
            </p>
          </li>
        ))}
      </ol>
      <p className={styles.background}>
        <strong>Background:</strong> {why.background}
      </p>
      <p className={styles.aiNote}>
        <Info size={16} aria-hidden="true" />
        <span>
          AI summary from {aiNote.sourceCount} sources · {aiNote.uncertainty}
        </span>
      </p>
    </div>
  )
}

/* Part 3: the original source, other perspectives, and the Ask Nova chat. */
export function ReadMorePart() {
  const { story, actions, chat } = usePost()
  const { readMore } = story
  const scrollRef = useRef<HTMLDivElement>(null)

  // Keep the newest chat message in view
  useEffect(() => {
    const area = scrollRef.current
    if (area && chat.messages.length > 0) area.scrollTo({ top: area.scrollHeight, behavior: 'smooth' })
  }, [chat.messages.length, chat.pending])

  return (
    <div className={`${styles.part} ${styles.readMore}`}>
      {/* Everything above the chat input scrolls; the input stays pinned at the bottom */}
      <div ref={scrollRef} className={styles.readMoreScroll}>
        <a
          className={styles.sourceCard}
          href={readMore.url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={actions.markOpened}
        >
          <span className={styles.sourceLabel}>Full story on {story.publisher.name}</span>
          <span className={styles.sourceTitle}>{story.title}</span>
          <span className={styles.sourceMeta}>
            {readMore.readTime}
            <ExternalLink size={15} aria-hidden="true" />
            <span className="sr-only">(opens in a new tab)</span>
          </span>
        </a>

        <h3 className={styles.subhead}>Other perspectives</h3>
        <ul className={styles.perspectives}>
          {readMore.perspectives.map((perspective) => (
            <li key={perspective.url}>
              <a className={styles.perspective} href={perspective.url} target="_blank" rel="noopener noreferrer">
                <span>
                  <span className={styles.perspectivePublisher}>{perspective.publisher}</span>
                  <span className={styles.perspectiveAngle}>{perspective.angle}</span>
                </span>
                <ExternalLink size={15} aria-hidden="true" />
                <span className="sr-only">(opens in a new tab)</span>
              </a>
            </li>
          ))}
        </ul>

        <h3 className={styles.subhead}>Still curious? Ask Nova</h3>
        <NovaChatLog />
      </div>
      <NovaComposer />
    </div>
  )
}
