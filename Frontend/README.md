# VNAANA – Frontend prototype

The **For You** landing page of the Virtual News Anchor Against News Avoidance (VNAANA).
It uses React, TypeScript and Vite. All data is sample data, and there is no backend or real AI yet.

## Run it

You need Node.js 20 or newer.

```bash
cd Frontend
npm install      # once, and again whenever package.json changes (e.g. after switching branches)
npm run dev      # http://localhost:5173
```

Other scripts:

| Command             | What it does                               |
| ------------------- | ------------------------------------------ |
| `npm run build`     | Type-checks, then builds into `dist/`      |
| `npm run preview`   | Serves the built `dist/` folder            |
| `npm run typecheck` | TypeScript check only                      |
| `npm run lint`      | ESLint                                     |

`node_modules/` and `dist/` are git-ignored. Never commit them.

## Folder structure

```
src/
  main.tsx                 Entry: loads fonts + global CSS
  App.tsx                  Page shell: sidebar / mobile bars, snapping feed
  types.ts                 Story, Topic, User types
  styles/
    tokens.css             ← all design tokens (colours, radii, fonts, sizes)
    global.css             Reset, focus style, .sr-only helper
  data/
    sampleStories.ts       3 fictional stories + sample user
    topics.ts              Topic list and their icons
  lib/
    nova.ts                askNova(storyId, question) – MOCK, swap for a real API later
    storage.ts             Safe localStorage read/write
  hooks/
    useCarousel.ts         Shared 3-part carousel state (keys + swipe)
    useNovaChat.ts         The Ask Nova conversation of one post
  components/
    Navigation/            Sidebar, MobileTopBar, MobileTabBar, Logo, SearchField
    BriefingCard/          Nova's greeting + progress bar (dismissible)
    NovaAvatar/            Nova's face
    FeedPost/              One story – see below
```

### Component tree

```
App
├─ Sidebar                      (≥ 820px)
├─ MobileTopBar / MobileTabBar  (< 820px)
├─ main
│  ├─ BriefingCard
│  └─ FeedPost × 3
│     ├─ PostHeader             (byline, topic + location pills, ⋯ menu with "Not interested")
│     ├─ PostCarousel           (parts: WhatHappenedPart, WhyPart, ReadMorePart)
│     │  ├─ ReadMorePart        └─ NovaChatLog + NovaComposer (the Ask Nova chat)
│     │  └─ CarouselArrows, CounterPill
│     ├─ PartDots               (progress dots)
│     └─ ReactionBar            (ActionButton, AskNovaButton)
```

`FeedPost` owns the state of a post: carousel position, like/dislike/save, the Ask Nova conversation and hidden. It shares that state through `PostContext`, and every piece reads it with `usePost()`.

### Ask Nova lives inside the post

Ask Nova is part 3 of every post ("Read more"). Below the source and the other perspectives, the conversation appears, with the suggestion chips and a chat input pinned to the bottom of the part.

Every Ask Nova button in a post calls `actions.askNova(question?)`. That jumps to part 3, focuses the chat input, and sends the question if one was given.

## Design tokens

All colours, radii, fonts and key sizes live in **`src/styles/tokens.css`** as CSS variables, for example `var(--accent)` or `var(--radius-card)`. Each component has its own `*.module.css` file that uses those variables. Don't hard-code colours.

The fonts are Bricolage Grotesque for headlines and Instrument Sans for everything else. They're self-hosted through `@fontsource` (imported in `main.tsx`), so the app doesn't need to load them from Google.

## The post ("Headline first")

Every post has the same design, built in `FeedPost.tsx`: a top bar (byline, topic and location pills, ⋯ menu), then a 3-part carousel. In part 1 the headline and summary come before the image, and they swipe away together. Below the carousel are the progress dots, then heart / share / Ask Nova.

The title is the `h2` with `id={titleId}`, so the post has an accessible name.

**Sizing:** the carousel height is set with `--parts-h` in `FeedPost.module.css`. Narrow feeds are adjusted with `@container feed (max-width: 520px)`, not a viewport media query.

## Connecting real AI later

The chat (`src/hooks/useNovaChat.ts`) only calls `askNova(storyId, question)` in `src/lib/nova.ts` and expects `{ text, sources, uncertainty }` back. Replace the body of that function with a real API call (through the backend, so no API key ends up in the browser); nothing else needs to change.

## Feed behaviour

- **One post per screen.** The feed (`<main id="feed">` in `App.tsx`) is its own scroll area with `scroll-snap-type: y mandatory`. Every post sits in a full-height slide, and `scroll-snap-stop: always` stops a fast swipe from skipping posts.
- **Phones:** a post is never taller than the screen. When space is short, only the carousel shrinks (`--parts-min` sets how far), and descriptions are limited to 3 lines on screens under 760px tall. On screens under 700px tall, posts keep their natural height and scroll instead.
- **Nova's briefing** can be dismissed with ×. It stays hidden for the browser session (`sessionStorage`), then comes back, like a new morning notification.

## Notes

- All stories, publishers, people and links are **fictional**. Links use the reserved `.example` domain.
- The briefing progress bar has one segment per story in the feed (3 here), not a fixed 5.
- Text parts (Why it matters / Read more) have a fixed height so the feed never jumps. Extra text scrolls inside the part.
