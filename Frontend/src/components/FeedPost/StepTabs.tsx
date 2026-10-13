import { useRef } from 'react'
import type { KeyboardEvent } from 'react'
import { PART_LABELS, usePost } from './PostContext'
import styles from './StepTabs.module.css'

/* "1 What happened / 2 Why it matters / 3 Read more" under the carousel. */
export function StepTabs() {
  const { story, carousel, partIds } = usePost()
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([])

  // Arrow keys move between tabs (standard ARIA tabs behaviour).
  const onKeyDown = (event: KeyboardEvent) => {
    const step = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0
    if (!step) return
    event.preventDefault()
    const next = (carousel.index + step + carousel.count) % carousel.count
    carousel.goTo(next)
    tabRefs.current[next]?.focus()
  }

  return (
    <div className={styles.tabs} role="tablist" aria-label={`Parts of: ${story.title}`} onKeyDown={onKeyDown}>
      {PART_LABELS.map((label, i) => {
        const selected = i === carousel.index
        return (
          <button
            key={label}
            ref={(el) => {
              tabRefs.current[i] = el
            }}
            type="button"
            role="tab"
            className={styles.tab}
            aria-selected={selected}
            aria-controls={partIds[i]}
            tabIndex={selected ? 0 : -1}
            onClick={() => carousel.goTo(i)}
          >
            <span className={styles.number}>{i + 1}</span>
            {label}
          </button>
        )
      })}
    </div>
  )
}
