import { Search } from 'lucide-react'
import styles from './Navigation.module.css'

export function SearchField({ id }: { id: string }) {
  return (
    <form className={styles.search} role="search" onSubmit={(event) => event.preventDefault()}>
      <label htmlFor={id} className="sr-only">
        Search news
      </label>
      <Search size={18} className={styles.searchIcon} aria-hidden="true" />
      <input id={id} type="search" className={styles.searchInput} placeholder="Search" autoComplete="off" />
    </form>
  )
}
