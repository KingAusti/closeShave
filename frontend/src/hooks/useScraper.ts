import { useState } from 'react'
import axios from 'axios'
import type { SearchRequest, SearchResponse } from '../types'

// Use relative path when running in Docker (nginx proxies /api to backend)
// Otherwise use explicit URL for local development
const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000')

export const useScraper = () => {
  const [loading, setLoading] = useState(false)

  const searchProducts = async (
    query: string,
    filters: Partial<SearchRequest> = {}
  ): Promise<SearchResponse> => {
    setLoading(true)
    try {
      const request: SearchRequest = {
        query,
        max_results: 20,
        include_out_of_stock: true,
        ...filters
      }
      
      const response = await axios.post<SearchResponse>(
        `${API_BASE}/api/search`,
        request
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to search products')
    } finally {
      setLoading(false)
    }
  }

  return {
    searchProducts,
    loading
  }
}

