import { createClient } from '@/app/utils/supabase/server'
import { redirect } from 'next/navigation'
import { LogoutButton } from '@/components/LogoutButton'

export default async function DashboardPage() {
  // Get the session from Supabase
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  
  if (!user) {
    redirect('/login')
  }

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center p-8"
      style={{ background: '#333b6a' }}
    >
      <div className="bg-white/10 backdrop-blur-lg p-10 rounded-2xl w-full max-w-md space-y-6 shadow-2xl text-gray-100">
        <h1 className="text-2xl font-semibold text-center">Dashboard</h1>
        <p className="text-gray-300">Welcome, {user.email}</p>
        <LogoutButton />
      </div>
    </div>
  )
}