/*
 * localStorage / sessionStorage can throw (private mode, blocked cookies),
 * so every read and write is wrapped. The app keeps working without them.
 *   'local'   – remembered until the user clears site data
 *   'session' – remembered until the browser tab is closed
 */
type Area = 'local' | 'session'

function getArea(area: Area) {
  return area === 'local' ? window.localStorage : window.sessionStorage
}

export function readStorage(key: string, area: Area = 'local'): string | null {
  try {
    return getArea(area).getItem(key)
  } catch {
    return null
  }
}

export function writeStorage(key: string, value: string, area: Area = 'local') {
  try {
    getArea(area).setItem(key, value)
  } catch {
    // Ignore: the setting just won't be remembered.
  }
}
