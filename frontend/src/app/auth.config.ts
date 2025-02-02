import type { AuthOptions } from 'next-auth'
import CredentialsProvider from "next-auth/providers/credentials"
import { supabase } from '@/lib/supabase'
import { hashPassword } from '@/lib/auth'

export const authConfig: AuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        try {
          const { data: user, error } = await supabase
            .from('users')
            .select('id, email, name')
            .eq('email', credentials.email)
            .eq('password_hash', hashPassword(credentials.password))
            .single()

          if (error || !user) {
            return null
          }

          return {
            id: user.id,
            email: user.email,
            name: user.name
          }
        } catch (error) {
          console.error('Auth error:', error)
          return null
        }
      }
    })
  ],
  pages: {
    signIn: '/login',
  },
  session: {
    strategy: 'jwt'
  }
} 