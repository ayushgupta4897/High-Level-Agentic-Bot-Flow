/**
 * Preferences store using Pinia
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { TravelPreferences } from '../types'

export const usePreferencesStore = defineStore('preferences', () => {
  // State
  const preferences = ref<TravelPreferences>({
    destination: undefined,
    origin: undefined,
    budget: undefined,
    dates: undefined,
    people_count: 1,
    dietary_preferences: [],
    activity_preferences: [],
    accommodation_type: undefined
  })
  
  // Getters
  const hasDestination = computed(() => !!preferences.value.destination)
  const hasBudget = computed(() => !!preferences.value.budget)
  const hasDates = computed(() => !!preferences.value.dates)
  const isComplete = computed(() => 
    hasDestination.value && hasBudget.value && hasDates.value
  )
  
  const budgetFormatted = computed(() => {
    if (!preferences.value.budget) return null
    return `₹${preferences.value.budget.toLocaleString()}`
  })
  
  const preferencesCount = computed(() => {
    return Object.values(preferences.value).filter(value => 
      value !== undefined && value !== null && 
      (Array.isArray(value) ? value.length > 0 : true)
    ).length
  })
  
  const preferencesSummary = computed(() => {
    const summary: Record<string, string | number> = {}
    
    if (preferences.value.destination) {
      summary['Destination'] = preferences.value.destination
    }
    
    if (preferences.value.origin) {
      summary['From'] = preferences.value.origin
    }
    
    if (preferences.value.budget) {
      summary['Budget'] = budgetFormatted.value || preferences.value.budget
    }
    
    if (preferences.value.dates) {
      summary['Dates'] = preferences.value.dates
    }
    
    if (preferences.value.people_count && preferences.value.people_count > 1) {
      summary['Travelers'] = preferences.value.people_count
    }
    
    if (preferences.value.dietary_preferences?.length) {
      summary['Dietary'] = preferences.value.dietary_preferences.join(', ')
    }
    
    if (preferences.value.activity_preferences?.length) {
      summary['Activities'] = preferences.value.activity_preferences.join(', ')
    }
    
    if (preferences.value.accommodation_type) {
      summary['Accommodation'] = preferences.value.accommodation_type
    }
    
    return summary
  })
  
  // Actions
  const updatePreference = <K extends keyof TravelPreferences>(
    key: K,
    value: TravelPreferences[K]
  ) => {
    preferences.value[key] = value
  }
  
  const updatePreferences = (updates: Partial<TravelPreferences>) => {
    Object.assign(preferences.value, updates)
  }
  
  const clearPreference = <K extends keyof TravelPreferences>(key: K) => {
    if (Array.isArray(preferences.value[key])) {
      preferences.value[key] = [] as any
    } else {
      preferences.value[key] = undefined as any
    }
  }
  
  const clearAllPreferences = () => {
    preferences.value = {
      destination: undefined,
      origin: undefined,
      budget: undefined,
      dates: undefined,
      people_count: 1,
      dietary_preferences: [],
      activity_preferences: [],
      accommodation_type: undefined
    }
  }
  
  const setFromMemoryUpdates = (memoryUpdates: Record<string, any>) => {
    Object.keys(memoryUpdates).forEach(key => {
      if (key in preferences.value) {
        updatePreference(key as keyof TravelPreferences, memoryUpdates[key])
      }
    })
  }
  
  return {
    // State
    preferences,
    
    // Getters
    hasDestination,
    hasBudget,
    hasDates,
    isComplete,
    budgetFormatted,
    preferencesCount,
    preferencesSummary,
    
    // Actions
    updatePreference,
    updatePreferences,
    clearPreference,
    clearAllPreferences,
    setFromMemoryUpdates
  }
})
