/**
 * Sessions store for ChatGPT-style session management
 * Connected to backend session persistence
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useLocalStorage } from '@vueuse/core'
import { v4 as uuidv4 } from 'uuid'

export interface ChatSession {
  id: string
  title: string
  lastMessage: string | null
  lastActivity: Date
  messageCount: number
  destination?: string | null
  budget?: number | null
}

export const useSessionsStore = defineStore('sessions', () => {
  // State
  const sessions = ref<ChatSession[]>([])
  const currentSessionId = useLocalStorage('travel-agent-current-session', () => uuidv4())
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // Getters
  const sortedSessions = computed(() => 
    sessions.value.sort((a, b) => new Date(b.lastActivity).getTime() - new Date(a.lastActivity).getTime())
  )
  
  const currentSession = computed(() => 
    sessions.value.find(s => s.id === currentSessionId.value)
  )
  
  const hasMultipleSessions = computed(() => sessions.value.length > 1)
  
  // Backend API methods
  const fetchSessions = async () => {
    console.log('🔄 Fetching sessions from backend...')
    isLoading.value = true
    error.value = null
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/chat/sessions')
      if (!response.ok) throw new Error('Failed to fetch sessions')
      
      const data = await response.json()
      console.log('📊 Backend sessions:', data.total)
      
      // Convert backend format to frontend format
      sessions.value = data.sessions.map((backendSession: any) => ({
        id: backendSession.session_id,
        title: backendSession.title,
        lastMessage: backendSession.last_message,
        lastActivity: new Date(backendSession.last_updated),
        messageCount: backendSession.message_count,
        destination: backendSession.destination,
        budget: backendSession.budget
      }))
      
      // If no current session or current session doesn't exist, select first one
      if (!currentSessionId.value || !sessions.value.find(s => s.id === currentSessionId.value)) {
        if (sessions.value.length > 0) {
          currentSessionId.value = sessions.value[0].id
          console.log('✅ Set current session to:', currentSessionId.value)
        }
      }
      
    } catch (err) {
      console.error('❌ Failed to fetch sessions:', err)
      error.value = 'Failed to load sessions'
    } finally {
      isLoading.value = false
    }
  }
  
  // Actions
  const createSession = (title: string = 'New Chat') => {
    const newSessionId = uuidv4()
    
    // Add to frontend immediately
    const newSession: ChatSession = {
      id: newSessionId,
      title,
      lastMessage: null,
      lastActivity: new Date(),
      messageCount: 0
    }
    
    console.log('🆕 Creating new session:', newSessionId)
    sessions.value.unshift(newSession)
    currentSessionId.value = newSessionId
    
    return newSessionId
  }
  
  const updateSession = (sessionId: string, updates: Partial<ChatSession>) => {
    const session = sessions.value.find(s => s.id === sessionId)
    if (session) {
      Object.assign(session, updates, { lastActivity: new Date() })
    }
  }
  
  const updateSessionFromMessage = (sessionId: string, message: string) => {
    const session = sessions.value.find(s => s.id === sessionId)
    if (session) {
      session.lastMessage = message
      session.lastActivity = new Date()
      session.messageCount += 1
      
      // Auto-update title from first message if it's still default
      if (session.title === 'New Chat' && message.trim()) {
        let title = message.trim()
        // Extract destination/travel intent for title
        const travelMatch = title.match(/(?:to|visit|trip.*to|go.*to)\s+(\w+(?:\s+\w+)*)/i)
        if (travelMatch) {
          title = `Trip to ${travelMatch[1]}`
        } else {
          title = title.length > 30 ? title.substring(0, 30) + '...' : title
        }
        session.title = title
      }
    }
  }
  
  const selectSession = (sessionId: string) => {
    console.log('🎯 Selecting session:', sessionId)
    currentSessionId.value = sessionId
  }
  
  const deleteSession = async (sessionId: string) => {
    console.log('🗑️ Deleting session:', sessionId)
    
    // Don't delete if it's the only session
    if (sessions.value.length <= 1) {
      console.log('❌ Cannot delete last session')
      return false
    }
    
    try {
      // Delete from backend
      const response = await fetch(`http://localhost:8000/api/v1/chat/session/${sessionId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        console.log('✅ Session deleted from backend')
      }
    } catch (err) {
      console.error('❌ Failed to delete session from backend:', err)
    }
    
    // Remove from frontend
    sessions.value = sessions.value.filter(s => s.id !== sessionId)
    
    // If deleted current session, switch to first available
    if (currentSessionId.value === sessionId) {
      if (sessions.value.length > 0) {
        currentSessionId.value = sessions.value[0].id
        console.log('🔄 Switched to session:', currentSessionId.value)
      } else {
        console.log('🆕 Creating new session after deletion')
        createSession()
      }
    }
    
    return true
  }
  
  const refreshSessions = async () => {
    console.log('🔄 Refreshing sessions...')
    await fetchSessions()
  }
  
  const clearAllSessions = async () => {
    try {
      // Clear all sessions from backend (would need endpoint)
      for (const session of sessions.value) {
        try {
          await fetch(`http://localhost:8000/api/v1/chat/session/${session.id}`, {
            method: 'DELETE'
          })
        } catch (err) {
          console.error('Failed to delete session:', session.id)
        }
      }
    } catch (err) {
      console.error('Error clearing sessions:', err)
    }
    
    sessions.value = []
    createSession()
  }
  
  // Initialize sessions on store creation
  const initialize = async () => {
    console.log('🚀 Initializing sessions store...')
    await fetchSessions()
    
    // If no sessions exist, create first one
    if (sessions.value.length === 0) {
      console.log('🆕 No sessions found, creating first session')
      createSession()
    }
  }
  
  // Auto-initialize
  initialize()
  
  return {
    // State
    sessions,
    currentSessionId,
    isLoading,
    error,
    
    // Getters
    sortedSessions,
    currentSession,
    hasMultipleSessions,
    
    // Actions
    fetchSessions,
    refreshSessions,
    createSession,
    updateSession,
    updateSessionFromMessage,
    selectSession,
    deleteSession,
    clearAllSessions,
    initialize
  }
})
