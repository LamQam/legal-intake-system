import { useEffect } from 'react'
import { supabase } from '@/lib/supabase/client'
import { useQueryClient } from '@tanstack/react-query'

export function useRealtimeInbox() {
  const queryClient = useQueryClient()

  useEffect(() => {
    const channel = supabase
      .channel('inbox-changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'conversations'
        },
        (payload) => {
          queryClient.invalidateQueries({ queryKey: ['inbox'] })
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [queryClient])
}