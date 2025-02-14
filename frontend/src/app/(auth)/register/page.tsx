'use client'

import { FormEvent, useState } from 'react'
import { useRouter } from 'next/navigation'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import Link from 'next/link'
import { FiMail, FiLock, FiUser, FiAlertCircle } from 'react-icons/fi'
import { ClipLoader } from 'react-spinners'

// Password requirements
const MIN_PASSWORD_LENGTH = 8

export default function RegisterPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

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
    setIsLoading(true)

    const passwordError = validatePassword()
    if (passwordError) {
      setError(passwordError)
      setIsLoading(false)
      return
    }
    
    try {
      const supabase = createClientComponentClient()
      const { data: authData, error: authError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            name: name,
          },
          emailRedirectTo: `${window.location.origin}/auth/callback`,
        },
      })

      if (authError) {
        console.error('Registration error details:', authError)
        
        if (authError.message.includes('rate limit')) {
          setError('Too many registration attempts. Please wait a few minutes before trying again')
        } else {
          setError(authError.message)
        }
        return
      }

      if (!authData.user?.id) {
        setError('Something went wrong during registration')
        return
      }

      // Redirect to login with a success message
      router.push('/login?registered=true&email=' + encodeURIComponent(email))
    } catch (error) {
      console.error('Registration error:', error)
      setError('Something went wrong. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ background: '#333b6a' }}>
      <div className="bg-white/10 backdrop-blur-lg p-10 rounded-2xl w-full max-w-md space-y-10 shadow-2xl">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <img 
              src="/ella.png" 
              alt="Ella Logo" 
              className="h-16 w-auto"
            />
          </div>
          <p className="text-xl text-gray-300 font-light">
            Create your account
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {error && (
            <div className="bg-red-900/50 text-red-300 p-4 rounded-xl flex items-center">
              <FiAlertCircle className="h-5 w-5 mr-3 flex-shrink-0" />
              <p className="text-sm font-medium">
                {error}
                {error.includes('already registered') && (
                  <> - <Link href="/login" className="underline">Login here</Link></>
                )}
              </p>
            </div>
          )}

          <div className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="name" className="block text-sm font-medium text-gray-300">
                Full Name
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <FiUser className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="block w-full pl-11 pr-4 py-3 rounded-xl bg-black/20 border border-gray-600 text-gray-100 placeholder-gray-400 focus:outline-none focus:border-[#b7feae] focus:ring-1 focus:ring-[#b7feae] transition-all"
                  placeholder="Enter your full name"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="email" className="block text-sm font-medium text-gray-300">
                Email address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <FiMail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="block w-full pl-11 pr-4 py-3 rounded-xl bg-black/20 border border-gray-600 text-gray-100 placeholder-gray-400 focus:outline-none focus:border-[#b7feae] focus:ring-1 focus:ring-[#b7feae] transition-all"
                  placeholder="Enter your email"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="block text-sm font-medium text-gray-300">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <FiLock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  minLength={MIN_PASSWORD_LENGTH}
                  required
                  className="block w-full pl-11 pr-4 py-3 rounded-xl bg-black/20 border border-gray-600 text-gray-100 placeholder-gray-400 focus:outline-none focus:border-[#b7feae] focus:ring-1 focus:ring-[#b7feae] transition-all"
                  placeholder="Create a password"
                />
              </div>
              <p className="text-sm text-gray-400 mt-1">
                Must be at least {MIN_PASSWORD_LENGTH} characters long
              </p>
            </div>

            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300">
                Confirm Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <FiLock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  minLength={MIN_PASSWORD_LENGTH}
                  required
                  className="block w-full pl-11 pr-4 py-3 rounded-xl bg-black/20 border border-gray-600 text-gray-100 placeholder-gray-400 focus:outline-none focus:border-[#b7feae] focus:ring-1 focus:ring-[#b7feae] transition-all"
                  placeholder="Confirm your password"
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3 px-4 rounded-xl font-semibold text-lg transition-all hover:opacity-90 hover:shadow-lg flex items-center justify-center"
            style={{ 
              backgroundColor: '#b7feae',
              color: '#333b6a',
            }}
            disabled={isLoading}
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <ClipLoader size={20} color="#333b6a" />
                <span>Creating account...</span>
              </div>
            ) : (
              'Create account'
            )}
          </button>

          <p className="text-center text-gray-300 pt-4">
            Already have an account?{' '}
            <Link 
              href="/login" 
              className="font-medium hover:underline transition-colors"
              style={{ color: '#b7feae' }}
            >
              Log in here
            </Link>
          </p>
        </form>
      </div>
    </div>
  )
}
