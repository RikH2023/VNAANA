/*
 * Ask Nova – MOCK version.
 * There is no AI behind this yet. Answers are built from the story data
 * after a short delay, so the UI can be designed and tested.
 * Swap the body of `askNova` for a real API call later; the UI only
 * depends on the `NovaAnswer` shape.
 */
import { findStory } from '../data/sampleStories'

export type NovaAnswer = {
  text: string
  sources: string[]
  uncertainty: string
}

export const SUGGESTED_QUESTIONS = [
  'Explain it simpler',
  'What led to this?',
  'What happens next?',
] as const

const FAKE_DELAY_MS = 900

function firstSentence(text: string) {
  return text.split(/(?<=\.)\s/)[0]
}

function lastSentence(text: string) {
  const sentences = text.split(/(?<=\.)\s/)
  return sentences[sentences.length - 1]
}

export async function askNova(storyId: string, question: string): Promise<NovaAnswer> {
  await new Promise((resolve) => setTimeout(resolve, FAKE_DELAY_MS))

  const story = findStory(storyId)
  if (!story) throw new Error(`Unknown story: ${storyId}`)

  const q = question.toLowerCase()
  const [firstPoint] = story.why.points
  let text: string

  if (q.includes('simple')) {
    text = `In short: ${firstSentence(story.summary)} ${firstPoint.text}`
  } else if (q.includes('led to') || q.includes('why')) {
    text = `Some background: ${story.why.background} That is part of why this is news now.`
  } else if (q.includes('next')) {
    text = `Nothing is final yet. Based on the reporting so far: ${lastSentence(story.summary)}`
  } else if (q.includes('for me')) {
    text = `${story.whyPicked} The most direct effect: ${firstPoint.text}`
  } else {
    text = `Here is what the sources agree on: ${story.why.points
      .map((point) => `${point.keyword} – ${point.text}`)
      .join(' ')}`
  }

  return {
    text,
    sources: [story.publisher.name, ...story.readMore.perspectives.map((p) => p.publisher)],
    uncertainty: story.aiNote.uncertainty,
  }
}
