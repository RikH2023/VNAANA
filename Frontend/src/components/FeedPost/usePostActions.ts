import { useState } from 'react'
import type { Story } from '../../types'

type Reaction = 'like' | 'dislike' | null

type Handlers = {
  onHide: () => void
  onOpened: () => void
  /** Opens the Ask Nova chat in the post, optionally sending a question. */
  onAskNova: (question?: string) => void
}

/* Reaction state and handlers for one post. */
export function usePostActions(story: Story, { onHide, onOpened, onAskNova }: Handlers) {
  const [reaction, setReaction] = useState<Reaction>(null)
  const [saved, setSaved] = useState(false)
  const [linkCopied, setLinkCopied] = useState(false)

  // Like and dislike are mutually exclusive: picking one clears the other.
  const toggleReaction = (value: Exclude<Reaction, null>) =>
    setReaction((current) => (current === value ? null : value))

  const share = async () => {
    const url = story.readMore.url
    try {
      if (navigator.share) {
        await navigator.share({ title: story.title, url })
      } else {
        await navigator.clipboard.writeText(url)
        setLinkCopied(true)
        setTimeout(() => setLinkCopied(false), 2000)
      }
    } catch {
      // The user cancelled the share sheet, or the clipboard is blocked.
    }
  }

  return {
    liked: reaction === 'like',
    disliked: reaction === 'dislike',
    saved,
    linkCopied,
    toggleLike: () => toggleReaction('like'),
    toggleDislike: () => toggleReaction('dislike'),
    toggleSave: () => setSaved((value) => !value),
    hide: onHide,
    share,
    markOpened: onOpened,
    askNova: onAskNova,
  }
}

export type PostActions = ReturnType<typeof usePostActions>
