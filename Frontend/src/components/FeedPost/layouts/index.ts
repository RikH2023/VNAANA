import type { ComponentType } from 'react'
import { AnchorLedLayout } from './AnchorLed'
import { HeadlineFirstLayout } from './HeadlineFirst'
import { ImageFirstLayout } from './ImageFirst'
import { InstagramStyleLayout } from './InstagramStyle'
import { PeekLayout } from './Peek'
import { PosterLayout } from './Poster'
import { SplitLayout } from './Split'

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
  imageFirst: { label: 'Image first', component: ImageFirstLayout },
  headlineFirst: { label: 'Headline first', component: HeadlineFirstLayout },
  poster: { label: 'Poster', component: PosterLayout },
  split: { label: 'Split', component: SplitLayout, wide: true },
  peek: { label: 'Peek', component: PeekLayout },
  anchorLed: { label: 'Anchor-led', component: AnchorLedLayout },
} satisfies Record<string, PostLayout>

export type PostLayoutKey = keyof typeof POST_LAYOUTS

export const DEFAULT_LAYOUT: PostLayoutKey = 'instagramStyle'

export function isPostLayoutKey(value: unknown): value is PostLayoutKey {
  return typeof value === 'string' && value in POST_LAYOUTS
}

export function isWideLayout(key: PostLayoutKey) {
  return (POST_LAYOUTS[key] as PostLayout).wide === true
}
