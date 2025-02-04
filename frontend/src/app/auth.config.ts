import type { AuthOptions } from 'next-auth'
import CredentialsProvider from "next-auth/providers/credentials"
import { supabase } from '@/lib/supabase'
import { hashPassword, verifyPassword } from '@/lib/auth'

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
            .select('id, email, name, password_hash')
            .eq('email', credentials.email)
            .single()

          if (error || !user) {
            return null
          }

          const isValidPassword = await verifyPassword(
            credentials.password,
            user.password_hash
          )

          if (!isValidPassword) {
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