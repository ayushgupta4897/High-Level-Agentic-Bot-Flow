<template>
  <div class="bg-white rounded-lg border border-gray-200 shadow-sm h-full flex flex-col">
    <!-- Chat Header -->
    <div class="border-b border-gray-200 px-4 py-3">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-lg font-semibold text-gray-900">Chat</h2>
          <p class="text-xs text-gray-500">
            {{ chatStore.messageCount }} messages • Session {{ chatStore.sessionId.slice(0, 8) }}
          </p>
        </div>
        
        <!-- Chat Status -->
        <div class="text-xs text-gray-500">
          <div v-if="chatStore.isTyping" class="flex items-center space-x-1">
            <span>AI is typing</span>
            <div class="flex space-x-1">
              <div class="w-1 h-1 bg-gray-400 rounded-full animate-bounce"></div>
              <div class="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s;"></div>
              <div class="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s;"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Messages Area -->
    <div 
      ref="messagesContainer"
      class="flex-1 overflow-y-auto px-4 py-4 space-y-4"
    >
      <!-- Loading indicator -->
      <div v-if="chatStore.isLoadingHistory" class="flex items-center justify-center py-8">
        <div class="flex items-center space-x-3 text-gray-500">
          <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
          <span class="text-sm">Loading conversation history...</span>
        </div>
      </div>
      
      <div
        v-for="message in chatStore.messages"
        :key="message.id"
        class="flex"
        :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-[85%] rounded-lg px-4 py-3"
          :class="getMessageClasses(message)"
        >
          <div class="text-sm leading-relaxed">
            <div 
              v-if="message.role === 'assistant' && !message.isError"
              v-html="renderMarkdown(message.content)"
              class="prose prose-sm max-w-none prose-headings:mt-4 prose-headings:mb-2 prose-p:my-2 prose-ul:my-2 prose-ol:my-2 prose-li:my-0"
            />
            <div v-else class="whitespace-pre-wrap">
              {{ message.content }}
            </div>
          </div>
          <div class="text-xs mt-2 opacity-70 flex items-center justify-between">
            <span>{{ formatTime(message.timestamp) }}</span>
            <span v-if="message.isError" class="text-red-500 ml-2">⚠️ Error</span>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-if="chatStore.messageCount === 0" class="text-center py-12">
        <div class="text-4xl mb-4">🌍</div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Start Planning Your Trip</h3>
        <p class="text-gray-500 mb-6 max-w-md mx-auto">
          Tell me where you'd like to go, your budget, and travel dates. 
          I'll help you find flights, hotels, and activities!
        </p>
        <div class="flex flex-wrap justify-center gap-2">
          <button
            v-for="suggestion in quickSuggestions"
            :key="suggestion"
            @click="sendQuickSuggestion(suggestion)"
            class="px-3 py-1 text-sm bg-blue-50 text-blue-600 rounded-full hover:bg-blue-100 transition-colors"
          >
            {{ suggestion }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Input Area -->
    <div class="border-t border-gray-200 p-4">
      <form @submit.prevent="handleSubmit" class="flex space-x-3">
        <div class="flex-1 relative">
          <input
            v-model="inputMessage"
            type="text"
            placeholder="Type your travel request... (e.g., 'Plan a 3-day trip to Goa for ₹30000')"
            class="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            :disabled="chatStore.isTyping"
            @keydown.enter.prevent="handleSubmit"
          />
          <div class="absolute right-3 top-1/2 transform -translate-y-1/2 text-xs text-gray-400">
            {{ inputMessage.length }}/500
          </div>
        </div>
        
        <button
          type="submit"
          :disabled="!canSend"
          class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
        >
          <span v-if="!chatStore.isTyping">Send</span>
          <span v-else>Sending...</span>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
          </svg>
        </button>
      </form>
      
      <!-- Quick Actions -->
      <div v-if="chatStore.messageCount > 0" class="mt-3 flex flex-wrap gap-2">
        <button
          v-for="action in quickActions"
          :key="action.text"
          @click="sendQuickSuggestion(action.text)"
          class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-md hover:bg-gray-200 transition-colors"
          :disabled="chatStore.isTyping"
        >
          {{ action.emoji }} {{ action.text }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { useChatStore } from '../stores/chat'
import { useChat } from '../composables/useChat'
import { useMarkdown } from '../composables/useMarkdown'
import type { Message } from '../types'

// Stores
const chatStore = useChatStore()

// Composables
const { sendMessage } = useChat()
const { renderMarkdown } = useMarkdown()

// State
const inputMessage = ref('')
const messagesContainer = ref<HTMLElement>()

// Computed
const canSend = computed(() => 
  inputMessage.value.trim().length > 0 && 
  inputMessage.value.length <= 500 &&
  !chatStore.isTyping
)

const quickSuggestions = [
  'Plan a trip to Goa for ₹25000',
  'Find hotels in Mumbai under ₹3000/night',
  'Show me Tokyo travel options',
  'Weekend getaway from Delhi'
]

const quickActions = computed(() => [
  { emoji: '💰', text: 'Change my budget' },
  { emoji: '📅', text: 'Update travel dates' },
  { emoji: '🍽️', text: 'I\'m vegetarian' },
  { emoji: '🎯', text: 'Show more activities' }
])

// Watch for new messages to auto-scroll
watch(() => chatStore.messages, async () => {
  await nextTick()
  scrollToBottom()
}, { deep: true })

// Methods
const handleSubmit = async () => {
  const content = inputMessage.value.trim()
  if (!content || !canSend.value) return
  
  // Send message
  await sendMessage(chatStore.sessionId, content)
  
  // Clear input
  inputMessage.value = ''
}

const sendQuickSuggestion = async (suggestion: string) => {
  if (chatStore.isTyping) return
  
  await sendMessage(chatStore.sessionId, suggestion)
}

const getMessageClasses = (message: Message) => {
  if (message.role === 'user') {
    return 'bg-blue-600 text-white'
  } else if (message.isError) {
    return 'bg-red-50 text-red-800 border border-red-200'
  } else {
    return 'bg-gray-100 text-gray-900'
  }
}

const formatTime = (timestamp: Date) => {
  return timestamp.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>
