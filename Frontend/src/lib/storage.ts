type StorageKind = 'local' | 'session'

/** Optional UI preferences must not break rendering when storage is unavailable. */
export function readStorage(key: string, kind: StorageKind = 'local'): string | null {
  try {
    if (typeof window === 'undefined') return null
    const storage = kind === 'session' ? window.sessionStorage : window.localStorage
    return storage.getItem(key)
  } catch {
    return null
  }
}

export function writeStorage(
  key: string,
  value: string,
  kind: StorageKind = 'local',
): void {
  try {
    if (typeof window === 'undefined') return
    const storage = kind === 'session' ? window.sessionStorage : window.localStorage
    storage.setItem(key, value)
  } catch {
    // Keep the in-memory UI state when storage is blocked or full.
  }
}
