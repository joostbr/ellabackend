import type { AuthOptions } from 'next-auth'
import CredentialsProvider from "next-auth/providers/credentials"

export const authConfig: AuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (credentials?.email === "test@example.com" && credentials?.password === "password") {
          return {
            id: "1",
            email: credentials.email,
            name: "Test User"
          }
        }
        return null
      }
    })
  ],
  pages: {
    signIn: '/login',
  }
} 