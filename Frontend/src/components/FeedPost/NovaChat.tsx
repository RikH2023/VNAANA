import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { Info, SendHorizontal } from 'lucide-react'
import { usePost } from './PostContext'
import { SuggestionChips } from './SuggestionChips'
import styles from './NovaChat.module.css'

/*
 * Ask Nova inside the post (part 3, "Read more").
 * NovaChatLog shows the conversation; NovaComposer is the chips + input bar
 * pinned to the bottom of the part.
 */

export function NovaChatLog() {
  const { story, chat } = usePost()

  return (
    <div className={styles.log} role="log" aria-live="polite" aria-label="Conversation with Nova">
      {chat.messages.length === 0 && (
        <p className={styles.intro}>
          Nova answers from {story.aiNote.sourceCount} sources and tells you what isn’t confirmed yet.
          <span className={styles.prototype}> Prototype: answers are pre-written, not live AI.</span>
        </p>
      )}
      {chat.messages.map((message) =>
        message.from === 'user' ? (
          <p key={message.id} className={styles.user}>
            <span className="sr-only">You asked: </span>
            {message.text}
          </p>
        ) : 'error' in message ? (
          <p key={message.id} className={styles.nova}>
            {message.error}
          </p>
        ) : (
          <div key={message.id} className={styles.nova}>
            <span className="sr-only">Nova answered: </span>
            <p>{message.answer.text}</p>
            <p className={styles.sources}>
              <strong>Sources:</strong> {message.answer.sources.join(', ')}
            </p>
            <p className={styles.uncertain}>
              <Info size={14} aria-hidden="true" />
              <span>
                <strong>Not certain:</strong> {message.answer.uncertainty}
              </span>
            </p>
          </div>
        ),
      )}
      {chat.pending && (
        <p className={styles.typing}>
          <span className={styles.typingDots} aria-hidden="true">
            <span />
            <span />
            <span />
          </span>
          Nova is checking the sources…
        </p>
      )}
    </div>
  )
}

export function NovaComposer() {
  const { story, chat, composerFocusRequest } = usePost()
  const [draft, setDraft] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const inputId = `${story.id}-nova-input`

  // An Ask Nova button elsewhere in the post asked for the input to be focused.
  // preventScroll stops the browser from scrolling the carousel or the feed.
  useEffect(() => {
    if (composerFocusRequest > 0) inputRef.current?.focus({ preventScroll: true })
  }, [composerFocusRequest])

  const onSubmit = (event: FormEvent) => {
    event.preventDefault()
    void chat.send(draft)
    setDraft('')
  }

  return (
    <div className={styles.composer}>
      <SuggestionChips onPick={(question) => void chat.send(question)} tone="row" />
      <form className={styles.form} onSubmit={onSubmit}>
        <label htmlFor={inputId} className="sr-only">
          Ask Nova about this story
        </label>
        <input
          ref={inputRef}
          id={inputId}
          className={styles.input}
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Ask Nova anything…"
          autoComplete="off"
        />
        <button type="submit" className={styles.send} aria-label="Send question to Nova" disabled={chat.pending}>
          <SendHorizontal size={18} aria-hidden="true" />
        </button>
      </form>
    </div>
  )
}
