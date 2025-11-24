import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import SearchBar from '../SearchBar'

describe('SearchBar', () => {
  const mockOnSearch = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render search input', () => {
    render(<SearchBar onSearch={mockOnSearch} loading={false} />)
    
    const searchInput = screen.getByPlaceholderText(/search/i)
    expect(searchInput).toBeInTheDocument()
  })

  it('should call onSearch when form is submitted', async () => {
    render(<SearchBar onSearch={mockOnSearch} loading={false} />)
    
    const searchInput = screen.getByPlaceholderText(/search/i)
    const submitButton = screen.getByRole('button', { name: /search/i })

    fireEvent.change(searchInput, { target: { value: 'laptop' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledWith(
        'laptop',
        expect.objectContaining({
          include_out_of_stock: true,
        })
      )
    })
  })

  it('should not call onSearch with empty query', () => {
    render(<SearchBar onSearch={mockOnSearch} loading={false} />)
    
    const submitButton = screen.getByRole('button', { name: /search/i })
    fireEvent.click(submitButton)

    expect(mockOnSearch).not.toHaveBeenCalled()
  })

  it('should disable submit button when loading', () => {
    render(<SearchBar onSearch={mockOnSearch} loading={true} />)
    
    const submitButton = screen.getByRole('button', { name: /search/i })
    expect(submitButton).toBeDisabled()
  })
})

