/**
 * Server-Sent Events composable for real-time communication
 */

import { ref, onUnmounted } from 'vue'
import type { SSEEvent } from '../types'

interface UseSSEOptions {
  onMessage?: (event: SSEEvent) => void
  onError?: (error: Event) => void
  onConnect?: () => void
  onDisconnect?: () => void
  autoReconnect?: boolean
  reconnectDelay?: number
}

export function useSSE(baseUrl: string = 'http://localhost:8000') {
  const eventSource = ref<EventSource | null>(null)
  const connectionStatus = ref<'disconnected' | 'connecting' | 'connected'>('disconnected')
  const error = ref<string | null>(null)
  
  const connect = (sessionId: string, options: UseSSEOptions = {}) => {
    if (eventSource.value && eventSource.value.readyState === EventSource.OPEN) {
      return
    }
    
    connectionStatus.value = 'connecting'
    error.value = null
    
    const url = `${baseUrl}/api/v1/chat/events/${sessionId}`
    eventSource.value = new EventSource(url)
    
    eventSource.value.onopen = () => {
      connectionStatus.value = 'connected'
      options.onConnect?.()
    }
    
    eventSource.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as SSEEvent
        
        // Handle connection confirmation
        if (data.type === 'connected') {
          connectionStatus.value = 'connected'
          error.value = null
        }
        
        options.onMessage?.(data)
      } catch (err) {
        console.error('Failed to parse SSE message:', err)
        options.onError?.(event as any)
      }
    }
    
    eventSource.value.onerror = (event) => {
      connectionStatus.value = 'disconnected'
      error.value = 'Connection error'
      options.onError?.(event)
      
      // Auto-reconnect if enabled
      if (options.autoReconnect !== false) {
        const delay = options.reconnectDelay || 3000
        setTimeout(() => {
          if (connectionStatus.value === 'disconnected') {
            connect(sessionId, options)
          }
        }, delay)
      }
    }
    
    // Cleanup on unmount
    onUnmounted(() => {
      disconnect()
    })
  }
  
  const disconnect = () => {
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
    }
    connectionStatus.value = 'disconnected'
    error.value = null
  }
  
  return {
    connect,
    disconnect,
    connectionStatus,
    error
  }
}
