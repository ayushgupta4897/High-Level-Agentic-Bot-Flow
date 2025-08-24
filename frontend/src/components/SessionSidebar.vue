<template>
  <div class="h-full bg-gray-900 text-white flex flex-col">
    <!-- Header -->
    <div class="p-4 border-b border-gray-700">
      <button
        @click="createNewChat"
        class="w-full flex items-center justify-center space-x-2 px-4 py-2.5 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors border border-gray-600"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        <span class="text-sm font-medium">New Chat</span>
      </button>
    </div>

    <!-- Sessions List -->
    <div class="flex-1 overflow-y-auto p-2 space-y-1">
      <!-- Loading State -->
      <div v-if="sessionsStore.isLoading" class="text-center py-8">
        <div class="text-gray-400 text-sm">Loading sessions...</div>
      </div>
      
      <!-- No Sessions -->
      <div v-else-if="sessionsStore.sessions.length === 0" class="text-center py-8">
        <div class="text-gray-400 text-sm">No sessions found</div>
        <button @click="createNewChat" class="mt-2 text-blue-400 text-xs underline">
          Create First Session
        </button>
      </div>
      
      <!-- Sessions -->
      <div
        v-for="session in sessionsStore.sortedSessions"
        :key="session.id"
        class="group relative"
      >
        <button
          @click="selectSession(session.id)"
          class="w-full text-left px-3 py-2.5 rounded-lg text-sm transition-colors relative"
          :class="session.id === sessionsStore.currentSessionId 
            ? 'bg-gray-700 text-white' 
            : 'text-gray-300 hover:bg-gray-800 hover:text-white'"
        >
          <!-- Session Content -->
          <div class="flex items-center space-x-2">
            <div class="w-6 h-6 rounded-full bg-gradient-to-br from-blue-400 to-purple-600 flex items-center justify-center text-xs font-bold text-white">
              🧳
            </div>
            <div class="flex-1 min-w-0">
              <div class="font-medium truncate">
                {{ session.title || session.id.slice(0, 8) }}
              </div>
              <div class="text-xs text-gray-400 truncate">
                {{ session.lastMessage || 'No messages yet' }}
              </div>
              <!-- Travel Details -->
              <div v-if="session.destination || session.budget" class="text-xs text-gray-500 mt-0.5">
                <span v-if="session.destination">📍{{ session.destination }}</span>
                <span v-if="session.budget" class="ml-2">💰₹{{ session.budget.toLocaleString() }}</span>
              </div>
            </div>
          </div>
          
          <!-- Session Metadata -->
          <div class="mt-1 flex items-center justify-between text-xs text-gray-500">
            <span>{{ session.messageCount }} msgs</span>
            <span>{{ formatSessionTime(session.lastActivity) }}</span>
          </div>
        </button>

        <!-- Delete Button -->
        <button
          @click.stop="deleteSession(session.id)"
          class="absolute top-2 right-2 w-6 h-6 rounded-md bg-red-600 hover:bg-red-700 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
        >
          <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Footer -->
    <div class="p-4 border-t border-gray-700">
      <div class="text-xs text-gray-400 text-center">
        Travel Agent • {{ sessionsStore.sessions.length }} sessions
      </div>
      <div class="text-xs text-gray-500 text-center mt-1">
        Current: {{ sessionsStore.currentSessionId.slice(0, 8) }}
      </div>
      <div class="mt-2 flex justify-center space-x-2">
        <button
          @click="createNewChat"
          class="text-xs text-blue-400 hover:text-blue-300 transition-colors"
        >
          + Add
        </button>
        <button
          @click="refreshSessions"
          class="text-xs text-green-400 hover:text-green-300 transition-colors"
        >
          🔄 Refresh
        </button>
        <button
          @click="clearAllSessions"
          class="text-xs text-gray-400 hover:text-white transition-colors"
        >
          Clear All
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useSessionsStore } from '../stores/sessions'
import { useChatStore } from '../stores/chat'
import { usePreferencesStore } from '../stores/preferences'

// Stores
const sessionsStore = useSessionsStore()
const chatStore = useChatStore()
const preferencesStore = usePreferencesStore()

// Emits
const emit = defineEmits<{
  'session-changed': [sessionId: string]
}>()

// Debug sessions on mount
onMounted(async () => {
  console.log('🔄 SessionSidebar mounted')
  console.log('Sessions available:', sessionsStore.sessions.length)
  
  // Refresh sessions from backend on mount
  if (sessionsStore.sessions.length === 0) {
    console.log('📥 No sessions, fetching from backend...')
    await sessionsStore.fetchSessions()
  }
  
  console.log('Current session ID:', sessionsStore.currentSessionId)
})

// Methods
const createNewChat = () => {
  const newSessionId = sessionsStore.createSession()
  chatStore.newSession()
  preferencesStore.clearAllPreferences()
  chatStore.initializeWelcome()
  emit('session-changed', newSessionId)
}

const selectSession = async (sessionId: string) => {
  if (sessionId === sessionsStore.currentSessionId) return
  
  console.log('Selecting session:', sessionId)
  sessionsStore.selectSession(sessionId)
  
  // Switch to session (loads conversation history)
  await chatStore.switchSession(sessionId)
  
  // Load session preferences if available
  preferencesStore.clearAllPreferences()
  if (chatStore.memoryUpdates && Object.keys(chatStore.memoryUpdates).length > 0) {
    preferencesStore.setFromMemoryUpdates(chatStore.memoryUpdates)
  }
  
  emit('session-changed', sessionId)
}

const deleteSession = async (sessionId: string) => {
  console.log('🗑️ Deleting session:', sessionId)
  
  const success = await sessionsStore.deleteSession(sessionId)
  if (success) {
    // If it was the current session and we switched, update UI
    if (sessionsStore.currentSessionId !== sessionId) {
      await chatStore.switchSession(sessionsStore.currentSessionId)
      preferencesStore.clearAllPreferences()
      if (chatStore.memoryUpdates && Object.keys(chatStore.memoryUpdates).length > 0) {
        preferencesStore.setFromMemoryUpdates(chatStore.memoryUpdates)
      }
      emit('session-changed', sessionsStore.currentSessionId)
    }
  }
}

const refreshSessions = async () => {
  console.log('🔄 Refreshing sessions from backend...')
  await sessionsStore.refreshSessions()
}

const clearAllSessions = async () => {
  await sessionsStore.clearAllSessions()
  chatStore.newSession()
  preferencesStore.clearAllPreferences()
  chatStore.initializeWelcome()
  emit('session-changed', sessionsStore.currentSessionId)
}

const formatSessionTime = (timestamp: Date) => {
  const now = new Date()
  const time = new Date(timestamp)
  const diffMs = now.getTime() - time.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'now'
  if (diffMins < 60) return `${diffMins}m`
  if (diffHours < 24) return `${diffHours}h`
  if (diffDays < 7) return `${diffDays}d`
  return time.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
</script>
