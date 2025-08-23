/**
 * Sessions store for ChatGPT-style session management
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useLocalStorage } from '@vueuse/core'
import { v4 as uuidv4 } from 'uuid'

export interface ChatSession {
  id: string
  title: string
  lastMessage: string
  lastActivity: Date
  messageCount: number
}

export const useSessionsStore = defineStore('sessions', () => {
  // State
  const sessions = useLocalStorage<ChatSession[]>('travel-agent-sessions', [])
  const currentSessionId = useLocalStorage('travel-agent-current-session', () => uuidv4())
  
  // Getters
  const sortedSessions = computed(() => 
    sessions.value.sort((a, b) => new Date(b.lastActivity).getTime() - new Date(a.lastActivity).getTime())
  )
  
  const currentSession = computed(() => 
    sessions.value.find(s => s.id === currentSessionId.value)
  )
  
  const hasMultipleSessions = computed(() => sessions.value.length > 1)
  
  // Actions
  const createSession = (title: string = 'New Chat') => {
    const newSession: ChatSession = {
      id: uuidv4(),
      title,
      lastMessage: '',
      lastActivity: new Date(),
      messageCount: 0
    }
    
    console.log('Creating new session:', newSession)
    sessions.value.unshift(newSession)
    currentSessionId.value = newSession.id
    console.log('Sessions after creation:', sessions.value.length)
    
    return newSession.id
  }
  
  const updateSession = (sessionId: string, updates: Partial<ChatSession>) => {
    const session = sessions.value.find(s => s.id === sessionId)
    if (session) {
      Object.assign(session, updates, { lastActivity: new Date() })
    }
  }
  
  const updateSessionTitle = (sessionId: string, firstMessage: string) => {
    const session = sessions.value.find(s => s.id === sessionId)
    if (session && session.title === 'New Chat') {
      // Generate concise title from first message (ChatGPT style)
      let title = firstMessage.trim()
      
      // Remove common travel words for conciseness
      title = title.replace(/plan a trip|find|show me|help me|i want to/gi, '').trim()
      
      // Capitalize and limit length
      title = title.charAt(0).toUpperCase() + title.slice(1)
      title = title.length > 30 ? title.substring(0, 30) + '...' : title
      
      session.title = title || 'Travel Planning'
    }
  }
  
  const selectSession = (sessionId: string) => {
    currentSessionId.value = sessionId
  }
  
  const deleteSession = (sessionId: string) => {
    console.log('Deleting session from store:', sessionId)
    console.log('Sessions before deletion:', sessions.value.length)
    
    // Don't delete if it's the only session
    if (sessions.value.length <= 1) {
      console.log('Cannot delete last session')
      return
    }
    
    sessions.value = sessions.value.filter(s => s.id !== sessionId)
    console.log('Sessions after deletion:', sessions.value.length)
    
    // If deleted current session, switch to first available
    if (currentSessionId.value === sessionId) {
      if (sessions.value.length > 0) {
        currentSessionId.value = sessions.value[0].id
        console.log('Switched current session to:', currentSessionId.value)
      } else {
        console.log('No sessions left, creating new one')
        createSession()
      }
    }
  }
  
  const clearAllSessions = () => {
    sessions.value = []
    createSession()
  }
  
  // Initialize first session if none exist
  const initializeSessions = () => {
    if (sessions.value.length === 0) {
      console.log('Creating initial session')
      const initialSessionId = createSession()
      console.log('Initial session created:', initialSessionId)
    } else {
      console.log('Existing sessions found:', sessions.value.length)
    }
  }
  
  // Initialize on store creation
  initializeSessions()
  
  return {
    // State
    sessions,
    currentSessionId,
    
    // Getters
    sortedSessions,
    currentSession,
    hasMultipleSessions,
    
    // Actions
    createSession,
    updateSession,
    updateSessionTitle,
    selectSession,
    deleteSession,
    clearAllSessions
  }
})
