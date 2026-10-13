import { createContext, useContext } from 'react'
import type { Carousel } from '../../hooks/useCarousel'
import type { NovaChat } from '../../hooks/useNovaChat'
import type { Story } from '../../types'
import type { PostActions } from './usePostActions'

/*
 * Everything a post layout needs: the story, the shared carousel state,
 * the reaction handlers and the Ask Nova conversation. FeedPost provides it;
 * layouts and their pieces read it with usePost().
 */
export type PostContextValue = {
  story: Story
  carousel: Carousel
  actions: PostActions
  chat: NovaChat
  /** Goes up by one each time an Ask Nova button asks for the chat input to be focused. */
  composerFocusRequest: number
  titleId: string
  partIds: string[]
}

export const PostContext = createContext<PostContextValue | null>(null)

export function usePost() {
  const context = useContext(PostContext)
  if (!context) throw new Error('usePost must be used inside <FeedPost>')
  return context
}

export const PART_LABELS = ['What happened', 'Why it matters', 'Read more'] as const

/** The part that holds "Read more" and the Ask Nova chat. */
export const ASK_NOVA_PART = PART_LABELS.length - 1
