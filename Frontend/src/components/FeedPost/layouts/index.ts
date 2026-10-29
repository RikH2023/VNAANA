import type { ComponentType } from 'react'
import { FlipbookLayout } from './Flipbook'
import { HeadlineFirstLayout } from './HeadlineFirst'
import { InstagramStyleLayout } from './InstagramStyle'
import { PosterLayout } from './Poster'

type PostLayout = {
  /** Name shown in the layout switcher */
  label: string
  component: ComponentType
  /** Widen the feed column to --feed-w-wide (960px) */
  wide?: boolean
}

/*
 * All post layouts, in the order the switcher shows them.
 * To add one: create <Name>.tsx in this folder and add it here.
 */
export const POST_LAYOUTS = {
  instagramStyle: { label: 'Instagram Style', component: InstagramStyleLayout },
  headlineFirst: { label: 'Headline first', component: HeadlineFirstLayout },
  poster: { label: 'Poster', component: PosterLayout },
  flipbook: { label: 'Flipbook', component: FlipbookLayout, wide: true },
} satisfies Record<string, PostLayout>

export type PostLayoutKey = keyof typeof POST_LAYOUTS

export const DEFAULT_LAYOUT: PostLayoutKey = 'instagramStyle'

export function isPostLayoutKey(value: unknown): value is PostLayoutKey {
  return typeof value === 'string' && value in POST_LAYOUTS
}

export function isWideLayout(key: PostLayoutKey) {
  return (POST_LAYOUTS[key] as PostLayout).wide === true
}
