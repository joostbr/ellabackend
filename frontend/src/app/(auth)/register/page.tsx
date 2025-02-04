'use client'

import { FormEvent, useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { hashPassword } from '@/lib/auth'
import Link from 'next/link'

// Password requirements
const MIN_PASSWORD_LENGTH = 8

export default function RegisterPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState('')

  function validatePassword(): string | null {
    if (password.length < MIN_PASSWORD_LENGTH) {
      return `Password must be at least ${MIN_PASSWORD_LENGTH} characters long`
    }
    if (password !== confirmPassword) {
      return 'Passwords do not match'
    }
    return null
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setError('')

    // Validate password
    const passwordError = validatePassword()
    if (passwordError) {
      setError(passwordError)
      return
    }
    
    try {
      // First check if email already exists
      const { data: existingUser } = await supabase
        .from('users')
        .select('id')
        .eq('email', email)
        .single()

      if (existingUser) {
        setError('This email is already registered. Please use a different email or login.')
        return
      }

      // If email doesn't exist, proceed with registration
      const { error: insertError } = await supabase
        .from('users')
        .insert([
          {
            email,
            password_hash: await hashPassword(password),
            name
          }
        ])
        .select()
        .single()

      if (insertError) {
        console.error('Registration error:', insertError)
        setError('Failed to create account. Please try again.')
        return
      }

      // Redirect to login page after successful registration
      router.push('/login?registered=true')
    } catch (error) {
      console.error('Registration error:', error)
      setError('Something went wrong. Please try again.')
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <h1>Register</h1>
        {error && (
          <p style={{ color: 'red' }}>
            {error}
            {error.includes('already registered') && (
              <> <Link href="/login">Login here</Link></>
            )}
          </p>
        )}
        <div>
          <label htmlFor="name">Name</label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
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
            minLength={MIN_PASSWORD_LENGTH}
            required
          />
          <small>Password must be at least {MIN_PASSWORD_LENGTH} characters long</small>
        </div>
        <div>
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            id="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            minLength={MIN_PASSWORD_LENGTH}
            required
          />
        </div>
        <button type="submit">Register</button>
        <p>
          Already have an account? <Link href="/login">Login here</Link>
        </p>
      </form>
    </div>
  )
}
