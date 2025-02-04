import { getServerSession } from "next-auth"
import { redirect } from "next/navigation"
import { authConfig } from "../auth.config"
import { LogoutButton } from "@/components/LogoutButton"

export default async function DashboardPage() {
  const session = await getServerSession(authConfig)
  
  if (!session) {
    redirect('/login')
  }

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome {session.user?.email}</p>
      <LogoutButton />
    </div>
  )
}

