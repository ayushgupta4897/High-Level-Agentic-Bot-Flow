<template>
  <div class="bg-white rounded-lg border border-gray-200 shadow-sm h-full flex flex-col">
    <!-- Tabs Header -->
    <div class="border-b border-gray-200">
      <nav class="flex space-x-1 p-2">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors"
          :class="activeTab === tab.id 
            ? 'bg-blue-100 text-blue-700' 
            : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'"
        >
          <span>{{ tab.name }}</span>
          <span 
            v-if="tab.count !== undefined"
            class="ml-1 px-1.5 py-0.5 text-xs rounded-full"
            :class="activeTab === tab.id ? 'bg-blue-200' : 'bg-gray-200'"
          >
            {{ tab.count }}
          </span>
        </button>
      </nav>
    </div>

    <!-- Tab Content -->
    <div class="flex-1 overflow-y-auto">
      
      <!-- Agent Actions Tab -->
      <div v-if="activeTab === 'actions'" class="p-4 space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-semibold text-gray-900">Agent Actions</h3>
          <button 
            v-if="chatStore.recentActions.length > 0"
            @click="clearActions"
            class="text-xs text-gray-500 hover:text-gray-700"
          >
            Clear
          </button>
        </div>
        
        <div v-if="chatStore.recentActions.length === 0" class="text-center py-8">
          <div class="text-2xl mb-2">🤖</div>
          <p class="text-sm text-gray-500">
            No actions yet.<br>
            Start a conversation to see how I work!
          </p>
        </div>
        
        <div 
          v-for="(action, index) in chatStore.recentActions.slice().reverse()" 
          :key="index"
          class="relative overflow-hidden rounded-xl border border-gray-100 bg-gradient-to-r from-white to-gray-50 p-4 shadow-sm hover:shadow-md transition-all duration-200"
        >
          <!-- Action Header -->
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center space-x-2">
              <div 
                class="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-semibold shadow-sm"
                :class="getActionTypeClasses(action.action_type)"
              >
                {{ getActionIcon(action.action_type) }}
              </div>
              <div>
                <span class="text-sm font-medium text-gray-900">
                  {{ formatActionType(action.action_type) }}
                </span>
                <div class="text-xs text-gray-500">
                  {{ formatTime(action.timestamp) }}
                </div>
              </div>
            </div>
            
            <!-- Status Indicator -->
            <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          </div>
          
          <!-- Action Description -->
          <p class="text-sm text-gray-700 leading-relaxed mb-3 pl-10">
            {{ action.description }}
          </p>
          
          <!-- Action Details (if any) -->
          <div v-if="action.data && Object.keys(action.data).length > 0" class="pl-10">
            <details class="group">
              <summary class="cursor-pointer text-xs text-blue-600 hover:text-blue-800 font-medium select-none">
                <span class="group-open:hidden">Show Details</span>
                <span class="hidden group-open:inline">Hide Details</span>
              </summary>
              <div class="mt-2 bg-blue-50 border border-blue-200 rounded-lg p-3">
                <pre class="text-xs text-blue-800 whitespace-pre-wrap overflow-x-auto">{{ JSON.stringify(action.data, null, 2) }}</pre>
              </div>
            </details>
          </div>
          
          <!-- Progress Bar -->
          <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-400 to-purple-500 opacity-20"></div>
        </div>
      </div>

      <!-- Memory Tab -->
      <div v-if="activeTab === 'memory'" class="p-4 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-semibold text-gray-900">Travel Preferences</h3>
          <span class="text-xs text-gray-500">
            {{ preferencesStore.preferencesCount }} stored
          </span>
        </div>
        
        <div v-if="preferencesStore.preferencesCount === 0" class="text-center py-8">
          <div class="text-2xl mb-2">💭</div>
          <p class="text-sm text-gray-500">
            No preferences stored yet.<br>
            Tell me about your travel plans!
          </p>
        </div>
        
        <!-- Current Preferences -->
        <div v-if="preferencesStore.preferencesCount > 0" class="space-y-3">
          <div 
            v-for="[key, value] in Object.entries(preferencesStore.preferencesSummary)" 
            :key="key"
            class="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 shadow-sm"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <div class="w-6 h-6 bg-blue-500 rounded-lg flex items-center justify-center text-white text-xs font-bold">
                  {{ getPreferenceIcon(key) }}
                </div>
                <span class="text-sm font-semibold text-gray-900">{{ key }}</span>
              </div>
              <span class="text-sm text-blue-700 font-medium bg-white px-2 py-1 rounded-md">
                {{ value }}
              </span>
            </div>
          </div>
        </div>

        <!-- Recent Updates -->
        <div v-if="hasRecentUpdates" class="mt-4">
          <h4 class="text-sm font-medium text-gray-700 mb-3 flex items-center">
            <div class="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
            Recent Updates
          </h4>
          <div class="space-y-2">
            <div 
              v-for="[key, value] in Object.entries(chatStore.memoryUpdates)"
              :key="key"
              class="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-3 shadow-sm animate-fade-in"
            >
              <div class="flex items-center space-x-2">
                <div class="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                  <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                  </svg>
                </div>
                <span class="text-xs text-green-800 font-medium">
                  Updated {{ formatPreferenceKey(key) }}: 
                  <strong class="text-green-900">{{ formatPreferenceValue(value) }}</strong>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Progress Indicator -->
        <div class="mt-4 p-3 bg-blue-50 rounded-lg">
          <h4 class="text-sm font-medium text-blue-900 mb-2">Trip Planning Progress</h4>
          <div class="space-y-2">
            <div class="flex items-center text-sm">
              <span class="mr-2">{{ preferencesStore.hasDestination ? '✅' : '⏸️' }}</span>
              <span class="text-blue-800">Destination</span>
            </div>
            <div class="flex items-center text-sm">
              <span class="mr-2">{{ preferencesStore.hasBudget ? '✅' : '⏸️' }}</span>
              <span class="text-blue-800">Budget</span>
            </div>
            <div class="flex items-center text-sm">
              <span class="mr-2">{{ preferencesStore.hasDates ? '✅' : '⏸️' }}</span>
              <span class="text-blue-800">Dates</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Context Tab -->
      <div v-if="activeTab === 'context'" class="p-4 space-y-4">
        <h3 class="text-sm font-semibold text-gray-900">Session Context</h3>
        
        <div class="space-y-3">
          <!-- Session Info -->
          <div class="border border-gray-200 rounded-lg p-3">
            <div class="text-sm font-medium text-gray-900 mb-2">Session Information</div>
            <div class="space-y-1 text-sm text-gray-600">
              <div class="flex justify-between">
                <span>Messages:</span>
                <span>{{ chatStore.messageCount }}</span>
              </div>
              <div class="flex justify-between">
                <span>User Messages:</span>
                <span>{{ chatStore.userMessageCount }}</span>
              </div>
              <div class="flex justify-between">
                <span>Actions:</span>
                <span>{{ chatStore.recentActions.length }}</span>
              </div>
              <div class="flex justify-between">
                <span>Preferences:</span>
                <span>{{ preferencesStore.preferencesCount }}</span>
              </div>
            </div>
          </div>

          <!-- Agent Capabilities -->
          <div class="border border-gray-200 rounded-lg p-3">
            <div class="text-sm font-medium text-gray-900 mb-2">Agent Capabilities</div>
            <div class="space-y-1">
              <div class="flex items-center text-xs text-gray-600">
                <span class="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                Web Search for Travel Info
              </div>
              <div class="flex items-center text-xs text-gray-600">
                <span class="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                Flight Recommendations
              </div>
              <div class="flex items-center text-xs text-gray-600">
                <span class="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                Hotel Suggestions
              </div>
              <div class="flex items-center text-xs text-gray-600">
                <span class="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                Activity Planning
              </div>
              <div class="flex items-center text-xs text-gray-600">
                <span class="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
                Memory & Preferences
              </div>
              <div class="flex items-center text-xs text-gray-600">
                <span class="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
                Contextual Conversations
              </div>
            </div>
          </div>

          <!-- Connection Info -->
          <div class="border border-gray-200 rounded-lg p-3">
            <div class="text-sm font-medium text-gray-900 mb-2">Connection</div>
            <div class="space-y-1 text-sm text-gray-600">
              <div class="flex justify-between">
                <span>Status:</span>
                <span class="capitalize" :class="{
                  'text-green-600': chatStore.isConnected,
                  'text-yellow-600': chatStore.connectionStatus === 'connecting',
                  'text-red-600': chatStore.connectionStatus === 'disconnected'
                }">
                  {{ chatStore.connectionStatus }}
                </span>
              </div>
              <div class="flex justify-between">
                <span>Session ID:</span>
                <span class="font-mono">{{ chatStore.sessionId.slice(0, 8) }}...</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useChatStore } from '../stores/chat'
import { usePreferencesStore } from '../stores/preferences'

// Stores
const chatStore = useChatStore()
const preferencesStore = usePreferencesStore()

// State
const activeTab = ref('actions')

// Computed
const tabs = computed(() => [
  { 
    id: 'actions', 
    name: 'Actions', 
    count: chatStore.recentActions.length 
  },
  { 
    id: 'memory', 
    name: 'Memory', 
    count: preferencesStore.preferencesCount 
  },
  { 
    id: 'context', 
    name: 'Context',
    count: undefined
  }
])

const hasRecentUpdates = computed(() => 
  Object.keys(chatStore.memoryUpdates).length > 0
)

// Methods
const getActionTypeClasses = (type: string) => {
  const classes = {
    'search_flights': 'bg-blue-500 text-white',
    'search_hotels': 'bg-emerald-500 text-white',
    'search_activities': 'bg-purple-500 text-white',
    'analyze_intent': 'bg-amber-500 text-white',
    'update_memory': 'bg-indigo-500 text-white',
    'generate_response': 'bg-pink-500 text-white',
    'web_search': 'bg-orange-500 text-white',
    'analyzing_your_travel_request': 'bg-cyan-500 text-white',
    'searching_for_flights': 'bg-sky-500 text-white',
    'finding_hotels': 'bg-teal-500 text-white',
    'discovering_activities': 'bg-violet-500 text-white'
  }
  return classes[type] || 'bg-slate-500 text-white'
}

const getActionIcon = (type: string) => {
  const icons = {
    'search_flights': '✈️',
    'search_hotels': '🏨',
    'search_activities': '🎯',
    'analyze_intent': '🧠',
    'update_memory': '💾',
    'generate_response': '💬',
    'web_search': '🔍'
  }
  return icons[type] || '•'
}

const formatActionType = (type: string) => {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatPreferenceKey = (key: string) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatPreferenceValue = (value: any) => {
  if (typeof value === 'number' && value > 1000) {
    return `₹${value.toLocaleString()}`
  }
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  return String(value)
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit'
  })
}

const clearActions = () => {
  chatStore.clearActions()
}

const getPreferenceIcon = (key: string) => {
  const icons = {
    'Destination': '🌍',
    'From': '🏠',
    'Budget': '💰',
    'Dates': '📅',
    'Travelers': '👥',
    'Dietary': '🍽️',
    'Activities': '🎯',
    'Accommodation': '🏨'
  }
  return icons[key] || '📋'
}
</script>
