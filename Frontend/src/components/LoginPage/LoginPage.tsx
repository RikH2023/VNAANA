import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { ArrowLeft, Eye, EyeOff } from 'lucide-react'
import { Logo } from '../Navigation/Logo'
import styles from './LoginPage.module.css'
import { supabase } from '../../lib/supabase'
import type { Session } from '@supabase/supabase-js'

type Errors = { email?: string; password?: string }

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validate(email: string, password: string): Errors {
  const errors: Errors = {}
  if (!email.trim()) errors.email = 'Enter your email address.'
  else if (!EMAIL_PATTERN.test(email.trim())) errors.email = 'Enter an email address like name@example.com.'
  if (!password) errors.password = 'Enter your password.'
  return errors
}

/* Google's "G", as used on "Continue with Google" buttons */
function GoogleIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 48 48" aria-hidden="true">
      <path
        fill="#EA4335"
        d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
      />
      <path
        fill="#4285F4"
        d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
      />
      <path
        fill="#FBBC05"
        d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"
      />
      <path
        fill="#34A853"
        d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
      />
    </svg>
  )
}

/*
 * Google sign-in uses Supabase and initializes the verified backend profile.
 * Email/password login remains a design preview.
 */
export function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [errors, setErrors] = useState<Errors>({})
  const [notice, setNotice] = useState('')
  const headingRef = useRef<HTMLHeadingElement>(null)
  const emailRef = useRef<HTMLInputElement>(null)
  const passwordRef = useRef<HTMLInputElement>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [checkingSession, setCheckingSession] = useState(true)
  const [backendStatus, setBackendStatus] = useState('')
  const [signingOut, setSigningOut] = useState(false)
  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, nextSession) => {
        setSession(nextSession)
        setCheckingSession(false)
      },
    )

    return () => {
      subscription.unsubscribe()
    }
  }, [])
  useEffect(() => {
    if (!session) {
      setBackendStatus('')
      return
    }

    const controller = new AbortController()
    const accessToken = session.access_token

    async function verifyBackend() {
      const apiUrl = import.meta.env.VITE_API_BASE_URL?.trim()

      if (!apiUrl) {
        setBackendStatus('Missing backend URL configuration.')
        return
      }

      setBackendStatus('Preparing your application profile…')

      try {
        const response = await fetch(
          `${apiUrl.replace(/\/$/, '')}/users/me/bootstrap`,
          {
            method: 'POST',
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
            signal: controller.signal,
          },
        )

        if (!response.ok) {
          throw new Error(`Backend returned HTTP ${response.status}`)
        }

        const profile = await response.json()

        if (typeof profile.id !== 'string') {
          throw new Error('Backend returned an unexpected profile')
        }

        if (!controller.signal.aborted) {
          setBackendStatus(
            `Your application profile is ready. User ID: ${profile.id}`,
          )
        }

      } catch {
        if (!controller.signal.aborted) {
          setBackendStatus(
            'Could not prepare your application profile. Check FastAPI and the bootstrap request.',
          )
        }
      }
    }

    void verifyBackend()

    return () => controller.abort()
  }, [session])

  const onSubmit = (event: FormEvent) => {
    event.preventDefault()
    const found = validate(email, password)
    setErrors(found)
    if (found.email) emailRef.current?.focus()
    else if (found.password) passwordRef.current?.focus()
    else setNotice('Logging in isn’t connected yet. This page is a design preview.')
  }

  const onGoogle = async () => {
    setNotice('Opening Google sign-in…')

    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/`,
        },
      })

      if (error) throw error
    } catch {
      setNotice('Could not start Google sign-in. Please try again.')
    }
  }

  const onSignOut = async () => {
    setSigningOut(true)
    try {
      const { error } = await supabase.auth.signOut({ scope: 'local' })
      if (error) throw error
      setSession(null)
      setBackendStatus('')
      setPassword('')
      setNotice('Signed out on this browser.')
    } catch {
      setNotice('Could not sign out. Please try again.')
    } finally {
      setSigningOut(false)
    }
  }

  return (
    <div className={styles.page}>
      <header className={styles.top}>
        <Logo />
        <a href="#" className={styles.back}>
          <ArrowLeft size={18} aria-hidden="true" />
          Back to feed
        </a>
      </header>

      <main className={styles.main}>
        <div className={styles.card}>
          <h1 ref={headingRef} className={styles.title} tabIndex={-1}>
            Log in
          </h1>
          <p className={styles.intro}>Welcome back. Your morning briefing is waiting.</p>
            <p className={styles.notice} role="status">
            {checkingSession
              ? 'Checking your session…'
              : session
                ? `Signed in as ${session.user.email ?? 'a Supabase user'}`
                : 'You are not signed in.'}
          </p>
            <p className={styles.notice} role="status">
              {backendStatus}
             </p>
          <form className={styles.form} onSubmit={onSubmit} noValidate>
            <div className={styles.field}>
              <label htmlFor="login-email" className={styles.label}>
                Email
              </label>
              <input
                ref={emailRef}
                id="login-email"
                className={styles.input}
                type="email"
                autoComplete="email"
                inputMode="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                aria-invalid={errors.email ? true : undefined}
                aria-describedby={errors.email ? 'login-email-error' : undefined}
              />
              {errors.email && (
                <p id="login-email-error" className={styles.error}>
                  {errors.email}
                </p>
              )}
            </div>

            <div className={styles.field}>
              <div className={styles.labelRow}>
                <label htmlFor="login-password" className={styles.label}>
                  Password
                </label>
                <a href="#forgot-password" className={styles.smallLink}>
                  Forgot password?
                </a>
              </div>
              <div className={styles.passwordWrap}>
                <input
                  ref={passwordRef}
                  id="login-password"
                  className={styles.input}
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  aria-invalid={errors.password ? true : undefined}
                  aria-describedby={errors.password ? 'login-password-error' : undefined}
                />
                <button
                  type="button"
                  className={styles.reveal}
                  onClick={() => setShowPassword((value) => !value)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  aria-pressed={showPassword}
                >
                  {/* The icon shows the current state: crossed-out eye while the password is hidden */}
                  {showPassword ? <Eye size={20} aria-hidden="true" /> : <EyeOff size={20} aria-hidden="true" />}
                </button>
              </div>
              {errors.password && (
                <p id="login-password-error" className={styles.error}>
                  {errors.password}
                </p>
              )}
            </div>

            <button type="submit" className={styles.submit}>
              Log in
            </button>
          </form>

          <p className={styles.divider}>
            <span>or</span>
          </p>

          {session ? (
            <button type="button" className={styles.google} onClick={onSignOut} disabled={signingOut}>
              {signingOut ? 'Signing out…' : 'Sign out'}
            </button>
          ) : (
            <button type="button" className={styles.google} onClick={onGoogle} disabled={checkingSession}>
              <GoogleIcon />
              Continue with Google
            </button>
          )}

          <p className={styles.notice} role="status">
            {notice}
          </p>

          <p className={styles.signUp}>
            New to Virtual News Anchor?{' '}
            <a href="#sign-up" className={styles.smallLink}>
              Create an account
            </a>
          </p>
        </div>
      </main>
    </div>
  )
}
