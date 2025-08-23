/**
 * Chat store using Pinia
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useLocalStorage } from '@vueuse/core'
import { v4 as uuidv4 } from 'uuid'
import type { Message, AgentAction, ChatState } from '../types'

export const useChatStore = defineStore('chat', () => {
  // State
  const sessionId = useLocalStorage('travel-agent-session-id', () => uuidv4())
  const messages = ref<Message[]>([])
  const agentActions = ref<AgentAction[]>([])
  const memoryUpdates = ref<Record<string, any>>({})
  const isTyping = ref(false)
  const error = ref<string | null>(null)
  const isLoadingHistory = ref(false)
  
  // Cache for session conversations
  const sessionMessages = useLocalStorage('travel-agent-session-messages', () => ({}))
  const sessionActions = useLocalStorage('travel-agent-session-actions', () => ({}))
  const sessionMemory = useLocalStorage('travel-agent-session-memory', () => ({}))
  
  // Getters
  const messageCount = computed(() => messages.value.length)
  const userMessageCount = computed(() => 
    messages.value.filter(m => m.role === 'user').length
  )
  const hasError = computed(() => error.value !== null)
  const lastUserMessage = computed(() => {
    const userMessages = messages.value.filter(m => m.role === 'user')
    return userMessages[userMessages.length - 1]
  })
  const recentActions = computed(() => 
    agentActions.value.slice(-10) // Last 10 actions
  )
  
  // Actions
  const setTyping = (typing: boolean) => {
    isTyping.value = typing
  }
  
  const setError = (errorMessage: string | null) => {
    error.value = errorMessage
  }
  
  const addMessage = (message: Message) => {
    messages.value.push(message)
  }
  
  const addAgentAction = (action: AgentAction) => {
    agentActions.value.push(action)
  }
  
  const updateMemory = (updates: Record<string, any>) => {
    Object.assign(memoryUpdates.value, updates)
  }
  
  const clearMessages = () => {
    messages.value = []
  }
  
  const clearActions = () => {
    agentActions.value = []
  }
  
  const clearMemory = () => {
    memoryUpdates.value = {}
  }
  
  const clearAll = () => {
    clearMessages()
    clearActions()
    clearMemory()
    setTyping(false)
    setError(null)
  }
  
  const newSession = () => {
    sessionId.value = uuidv4()
    clearAll()
  }
  
  const initializeWelcome = () => {
    const welcomeMessage: Message = {
      id: uuidv4(),
      role: 'assistant',
      content: "Hello! I'm your AI travel agent. I can help you plan flights, hotels, and activities for your trip. Where would you like to go?",
      timestamp: new Date()
    }
    messages.value = [welcomeMessage]
  }
  
  // Load conversation history from backend
  const loadConversationHistory = async (sessionIdToLoad: string) => {
    console.log('Loading conversation history for session:', sessionIdToLoad)
    isLoadingHistory.value = true
    error.value = null
    
    try {
      // Try to load from cache first
      const cachedMessages = sessionMessages.value[sessionIdToLoad]
      const cachedActions = sessionActions.value[sessionIdToLoad]
      const cachedMemory = sessionMemory.value[sessionIdToLoad]
      
      if (cachedMessages && cachedMessages.length > 1) {
        console.log('Loading from cache:', cachedMessages.length, 'messages')
        messages.value = cachedMessages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }))
        agentActions.value = cachedActions || []
        memoryUpdates.value = cachedMemory || {}
        isLoadingHistory.value = false
        return
      }
      
      // Load from backend
      console.log('Loading from backend...')
      const [historyResponse, contextResponse] = await Promise.all([
        fetch(`http://localhost:8000/api/v1/chat/history/${sessionIdToLoad}`),
        fetch(`http://localhost:8000/api/v1/chat/context/${sessionIdToLoad}`)
      ])
      
      if (historyResponse.ok) {
        const historyData = await historyResponse.json()
        console.log('Backend history:', historyData.messages?.length || 0, 'messages')
        
        if (historyData.messages && historyData.messages.length > 0) {
          // Convert backend format to frontend format
          const backendMessages = historyData.messages.map((msg: any) => ({
            id: uuidv4(),
            role: msg.role,
            content: msg.content,
            timestamp: new Date(msg.timestamp)
          }))
          
          messages.value = backendMessages
          
          // Cache the loaded messages
          sessionMessages.value[sessionIdToLoad] = backendMessages
        } else {
          console.log('No backend history, initializing welcome message')
          initializeWelcome()
        }
      } else {
        console.log('Failed to load backend history, initializing welcome message')
        initializeWelcome()
      }
      
      if (contextResponse.ok) {
        const contextData = await contextResponse.json()
        console.log('Backend context:', contextData.preferences)
        memoryUpdates.value = contextData.preferences || {}
        
        // Cache the loaded context
        sessionMemory.value[sessionIdToLoad] = contextData.preferences || {}
      }
      
    } catch (err) {
      console.error('Error loading conversation history:', err)
      error.value = 'Failed to load conversation history'
      initializeWelcome()
    } finally {
      isLoadingHistory.value = false
    }
  }
  
  // Save current session to cache
  const saveCurrentSession = () => {
    const currentSessionId = sessionId.value
    console.log('Saving session to cache:', currentSessionId, messages.value.length, 'messages')
    
    sessionMessages.value[currentSessionId] = messages.value
    sessionActions.value[currentSessionId] = agentActions.value
    sessionMemory.value[currentSessionId] = memoryUpdates.value
  }
  
  // Switch to a different session
  const switchSession = async (newSessionId: string) => {
    console.log('Switching from', sessionId.value, 'to', newSessionId)
    
    // Save current session first
    if (messages.value.length > 0) {
      saveCurrentSession()
    }
    
    // Clear current state
    clearAll()
    
    // Update session ID
    sessionId.value = newSessionId
    
    // Load new session
    await loadConversationHistory(newSessionId)
  }
  
  return {
    // State
    sessionId,
    messages,
    agentActions,
    memoryUpdates,
    isTyping,
    error,
    isLoadingHistory,
    
    // Getters
    messageCount,
    userMessageCount,
    hasError,
    lastUserMessage,
    recentActions,
    
    // Actions
    setTyping,
    setError,
    addMessage,
    addAgentAction,
    updateMemory,
    clearMessages,
    clearActions,
    clearMemory,
    clearAll,
    newSession,
    initializeWelcome,
    loadConversationHistory,
    saveCurrentSession,
    switchSession
  }
})
