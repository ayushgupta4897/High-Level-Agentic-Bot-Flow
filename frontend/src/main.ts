/**
 * Main entry point for Travel Agent frontend
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import './style.css'

// Create Vue app
const app = createApp(App)

// Install Pinia store
const pinia = createPinia()
app.use(pinia)

// Mount app
app.mount('#app')
