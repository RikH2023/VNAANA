import { useEffect, useRef, useState } from 'react'
import { useCarousel } from '../../hooks/useCarousel'
import { useNovaChat } from '../../hooks/useNovaChat'
import type { Story } from '../../types'
import { POST_LAYOUTS } from './layouts'
import type { PostLayoutKey } from './layouts'
import { ASK_NOVA_PART, PART_LABELS, PostContext } from './PostContext'
import { usePostActions } from './usePostActions'
import styles from './FeedPost.module.css'

type Props = {
  story: Story
  layout: PostLayoutKey
  /** Called when the user opens the story (moves past part 1, reads more or asks Nova). */
  onOpened: (storyId: string) => void
}

/*
 * One news story in the feed. Holds the state (carousel, reactions, Ask Nova
 * chat, hidden) and renders whichever layout is selected. Because the state
 * lives here, switching layouts keeps the current part, likes and the chat.
 */
export function FeedPost({ story, layout, onOpened }: Props) {
  const carousel = useCarousel(PART_LABELS.length)
  const chat = useNovaChat(story.id)
  const [hidden, setHidden] = useState(false)
  const [composerFocusRequest, setComposerFocusRequest] = useState(0)
  const undoRef = useRef<HTMLButtonElement>(null)
  const postRef = useRef<HTMLElement>(null)
  const wasHidden = useRef(false)

  // Every Ask Nova button in the post leads here: go to the chat part,
  // focus its input, and send the question if there is one.
  const askNova = (question?: string) => {
    onOpened(story.id)
    carousel.goTo(ASK_NOVA_PART)
    setComposerFocusRequest((n) => n + 1)
    if (question) void chat.send(question)
  }

  const actions = usePostActions(story, {
    onHide: () => setHidden(true),
    onOpened: () => onOpened(story.id),
    onAskNova: askNova,
  })

  useEffect(() => {
    if (carousel.index > 0) onOpened(story.id)
  }, [carousel.index, onOpened, story.id])

  // Keep keyboard focus in a sensible place when hiding / undoing.
  useEffect(() => {
    if (hidden) undoRef.current?.focus()
    else if (wasHidden.current) postRef.current?.focus()
    wasHidden.current = hidden
  }, [hidden])

  if (hidden) {
    return (
      <article className={styles.hidden} data-hidden="true" aria-label={`Hidden: ${story.title}`}>
        <p>
          <strong>Hidden</strong> · You’ll see fewer stories like this.
        </p>
        <button ref={undoRef} type="button" className={styles.undo} onClick={() => setHidden(false)}>
          Undo
        </button>
      </article>
    )
  }

  const Layout = POST_LAYOUTS[layout].component
  const titleId = `${story.id}-title`
  const partIds = PART_LABELS.map((_, i) => `${story.id}-part-${i + 1}`)

  return (
    <PostContext.Provider value={{ story, carousel, actions, chat, composerFocusRequest, titleId, partIds }}>
      <article ref={postRef} className={styles.post} data-layout={layout} aria-labelledby={titleId} tabIndex={-1}>
        <Layout />
      </article>
    </PostContext.Provider>
  )
}
