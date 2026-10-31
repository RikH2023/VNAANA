import { SUGGESTED_QUESTIONS } from '../../utils/nova'
import styles from './SuggestionChips.module.css'

/* Quick questions for Nova. "row" keeps them on one line that scrolls sideways. */
export function SuggestionChips({ onPick, tone = 'wrap' }: { onPick: (question: string) => void; tone?: 'wrap' | 'row' }) {
  return (
    <ul className={`${styles.chips} ${styles[tone]}`} aria-label="Suggested questions">
      {SUGGESTED_QUESTIONS.map((question) => (
        <li key={question}>
          <button type="button" className={styles.chip} onClick={() => onPick(question)}>
            {question}
          </button>
        </li>
      ))}
    </ul>
  )
}
