/**
 * Chat composable for managing chat state and interactions
 */

import { ref } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import type { Message, AgentAction, SSEEvent } from '../types'
import { useChatStore } from '../stores/chat'
import { usePreferencesStore } from '../stores/preferences'
import { useSessionsStore } from '../stores/sessions'

export function useChat() {
  const messages = ref<Message[]>([])
  const agentActions = ref<AgentAction[]>([])
  const memoryUpdates = ref<Record<string, any>>({})
  const isTyping = ref(false)
  const error = ref<string | null>(null)
  
  // Get stores
  const chatStore = useChatStore()
  const preferencesStore = usePreferencesStore()
  const sessionsStore = useSessionsStore()
  
  const sendMessage = async (sessionId: string, content: string) => {
    if (!content.trim()) return

    // Add user message to store
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    }
    chatStore.addMessage(userMessage)
    
    // Update session with first message title
    console.log('Current message count:', chatStore.messageCount)
    if (chatStore.messageCount <= 2) { // Only user + welcome message
      console.log('Updating session title with:', content)
      sessionsStore.updateSessionTitle(sessionId, content)
    }
    
    // Update session metadata
    sessionsStore.updateSession(sessionId, {
      lastMessage: content.length > 50 ? content.substring(0, 50) + '...' : content,
      messageCount: chatStore.messageCount
    })

    try {
      chatStore.setTyping(true)
      
      // Use fetch API for streaming POST requests
      const response = await fetch(`http://localhost:8000/api/v1/chat/message/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: content
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body reader')
      }

      const decoder = new TextDecoder()
      let buffer = ''
      let currentMessage: Message | null = null
      let messageContent = ''

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) {
          break
        }

        buffer += decoder.decode(value, { stream: true })
        
        // Process complete SSE messages
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // Keep incomplete line in buffer
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const eventData = line.slice(6) // Remove 'data: '
              if (eventData.trim() === '') continue // Skip empty data
              
              const data = JSON.parse(eventData)
              
              switch (data.type) {
                case 'start':
                  chatStore.setTyping(true)
                  break
                  
                case 'action':
                  // Add to inspector panel
                  const action: AgentAction = {
                    action_type: data.description.toLowerCase().replace(/\s+/g, '_'),
                    description: data.description,
                    timestamp: new Date().toISOString(),
                    data: {}
                  }
                  chatStore.addAgentAction(action)
                  break
                  
                case 'memory':
                  // Update memory in stores
                  console.log('Received memory update:', data.updates)
                  if (data.updates) {
                    chatStore.updateMemory(data.updates)
                    preferencesStore.setFromMemoryUpdates(data.updates)
                    console.log('Updated preferences store with:', data.updates)
                  }
                  break
                  
                case 'response_start':
                  // Start a new assistant message
                  currentMessage = {
                    id: uuidv4(),
                    role: 'assistant',
                    content: '',
                    timestamp: new Date()
                  }
                  chatStore.addMessage(currentMessage)
                  messageContent = ''
                  chatStore.setTyping(false)
                  break
                  
                case 'token':
                  // Append token to current message (ChatGPT-style)
                  if (currentMessage) {
                    messageContent += data.content
                    currentMessage.content = messageContent
                    // Trigger reactivity by updating the store
                    const messageIndex = chatStore.messages.findIndex(m => m.id === currentMessage?.id)
                    if (messageIndex !== -1) {
                      chatStore.messages[messageIndex] = { ...currentMessage }
                    }
                  }
                  break
                  
                case 'complete':
                  chatStore.setTyping(false)
                  
                  // Save current session to cache (conversation history persistence)
                  chatStore.saveCurrentSession()
                  
                  // Update session with final message count
                  sessionsStore.updateSession(sessionId, {
                    messageCount: chatStore.messageCount,
                    lastMessage: chatStore.messages[chatStore.messages.length - 1]?.content.substring(0, 50) + '...' || ''
                  })
                  
                  return // Exit the function
                  
                case 'error':
                  console.log('Streaming error:', data.message)
                  chatStore.setTyping(false)
                  chatStore.setError(data.message)
                  
                  const errorMessage: Message = {
                    id: uuidv4(),
                    role: 'assistant',
                    content: data.message || 'Sorry, I encountered an error. Please try again.',
                    timestamp: new Date(),
                    isError: true
                  }
                  chatStore.addMessage(errorMessage)
                  return // Exit the function
              }
            } catch (parseError) {
              console.error('Failed to parse streaming event:', parseError, 'Raw line:', line)
            }
          }
        }
      }
      
      console.log('Streaming ended')

    } catch (err) {
      console.error('Failed to send message:', err)
      chatStore.setError('Failed to send message. Please try again.')
      chatStore.setTyping(false)
      
      // Add error message
      const errorMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: 'Sorry, I encountered an error sending your message. Please try again.',
        timestamp: new Date(),
        isError: true
      }
      chatStore.addMessage(errorMessage)
    }
  }
  
  return {
    sendMessage
  }
}
