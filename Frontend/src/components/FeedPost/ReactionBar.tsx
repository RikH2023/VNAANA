import { useState } from 'react'
import type { FormEvent, ReactNode } from 'react'
import { Bookmark, Check, EyeOff, Heart, SendHorizontal, Share2, Sparkles, ThumbsDown, ThumbsUp } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { usePost } from './PostContext'
import styles from './ReactionBar.module.css'

export type ActionKind = 'like' | 'dislike' | 'notInterested' | 'share' | 'save'
type ButtonVariant = 'icon' | 'labelled' | 'floating'
type LikeIcon = 'thumb' | 'heart'

type ActionButtonProps = {
  kind: ActionKind
  variant?: ButtonVariant
  /** Thumbs-up (default) or a heart for the like button */
  likeIcon?: LikeIcon
}

/* One reaction button. Reads its state from the post, so it can be placed anywhere. */
export function ActionButton({ kind, variant = 'icon', likeIcon = 'thumb' }: ActionButtonProps) {
  const { actions } = usePost()

  const config: Record<ActionKind, { label: string; Icon: LucideIcon; onClick: () => void; pressed?: boolean }> = {
    like: {
      label: 'Like',
      Icon: likeIcon === 'heart' ? Heart : ThumbsUp,
      onClick: actions.toggleLike,
      pressed: actions.liked,
    },
    dislike: { label: 'Dislike', Icon: ThumbsDown, onClick: actions.toggleDislike, pressed: actions.disliked },
    notInterested: { label: variant === 'labelled' ? 'Not for me' : 'Not interested', Icon: EyeOff, onClick: actions.hide },
    share: {
      label: actions.linkCopied ? 'Link copied' : 'Share',
      Icon: actions.linkCopied ? Check : Share2,
      onClick: actions.share,
    },
    save: { label: actions.saved ? 'Saved' : 'Save', Icon: Bookmark, onClick: actions.toggleSave, pressed: actions.saved },
  }
  const { label, Icon, onClick, pressed } = config[kind]
  const showLabel = variant === 'labelled'

  return (
    <button
      type="button"
      className={`${styles.action} ${styles[variant]}`}
      onClick={onClick}
      aria-pressed={pressed}
      aria-label={showLabel ? undefined : kind === 'notInterested' ? 'Not interested – show less like this' : label}
      title={showLabel ? undefined : label}
    >
      <Icon size={20} aria-hidden="true" fill={pressed ? 'currentColor' : 'none'} />
      {showLabel && <span>{label}</span>}
    </button>
  )
}

type AskVariant = 'pill' | 'short' | 'round'

export function AskNovaButton({ variant = 'pill' }: { variant?: AskVariant }) {
  const { actions } = usePost()
  return (
    <button
      type="button"
      className={`${styles.ask} ${styles[`ask_${variant}`]}`}
      onClick={() => actions.askNova()}
      aria-label={variant === 'pill' ? undefined : 'Ask Nova about this story'}
    >
      <Sparkles size={18} aria-hidden="true" />
      {variant === 'pill' && 'Ask Nova'}
      {variant === 'short' && 'Ask'}
    </button>
  )
}

/*
 * Always-visible question field (Split, Anchor-led). Submitting jumps to the
 * chat in part 3 and sends the typed question, or `fallbackQuestion` when empty.
 */
export function AskNovaInput({ placeholder, fallbackQuestion }: { placeholder: string; fallbackQuestion?: string }) {
  const { story, actions } = usePost()
  const [value, setValue] = useState('')
  const inputId = `${story.id}-ask`

  const onSubmit = (event: FormEvent) => {
    event.preventDefault()
    actions.askNova(value.trim() || fallbackQuestion)
    setValue('')
  }

  return (
    <form className={styles.askForm} onSubmit={onSubmit}>
      <label htmlFor={inputId} className="sr-only">
        Start a chat with Nova about this story
      </label>
      <Sparkles size={18} className={styles.askFormIcon} aria-hidden="true" />
      <input
        id={inputId}
        className={styles.askInput}
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder={placeholder}
        autoComplete="off"
      />
      <button type="submit" className={styles.send} aria-label="Start chat with Nova">
        <SendHorizontal size={18} aria-hidden="true" />
      </button>
    </form>
  )
}

type ReactionBarProps = {
  kinds: ActionKind[]
  variant?: ButtonVariant
  likeIcon?: LikeIcon
  ask?: AskVariant | null
  /** Anything to show at the end of the row instead of / next to Ask Nova (e.g. dots). */
  trailing?: ReactNode
  className?: string
}

/* A row (or column, for "floating") of reaction buttons with an optional Ask Nova button. */
export function ReactionBar({ kinds, variant = 'icon', likeIcon, ask = 'pill', trailing, className = '' }: ReactionBarProps) {
  const floating = variant === 'floating'
  return (
    <div className={`${styles.bar} ${floating ? styles.column : ''} ${className}`} role="group" aria-label="Reactions">
      {floating && ask && <AskNovaButton variant={ask} />}
      {kinds.map((kind) => (
        <ActionButton key={kind} kind={kind} variant={variant} likeIcon={likeIcon} />
      ))}
      {(trailing || (!floating && ask)) && (
        <div className={styles.end}>
          {trailing}
          {!floating && ask && <AskNovaButton variant={ask} />}
        </div>
      )}
    </div>
  )
}
