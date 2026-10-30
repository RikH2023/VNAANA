import { useEffect, useState } from 'react'

/*
 * The current URL hash (e.g. "#login"). The app has no router: pages that
 * replace the feed, like the login page, are picked by the hash.
 */
export function useHash() {
  const [hash, setHash] = useState(() => window.location.hash)

  useEffect(() => {
    const onHashChange = () => setHash(window.location.hash)
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  return hash
}
