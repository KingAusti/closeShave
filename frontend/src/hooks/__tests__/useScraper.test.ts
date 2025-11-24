import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import axios from 'axios'
import { useScraper, ScraperError } from '../useScraper'

// Mock axios
vi.mock('axios')
const mockedAxios = axios as unknown as {
  post: ReturnType<typeof vi.fn>
  isAxiosError: typeof axios.isAxiosError
  isCancel: typeof axios.isCancel
}

describe('useScraper', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockedAxios.isAxiosError = vi.fn((error) => error && typeof error === 'object' && 'isAxiosError' in error)
    mockedAxios.isCancel = vi.fn(() => false)
  })

  it('should initialize with loading false', () => {
    const { result } = renderHook(() => useScraper())
    expect(result.current.loading).toBe(false)
  })

  it('should throw error for empty query', async () => {
    const { result } = renderHook(() => useScraper())
    
    await expect(
      result.current.searchProducts('')
    ).rejects.toThrow(ScraperError)
    
    await expect(
      result.current.searchProducts('   ')
    ).rejects.toThrow(ScraperError)
  })

  it('should successfully search products', async () => {
    const mockResponse = {
      data: {
        products: [],
        total_results: 0,
        search_time: 0.5,
        cached: false,
      },
    }

    mockedAxios.post.mockResolvedValue(mockResponse)

    const { result } = renderHook(() => useScraper())
    
    const response = await result.current.searchProducts('laptop')
    
    expect(response).toEqual(mockResponse.data)
    expect(mockedAxios.post).toHaveBeenCalledWith(
      expect.stringContaining('/api/search'),
      expect.objectContaining({
        query: 'laptop',
        max_results: 20,
        include_out_of_stock: true,
      }),
      expect.objectContaining({
        timeout: 60000,
      })
    )
  })

  it('should handle network errors', async () => {
    const networkError = new Error('Network Error')
    mockedAxios.post.mockRejectedValue(networkError)
    mockedAxios.isAxiosError.mockReturnValue(false)

    const { result } = renderHook(() => useScraper())
    
    await expect(
      result.current.searchProducts('laptop')
    ).rejects.toThrow(ScraperError)
  })

  it('should handle axios errors with structured response', async () => {
    const axiosError = {
      response: {
        status: 400,
        data: {
          error: 'VALIDATION_ERROR',
          message: 'Invalid query',
        },
      },
      isAxiosError: true,
    }
    mockedAxios.post.mockRejectedValue(axiosError)
    mockedAxios.isAxiosError.mockReturnValue(true)

    const { result } = renderHook(() => useScraper())
    
    await expect(
      result.current.searchProducts('laptop')
    ).rejects.toThrow(ScraperError)
  })
})

