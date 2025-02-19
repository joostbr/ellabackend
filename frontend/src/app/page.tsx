import { redirect } from 'next/navigation';
import { createClient } from '../app/utils/supabase/server';

export default async function Home() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  
  // Simple redirect based on session status
  return redirect(user ? '/dashboard' : '/login');
}
