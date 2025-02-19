'use client'

import { useRouter } from 'next/navigation'
import { createClient } from '@/app/utils/supabase/client'

export function LogoutButton() {
  const router = useRouter()

  const handleSignOut = async () => {
    const supabase = createClient()
    await supabase.auth.signOut()
    router.push('/login')
    router.refresh()
  }

  return (
    <button 
      onClick={handleSignOut}
      className="px-4 py-2 rounded bg-red-500 text-white hover:bg-red-600"
    >
      Sign Out
    </button>
  )
} 