/**
 * API service for HTTP communication with backend
 */

import axios, { type AxiosInstance } from 'axios'
import type { 
  Message, 
  TravelPreferences, 
  ConversationSummary,
  SessionContext,
  APIResponse 
} from '../types'

class APIClient {
  private client: AxiosInstance
  
  constructor(baseURL: string = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL: `${baseURL}/api/v1`,
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 30000
    })
    
    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message)
        throw error
      }
    )
  }
  
  async sendMessage(sessionId: string, message: string): Promise<any> {
    const response = await this.client.post('/chat/message', {
      session_id: sessionId,
      message
    })
    return response.data
  }
  
  async getConversationHistory(sessionId: string, limit: number = 20): Promise<{
    messages: Message[]
    summary: ConversationSummary
  }> {
    const response = await this.client.get(`/chat/history/${sessionId}`, {
      params: { limit }
    })
    return response.data
  }
  
  async getContext(sessionId: string): Promise<SessionContext> {
    const response = await this.client.get(`/chat/context/${sessionId}`)
    return response.data
  }
  
  async clearSession(sessionId: string): Promise<{ status: string }> {
    const response = await this.client.delete(`/chat/session/${sessionId}`)
    return response.data
  }
  
  async healthCheck(): Promise<{
    status: string
    service: string
    version: string
  }> {
    const response = await this.client.get('/health')
    return response.data
  }
  
  async databaseHealth(): Promise<{
    status: string
    database: string
    type: string
  }> {
    const response = await this.client.get('/health/database')
    return response.data
  }
}

// Create singleton instance
export const apiClient = new APIClient()

// Environment-specific configuration
const isDevelopment = import.meta.env.DEV
const baseUrl = isDevelopment 
  ? 'http://localhost:8000'
  : 'https://your-backend-url.com' // Update with your Beanstalk URL

export const productionApiClient = new APIClient(baseUrl)
