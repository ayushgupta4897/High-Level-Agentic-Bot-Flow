<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white border-b border-gray-200 px-4 py-3 shadow-sm">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <span class="text-white font-bold text-sm">🧳</span>
          </div>
          <div>
            <h1 class="text-lg font-semibold text-gray-900">Travel Agent</h1>
            <p class="text-xs text-gray-500">AI-powered travel planning assistant</p>
          </div>
        </div>
        
        <div class="flex items-center space-x-4">
          <!-- Status Info -->
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 bg-green-400 rounded-full" />
            <span class="text-xs text-gray-500">
              Ready
            </span>
          </div>
          
          <!-- New Chat Button -->
          <button 
            @click="startNewChat"
            class="text-xs text-gray-600 hover:text-gray-800 px-3 py-1.5 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            New Chat
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="h-[calc(100vh-80px)] flex">
      
      <!-- Session Sidebar (ChatGPT-style) -->
      <div class="w-64 hidden md:block">
        <SessionSidebar @session-changed="handleSessionChanged" />
      </div>
      
      <!-- Main Chat Area -->
      <div class="flex-1 flex">
        
        <!-- Chat Interface (Main) -->
        <div class="flex-1 min-w-0">
          <ChatInterface />
        </div>
        
        <!-- Inspector Panel (Right Sidebar) -->
        <div class="w-80 border-l border-gray-200">
          <InspectorPanel />
        </div>
        
      </div>
    </div>
    
    <!-- Error Toast -->
    <div 
      v-if="chatStore.hasError"
      class="fixed bottom-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg shadow-lg max-w-md"
    >
      <div class="flex items-center justify-between">
        <span class="text-sm">{{ chatStore.error }}</span>
        <button 
          @click="chatStore.setError(null)"
          class="ml-3 text-red-700 hover:text-red-900"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import ChatInterface from './components/ChatInterface.vue'
import InspectorPanel from './components/InspectorPanel.vue'
import SessionSidebar from './components/SessionSidebar.vue'
import { useChatStore } from './stores/chat'
import { usePreferencesStore } from './stores/preferences'
import { useSessionsStore } from './stores/sessions'

// Stores
const chatStore = useChatStore()
const preferencesStore = usePreferencesStore()
const sessionsStore = useSessionsStore()

// Lifecycle
onMounted(async () => {
  console.log('App mounted, available sessions:', sessionsStore.sessions.length)
  console.log('Current session ID from store:', sessionsStore.currentSessionId)
  
  // Sync session ID with current session
  chatStore.sessionId = sessionsStore.currentSessionId
  
  // Load conversation history for current session (or initialize welcome message)
  await chatStore.loadConversationHistory(chatStore.sessionId)
  
  // Load session preferences if available
  if (chatStore.memoryUpdates && Object.keys(chatStore.memoryUpdates).length > 0) {
    preferencesStore.setFromMemoryUpdates(chatStore.memoryUpdates)
  }
  
  console.log('Chat store session ID set to:', chatStore.sessionId)
  console.log('Loaded messages:', chatStore.messages.length)
})

// Methods
const startNewChat = () => {
  // Create new session
  const newSessionId = sessionsStore.createSession()
  
  // Clear all data
  chatStore.newSession()
  preferencesStore.clearAllPreferences()
  
  // Set new session ID
  chatStore.sessionId = newSessionId
  
  // Initialize new chat
  chatStore.initializeWelcome()
}

const handleSessionChanged = (sessionId: string) => {
  console.log('Session changed to:', sessionId)
  // Session change is already handled in SessionSidebar component
}
</script>

<style>
/* Custom scrollbar styles */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* Animations */
@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.animate-bounce {
  animation: bounce 1.4s infinite ease-in-out both;
}
</style>
