'use client'

import { signIn } from 'next-auth/react'
import { FormEvent, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { FiMail, FiLock, FiAlertCircle } from 'react-icons/fi'

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
    <div className="min-h-screen flex items-center justify-center px-4" style={{ background: '#333b6a' }}>
      <div className="bg-white/10 backdrop-blur-lg p-10 rounded-2xl w-full max-w-md space-y-10 shadow-2xl">
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold tracking-tight" style={{ color: '#b7feae' }}>
            Ella
          </h1>
          <p className="text-xl text-gray-300 font-light">
            Sign in to your account
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {justRegistered && (
            <div className="bg-green-900/50 text-green-300 p-4 rounded-xl flex items-center">
              <FiAlertCircle className="h-5 w-5 mr-3 flex-shrink-0" />
              <p className="text-sm font-medium">Registration successful! Please log in.</p>
            </div>
          )}

          {error && (
            <div className="bg-red-900/50 text-red-300 p-4 rounded-xl flex items-center">
              <FiAlertCircle className="h-5 w-5 mr-3 flex-shrink-0" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          )}

          <div className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="email" className="block text-sm font-medium text-gray-300">
                Email
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
                  required
                  className="block w-full pl-11 pr-4 py-3 rounded-xl bg-black/20 border border-gray-600 text-gray-100 placeholder-gray-400 focus:outline-none focus:border-[#b7feae] focus:ring-1 focus:ring-[#b7feae] transition-all"
                  placeholder="Enter your password"
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-3 px-4 rounded-xl font-semibold text-lg transition-all hover:opacity-90 hover:shadow-lg"
            style={{ 
              backgroundColor: '#b7feae',
              color: '#333b6a',
            }}
          >
            Sign in
          </button>

          <p className="text-center text-gray-300 pt-4">
            Don't have an account?{' '}
            <Link 
              href="/register" 
              className="font-medium hover:underline transition-colors"
              style={{ color: '#b7feae' }}
            >
              Register here
            </Link>
          </p>
        </form>
      </div>
    </div>
  )
}
