import { useState } from 'react'
import axios, { AxiosError } from 'axios'
import type { SearchRequest, SearchResponse } from '../types'

// Use relative path when running in Docker (nginx proxies /api to backend)
// Otherwise use explicit URL for local development
// In dev mode, Vite proxy handles /api requests, so use empty string
// In prod mode, nginx proxy handles /api requests, so use empty string
// Only use explicit URL if VITE_API_URL is explicitly set
const API_BASE = import.meta.env.VITE_API_URL || ''

export class ScraperError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public errorCode?: string,
    public details?: unknown
  ) {
    super(message)
    this.name = 'ScraperError'
  }
}

export const useScraper = () => {
  const [loading, setLoading] = useState(false)

  const searchProducts = async (
    query: string,
    filters: Partial<SearchRequest> = {}
  ): Promise<SearchResponse> => {
    if (!query || !query.trim()) {
      throw new ScraperError('Search query cannot be empty', 400, 'VALIDATION_ERROR')
    }

    setLoading(true)
    try {
      const request: SearchRequest = {
        query: query.trim(),
        max_results: 20,
        include_out_of_stock: true,
        ...filters
      }
      
      const response = await axios.post<SearchResponse>(
        `${API_BASE}/api/search`,
        request,
        {
          timeout: 60000, // 60 second timeout for searches
        }
      )
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<{ error?: string; message?: string; detail?: string }>
        const statusCode = axiosError.response?.status
        const errorData = axiosError.response?.data
        
        // Handle structured error responses
        if (errorData?.error || errorData?.message || errorData?.detail) {
          const message = errorData.message || errorData.detail || errorData.error || 'Failed to search products'
          throw new ScraperError(
            message,
            statusCode,
            errorData.error,
            errorData
          )
        }
        
        // Handle network errors
        if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
          throw new ScraperError(
            'Request timed out. Please try again.',
            408,
            'TIMEOUT_ERROR'
          )
        }
        
        if (error.code === 'ERR_NETWORK' || !error.response) {
          throw new ScraperError(
            'Network error. Please check your connection.',
            0,
            'NETWORK_ERROR'
          )
        }
        
        // Generic HTTP error
        throw new ScraperError(
          `Search failed: ${error.message}`,
          statusCode,
          'HTTP_ERROR'
        )
      }
      
      // Unknown error
      throw new ScraperError(
        error instanceof Error ? error.message : 'An unexpected error occurred',
        500,
        'UNKNOWN_ERROR'
      )
    } finally {
      setLoading(false)
    }
  }

  return {
    searchProducts,
    loading
  }
}

