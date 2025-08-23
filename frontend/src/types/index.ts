/**
 * TypeScript types for Travel Agent Frontend
 */

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  isError?: boolean
}

export interface SSEEvent {
  type: string
  timestamp: string
  [key: string]: any
}

export interface AgentAction {
  action_type: string
  description: string
  timestamp: string
  data?: Record<string, any>
}

export interface MemoryUpdate {
  updates: Record<string, any>
}

export interface TravelPreferences {
  destination?: string
  origin?: string
  budget?: number
  dates?: string
  people_count?: number
  dietary_preferences?: string[]
  activity_preferences?: string[]
  accommodation_type?: string
}

export interface ConversationSummary {
  total_messages: number
  user_messages: number
  preferences_count: number
  has_destination: boolean
  has_budget: boolean
  has_dates: boolean
  last_user_message?: string
  session_start?: string
}

export interface SessionContext {
  session_id: string
  preferences: TravelPreferences
  conversation: ConversationSummary
}

export interface ChatState {
  messages: Message[]
  isTyping: boolean
  agentActions: AgentAction[]
  memoryUpdates: Record<string, any>
}

export interface APIResponse<T = any> {
  data: T
  status: number
  message?: string
}

export interface ErrorResponse {
  error: string
  detail?: string
  timestamp: string
}
