import { useCallback, useRef, useState } from 'react'
import type { KeyboardEvent, TouchEvent } from 'react'

const SWIPE_MIN_PX = 40

/*
 * State for the 3-part story carousel.
 * One instance lives in FeedPost, so every piece of the post shares the same current part.
 */
export function useCarousel(count: number) {
  const [index, setIndex] = useState(0)
  const touchStart = useRef<{ x: number; y: number } | null>(null)

  const goTo = useCallback(
    (next: number) => setIndex(Math.max(0, Math.min(count - 1, next))),
    [count],
  )
  const next = useCallback(() => goTo(index + 1), [goTo, index])
  const prev = useCallback(() => goTo(index - 1), [goTo, index])

  const onKeyDown = (event: KeyboardEvent) => {
    const target = event.target as HTMLElement
    if (target.closest('input, textarea, [role="tablist"]')) return
    if (event.key === 'ArrowRight') {
      event.preventDefault()
      next()
    } else if (event.key === 'ArrowLeft') {
      event.preventDefault()
      prev()
    }
  }

  const onTouchStart = (event: TouchEvent) => {
    const touch = event.touches[0]
    touchStart.current = { x: touch.clientX, y: touch.clientY }
  }

  const onTouchEnd = (event: TouchEvent) => {
    const start = touchStart.current
    touchStart.current = null
    if (!start) return
    const touch = event.changedTouches[0]
    const dx = touch.clientX - start.x
    const dy = touch.clientY - start.y
    // Only count clearly horizontal swipes, so vertical scrolling still works.
    if (Math.abs(dx) < SWIPE_MIN_PX || Math.abs(dx) < Math.abs(dy)) return
    if (dx < 0) next()
    else prev()
  }

  return {
    index,
    count,
    goTo,
    next,
    prev,
    isFirst: index === 0,
    isLast: index === count - 1,
    keyHandlers: { onKeyDown },
    swipeHandlers: { onTouchStart, onTouchEnd },
  }
}

export type Carousel = ReturnType<typeof useCarousel>
