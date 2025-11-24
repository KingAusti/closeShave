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
  const abortControllerRef = useRef<AbortController | null>(null)
  const currentQueryRef = useRef<string | null>(null)

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
        currentQueryRef.current = null
        return emptyResult
      }

      const trimmedQuery = query.trim()
      
      // Cancel any in-flight request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
      
      // Track the current query being validated
      currentQueryRef.current = trimmedQuery

      // Check cache first
      if (cache.current.has(trimmedQuery)) {
        const cached = cache.current.get(trimmedQuery)!
        // Only update state if this is still the current query
        if (currentQueryRef.current === trimmedQuery) {
          setValidationResult(cached)
        }
        return cached
      }

      // Create new AbortController for this request
      const abortController = new AbortController()
      abortControllerRef.current = abortController

      setLoading(true)
      try {
        const request: ValidationRequest = {
          query: trimmedQuery
        }

        const response = await axios.post<ValidationResponse>(
          `${API_BASE}/api/validate`,
          request,
          {
            signal: abortController.signal
          }
        )

        // Only update state if this is still the current query
        if (currentQueryRef.current === trimmedQuery) {
          // Cache the result
          cache.current.set(trimmedQuery, response.data)
          setValidationResult(response.data)
        }
        return response.data
      } catch (error: any) {
        // Ignore abort/cancellation errors
        const isCancelled = 
          axios.isCancel(error) || 
          error.name === 'AbortError' || 
          error.name === 'CanceledError' ||
          error.code === 'ERR_CANCELED'
        
        if (isCancelled) {
          // Request was cancelled, return a neutral result
          return {
            is_valid: true,
            has_results: false,
            suggestions: [],
            confidence: 0.5
          }
        }
        
        // Only update state on real errors if this is still the current query
        if (currentQueryRef.current === trimmedQuery) {
          // Return permissive result on error (don't block searches)
          const errorResult: ValidationResponse = {
            is_valid: true,
            has_results: false,
            suggestions: [],
            confidence: 0.5
          }
          setValidationResult(errorResult)
          return errorResult
        }
        
        // Return default result for cancelled/stale requests
        return {
          is_valid: true,
          has_results: false,
          suggestions: [],
          confidence: 0.5
        }
      } finally {
        // Only update loading state if this is still the current query
        if (currentQueryRef.current === trimmedQuery) {
          setLoading(false)
        }
        // Clear abort controller if this was the current request
        if (abortControllerRef.current === abortController) {
          abortControllerRef.current = null
        }
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
    // Cancel any in-flight request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    
    // Clear current query tracking
    currentQueryRef.current = null
    
    setValidationResult(null)
    setLoading(false)
    
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

