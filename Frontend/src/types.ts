export type Topic =
  | 'Technology'
  | 'Sports'
  | 'Politics'
  | 'Entertainment'
  | 'Science'
  | 'World'
  | 'Business'

export type FeedReason = 'forYou' | 'dontMiss'

export type Story = {
  id: string
  publisher: { name: string; initials: string; verified: boolean }
  author: string
  publishedAgo: string // "2h ago"
  topic: Topic
  location?: string // "Eindhoven"
  feedReason: FeedReason
  whyPicked: string
  image: { src: string; alt: string }
  title: string
  summary: string
  why: { heading: string; points: { keyword: string; text: string }[]; background: string }
  aiNote: { sourceCount: number; uncertainty: string }
  readMore: {
    url: string
    readTime: string
    perspectives: { publisher: string; angle: string; url: string }[]
  }
}

export type User = {
  firstName: string
  name: string
  username: string
  initials: string
  followedTopics: Topic[]
}
