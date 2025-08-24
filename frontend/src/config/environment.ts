/**
 * Environment configuration for different deployment stages
 * Supports both build-time (Vite) and runtime (Docker) configuration
 */

interface EnvironmentConfig {
  apiBaseUrl: string
  appTitle: string
  environment: 'development' | 'production' | 'staging'
  isDevelopment: boolean
  isProduction: boolean
  version: string
  buildTime?: string
}

// Runtime configuration from Docker container (if available)
declare global {
  interface Window {
    APP_CONFIG?: {
      API_BASE_URL: string
      APP_TITLE: string
      APP_ENV: string
      VERSION: string
      BUILD_TIME: string
    }
  }
}

// Get environment variables (runtime first, then build-time)
const getEnvVar = (key: string, runtimeKey?: string, defaultValue: string = ''): string => {
  // Check runtime config first (Docker container)
  if (typeof window !== 'undefined' && window.APP_CONFIG && runtimeKey) {
    const runtimeValue = (window.APP_CONFIG as any)[runtimeKey]
    if (runtimeValue) return runtimeValue
  }
  
  // Fall back to build-time config (Vite)
  return import.meta.env[key] || defaultValue
}

// Determine the current environment
const isDevelopment = import.meta.env.DEV
const isProduction = import.meta.env.PROD

// Default URLs for different environments
const AZURE_BACKEND_URL = 'http://4.187.163.17:8000'
const LOCAL_BACKEND_URL = 'http://localhost:8000'
const DEV_SERVER_URL = 'http://localhost:8000'  // For Vite dev server

// Configuration based on environment
export const config: EnvironmentConfig = {
  apiBaseUrl: getEnvVar('VITE_API_BASE_URL', 'API_BASE_URL') || (isProduction ? AZURE_BACKEND_URL : DEV_SERVER_URL),
  appTitle: getEnvVar('VITE_APP_TITLE', 'APP_TITLE') || (isProduction ? 'Travel Agent' : 'Travel Agent - Dev'),
  environment: getEnvVar('VITE_APP_ENV', 'APP_ENV', isProduction ? 'production' : 'development') as any,
  version: getEnvVar('VITE_APP_VERSION', 'VERSION', '1.0.0'),
  buildTime: getEnvVar('VITE_BUILD_TIME', 'BUILD_TIME'),
  isDevelopment,
  isProduction
}

// Export individual values for convenience
export const {
  apiBaseUrl,
  appTitle,
  environment,
  isDevelopment,
  isProduction
} = config

// Debug info (only in development)
if (isDevelopment) {
  console.log('🔧 Environment Config:', config)
}
