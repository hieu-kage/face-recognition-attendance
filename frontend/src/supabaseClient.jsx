import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://ecllkmftjruvncwfxvpa.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVjbGxrbWZ0anJ1dm5jd2Z4dnBhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyNDU4ODUsImV4cCI6MjA3NzgyMTg4NX0.wK1YCBs7UjEzf9NUHNUpA7A6CU7Sse3Z2bum5Da91Yo'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)