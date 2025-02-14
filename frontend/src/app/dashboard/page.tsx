import { createServerComponentClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { LogoutButton } from '@/components/LogoutButton'

export default async function DashboardPage() {
  // Get the cookie store
  const cookieStore = cookies()
  
  // Create the Supabase client with the cookie store
  const supabase = createServerComponentClient({ cookies: () => cookieStore })
  
  // Get the session
  const { data: { session } } = await supabase.auth.getSession()
  
  if (!session) {
    redirect('/login')
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8" style={{ background: '#333b6a' }}>
      <div className="bg-white/10 backdrop-blur-lg p-10 rounded-2xl w-full max-w-md space-y-6 shadow-2xl text-gray-100">
        <h1 className="text-2xl font-semibold text-center">Dashboard</h1>
        <p className="text-gray-300">Welcome, {session.user.email}</p>
        <LogoutButton />
      </div>
    </div>
  )
}

