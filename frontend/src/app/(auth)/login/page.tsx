'use client'

import { signIn } from 'next-auth/react'
import { FormEvent, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'

export default function LoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  // Check if user just registered
  const justRegistered = searchParams.get('registered') === 'true'

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    
    try {
      const result = await signIn('credentials', {
        email,
        password,
        redirect: false,
      })

      if (result?.error) {
        setError('Invalid credentials')
      } else {
        router.push('/dashboard')
        router.refresh()
      }
    } catch (error) {
      setError('Something went wrong')
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <h1>Login</h1>
        {justRegistered && (
          <p style={{ color: 'green' }}>
            Registration successful! Please log in.
          </p>
        )}
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <div>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Log in</button>
        <p>
          Don't have an account?{' '}
          <Link href="/register">Register here</Link>
        </p>
      </form>
    </div>
  )
}
