import { useEffect, useState } from 'react'
import type { Session } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'
import { useHash } from './useHash'

/** Keep authentication alive on both the feed and the login page. */
export function useAuth() {
  const [session, setSession] = useState<Session | null>(null)
  const [checkingSession, setCheckingSession] = useState(true)
  const [backendStatus, setBackendStatus] = useState('')
  const [signingOut, setSigningOut] = useState(false)
  const [readyToken, setReadyToken] = useState<string | null>(null)
  const hash = useHash()

  useEffect(() => {
    if (hash === '#login' && session && readyToken === session.access_token) {
      window.location.hash = ''
    }
  }, [hash, session, readyToken])

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, next) => {
      setSession(next)
      setCheckingSession(false)
    })
    return () => subscription.unsubscribe()
  }, [])

  useEffect(() => {
    if (!session) {
      setBackendStatus('')
      setReadyToken(null)
      return
    }
    const controller = new AbortController()
    const timeout = window.setTimeout(() => controller.abort(), 15000)
    let active = true
    const token = session.access_token

    async function bootstrap() {
      setBackendStatus('Finishing sign-in…')
      try {
        const apiUrl = import.meta.env.VITE_API_BASE_URL?.trim()
        if (!apiUrl) throw new Error('Missing API URL')
        const response = await fetch(`${apiUrl.replace(/\/$/, '')}/users/me/bootstrap`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
          signal: controller.signal,
        })
        if (!response.ok) throw new Error('Profile request failed')
        const profile = await response.json()
        if (typeof profile.id !== 'string') throw new Error('Invalid profile')
        if (active) {
          setBackendStatus('')
          setReadyToken(token)
          if (window.location.hash === '#login') window.location.hash = ''
          // The SDK has exchanged the OAuth code before emitting the session.
          const url = new URL(window.location.href)
          if (url.searchParams.has('code')) {
            url.searchParams.delete('code')
            window.history.replaceState(null, '', url)
          }
        }
      } catch {
        if (active) setBackendStatus('We could not finish signing you in. Please refresh to try again.')
      } finally {
        window.clearTimeout(timeout)
      }
    }
    void bootstrap()
    return () => {
      active = false
      window.clearTimeout(timeout)
      controller.abort()
    }
  }, [session])

  async function signOut() {
    setSigningOut(true)
    try {
      const { error } = await supabase.auth.signOut({ scope: 'local' })
      if (error) throw error
      setSession(null)
      setBackendStatus('')
      window.location.hash = ''
    } catch {
      setBackendStatus('Could not sign out. Please try again.')
    } finally {
      setSigningOut(false)
    }
  }

  return { session, checkingSession, backendStatus, signingOut, signOut }
}
