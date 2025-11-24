import { useState, useCallback, useRef } from 'react'
import axios from 'axios'
import type { ValidationRequest, ValidationResponse } from '../types'

// Use relative path when running in Docker (nginx proxies /api to backend)
// Otherwise use explicit URL for local development
const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000')

export const useValidation = () => {
  const [loading, setLoading] = useState(false)
  const [validationResult, setValidationResult] = useState<ValidationResponse | null>(null)
  const debounceTimer = useRef<NodeJS.Timeout | null>(null)
  const cache = useRef<Map<string, ValidationResponse>>(new Map())

  const validateQuery = useCallback(
    async (query: string): Promise<ValidationResponse> => {
      if (!query || !query.trim()) {
        const emptyResult: ValidationResponse = {
          is_valid: false,
          has_results: false,
          suggestions: [],
          confidence: 0.0
        }
        setValidationResult(emptyResult)
        return emptyResult
      }

      const trimmedQuery = query.trim()

      // Check cache first
      if (cache.current.has(trimmedQuery)) {
        const cached = cache.current.get(trimmedQuery)!
        setValidationResult(cached)
        return cached
      }

      setLoading(true)
      try {
        const request: ValidationRequest = {
          query: trimmedQuery
        }

        const response = await axios.post<ValidationResponse>(
          `${API_BASE}/api/validate`,
          request
        )

        // Cache the result
        cache.current.set(trimmedQuery, response.data)
        setValidationResult(response.data)
        return response.data
      } catch (error: any) {
        // Return permissive result on error (don't block searches)
        const errorResult: ValidationResponse = {
          is_valid: true,
          has_results: false,
          suggestions: [],
          confidence: 0.5
        }
        setValidationResult(errorResult)
        return errorResult
      } finally {
        setLoading(false)
      }
    },
    []
  )

  const validateQueryDebounced = useCallback(
    (query: string, delay: number = 500) => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current)
      }

      debounceTimer.current = setTimeout(() => {
        validateQuery(query)
      }, delay)
    },
    [validateQuery]
  )

  const clearValidation = useCallback(() => {
    setValidationResult(null)
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
      debounceTimer.current = null
    }
  }, [])

  return {
    validateQuery,
    validateQueryDebounced,
    clearValidation,
    validationResult,
    loading
  }
}

