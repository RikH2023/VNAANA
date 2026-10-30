import { useRef, useState } from 'react'
import { askNova } from '../lib/nova'
import type { NovaAnswer } from '../lib/nova'

export type ChatMessage =
  | { id: number; from: 'user'; text: string }
  | { id: number; from: 'nova'; answer: NovaAnswer }
  | { id: number; from: 'nova'; error: string }

/* The Ask Nova conversation for one post. Lives in FeedPost. */
export function useNovaChat(storyId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [pending, setPending] = useState(false)
  const nextId = useRef(0)

  const send = async (question: string) => {
    const text = question.trim()
    if (!text || pending) return
    setMessages((list) => [...list, { id: nextId.current++, from: 'user', text }])
    setPending(true)
    try {
      const answer = await askNova(storyId, text)
      setMessages((list) => [...list, { id: nextId.current++, from: 'nova', answer }])
    } catch {
      setMessages((list) => [
        ...list,
        { id: nextId.current++, from: 'nova', error: 'Nova couldn’t answer that right now.' },
      ])
    } finally {
      setPending(false)
    }
  }

  return { messages, pending, send }
}

export type NovaChat = ReturnType<typeof useNovaChat>
