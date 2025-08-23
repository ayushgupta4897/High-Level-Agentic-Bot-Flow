/**
 * Markdown rendering composable
 */

import { marked } from 'marked'
import { ref, computed } from 'vue'

// Configure marked for clean output
marked.setOptions({
  breaks: true,
  gfm: true,
  headerIds: false,
  mangle: false
})

export function useMarkdown() {
  const renderMarkdown = (content: string): string => {
    try {
      // Clean and render markdown
      const cleaned = content
        .replace(/^\s+|\s+$/g, '') // Trim whitespace
        .replace(/\n{3,}/g, '\n\n') // Normalize line breaks
      
      return marked(cleaned) as string
    } catch (error) {
      console.error('Markdown rendering error:', error)
      return content // Fallback to plain text
    }
  }
  
  const isMarkdown = (content: string): boolean => {
    // Simple heuristic to detect markdown content
    const markdownPatterns = [
      /^\s*#+\s/, // Headers
      /\*\*.*\*\*/, // Bold
      /\*.*\*/, // Italic
      /^\s*-\s/, // Lists
      /^\s*\d+\.\s/, // Numbered lists
      /`.*`/, // Code
      /\[.*\]\(.*\)/ // Links
    ]
    
    return markdownPatterns.some(pattern => pattern.test(content))
  }
  
  return {
    renderMarkdown,
    isMarkdown
  }
}
