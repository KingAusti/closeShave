import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { useValidation } from '../hooks/useValidation'
import './SearchBar.css'

import type { SearchRequest } from '../types'

interface SearchBarProps {
  onSearch: (query: string, filters: Partial<SearchRequest>) => void
  loading: boolean
}

interface Merchant {
  name: string
  enabled: boolean
  version: string
}

const API_BASE =
  import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000')

export default function SearchBar({ onSearch, loading }: SearchBarProps) {
  const [query, setQuery] = useState('')
  const [barcode, setBarcode] = useState('')
  const [minPrice, setMinPrice] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const [brand, setBrand] = useState('')
  const [includeOutOfStock, setIncludeOutOfStock] = useState(true)
  const [searchDeals, setSearchDeals] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1)
  const [merchants, setMerchants] = useState<Merchant[]>([])
  const [selectedMerchants, setSelectedMerchants] = useState<Set<string>>(new Set())
  const [showMerchantSelection, setShowMerchantSelection] = useState(false)
  const suppressAutoShowRef = useRef(false)
  const suggestionsRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const {
    validateQueryDebounced,
    validationResult,
    loading: validating,
    clearValidation,
  } = useValidation()

  // Fetch available merchants
  useEffect(() => {
    const fetchMerchants = async () => {
      try {
        const response = await axios.get<{ merchants: Merchant[] }>(`${API_BASE}/api/merchants`)
        const enabledMerchants = response.data.merchants.filter(m => m.enabled)
        setMerchants(enabledMerchants)
        // Select all enabled merchants by default
        setSelectedMerchants(new Set(enabledMerchants.map(m => m.name)))
      } catch (error) {
        console.error('Failed to fetch merchants:', error)
        // Fallback to default merchants if API fails
        const defaultMerchants: Merchant[] = [
          { name: 'amazon', enabled: true, version: '1.0.0' },
          { name: 'ebay', enabled: true, version: '1.0.0' },
          { name: 'walmart', enabled: true, version: '1.0.0' },
          { name: 'target', enabled: true, version: '1.0.0' },
          { name: 'bestbuy', enabled: true, version: '1.0.0' },
          { name: 'newegg', enabled: true, version: '1.0.0' },
          { name: 'duckduckgo', enabled: true, version: '1.0.0' },
        ]
        setMerchants(defaultMerchants)
        setSelectedMerchants(new Set(defaultMerchants.map(m => m.name)))
      }
    }
    fetchMerchants()
  }, [])

  // Validate query as user types (debounced)
  useEffect(() => {
    if (query && !barcode) {
      validateQueryDebounced(query, 500)
      // Only auto-show suggestions if not suppressed (e.g., by clicking a suggestion)
      if (!suppressAutoShowRef.current) {
        setShowSuggestions(true)
      }
      // Reset suppression flag after handling the query change
      suppressAutoShowRef.current = false
    } else {
      clearValidation()
      setShowSuggestions(false)
      suppressAutoShowRef.current = false
    }

    // Cleanup function to abort pending requests on unmount
    return () => {
      clearValidation()
    }
  }, [query, barcode, validateQueryDebounced, clearValidation])

  // Close merchant selection when clicking outside
  useEffect(() => {
    if (!showMerchantSelection) return

    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (!target.closest('.merchant-selection-panel') && !target.closest('.merchant-selection-button')) {
        setShowMerchantSelection(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [showMerchantSelection])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const searchQuery = barcode || query
    if (!searchQuery.trim()) return

    setShowSuggestions(false)
    
    // Determine which merchants to search
    let merchantsToSearch: string[] | undefined
    if (searchDeals) {
      merchantsToSearch = ['duckduckgo']
    } else if (selectedMerchants.size > 0 && selectedMerchants.size < merchants.length) {
      merchantsToSearch = Array.from(selectedMerchants)
    } else {
      merchantsToSearch = undefined // Search all enabled merchants
    }
    
    onSearch(searchQuery, {
      barcode: barcode || undefined,
      min_price: minPrice ? parseFloat(minPrice) : undefined,
      max_price: maxPrice ? parseFloat(maxPrice) : undefined,
      brand: brand || undefined,
      include_out_of_stock: includeOutOfStock,
      merchants: merchantsToSearch,
    })
  }

  const handleSuggestionClick = (suggestion: string) => {
    // Suppress auto-showing suggestions when query is updated programmatically
    suppressAutoShowRef.current = true
    setQuery(suggestion)
    setShowSuggestions(false)
    setSelectedSuggestionIndex(-1)
    // Trigger search with suggestion
    onSearch(suggestion, {
      min_price: minPrice ? parseFloat(minPrice) : undefined,
      max_price: maxPrice ? parseFloat(maxPrice) : undefined,
      brand: brand || undefined,
      include_out_of_stock: includeOutOfStock,
    })
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestions || !validationResult?.suggestions.length) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedSuggestionIndex(prev =>
          prev < validationResult!.suggestions.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedSuggestionIndex(prev => (prev > 0 ? prev - 1 : -1))
        break
      case 'Enter':
        e.preventDefault()
        if (selectedSuggestionIndex >= 0 && selectedSuggestionIndex < validationResult!.suggestions.length) {
          handleSuggestionClick(validationResult!.suggestions[selectedSuggestionIndex])
        }
        break
      case 'Escape':
        e.preventDefault()
        setShowSuggestions(false)
        setSelectedSuggestionIndex(-1)
        inputRef.current?.blur()
        break
    }
  }

  const clearFilters = () => {
    setQuery('')
    setBarcode('')
    setMinPrice('')
    setMaxPrice('')
    setBrand('')
    setIncludeOutOfStock(true)
    setSearchDeals(false)
    setSelectedMerchants(new Set(merchants.map(m => m.name)))
    clearValidation()
  }

  const toggleMerchant = (merchantName: string) => {
    setSelectedMerchants(prev => {
      const newSet = new Set(prev)
      if (newSet.has(merchantName)) {
        newSet.delete(merchantName)
      } else {
        newSet.add(merchantName)
      }
      return newSet
    })
  }

  const selectAllMerchants = () => {
    setSelectedMerchants(new Set(merchants.map(m => m.name)))
  }

  const deselectAllMerchants = () => {
    setSelectedMerchants(new Set())
  }

  const getValidationStatus = () => {
    if (!validationResult || validating) return null
    if (validationResult.is_valid && validationResult.has_results) return 'valid'
    if (validationResult.is_valid) return 'warning'
    return 'invalid'
  }

  const validationStatus = getValidationStatus()

  return (
    <form className="search-bar" onSubmit={handleSubmit} aria-label="Product search form">
      <div className="search-input-group">
        <div
          className="search-input-wrapper"
          style={{ position: 'relative', flex: 1, minWidth: '300px' }}
        >
          <label htmlFor="search-input" className="visually-hidden">
            Search for products
          </label>
          <input
            id="search-input"
            ref={inputRef}
            type="text"
            className={`search-input neon-input ${validationStatus ? `validation-${validationStatus}` : ''}`}
            placeholder="Search for products..."
            value={query}
            onChange={e => {
              setQuery(e.target.value)
              setSelectedSuggestionIndex(-1)
            }}
            disabled={loading || !!barcode}
            onFocus={() =>
              validationResult &&
              validationResult.suggestions.length > 0 &&
              setShowSuggestions(true)
            }
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            onKeyDown={handleKeyDown}
            aria-label="Search for products"
            aria-autocomplete="list"
            aria-expanded={showSuggestions}
            aria-controls="suggestions-list"
            aria-activedescendant={
              selectedSuggestionIndex >= 0
                ? `suggestion-${selectedSuggestionIndex}`
                : undefined
            }
          />
          {validating && (
            <span
              className="validation-indicator"
              style={{
                position: 'absolute',
                right: '10px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--neon-green)',
                fontSize: '0.8rem',
              }}
              aria-live="polite"
              aria-label="Validating search query"
            >
              Validating...
            </span>
          )}
          {validationStatus && !validating && (
            <span
              className={`validation-indicator validation-${validationStatus}`}
              style={{
                position: 'absolute',
                right: '10px',
                top: '50%',
                transform: 'translateY(-50%)',
                fontSize: '0.8rem',
              }}
              title={
                validationStatus === 'valid'
                  ? 'Query looks good!'
                  : validationStatus === 'warning'
                    ? 'Query may have limited results'
                    : 'Query may not return results'
              }
              role="status"
              aria-label={
                validationStatus === 'valid'
                  ? 'Query looks good'
                  : validationStatus === 'warning'
                    ? 'Query may have limited results'
                    : 'Query may not return results'
              }
            >
              {validationStatus === 'valid' ? '✓' : validationStatus === 'warning' ? '⚠' : '✗'}
            </span>
          )}
          {showSuggestions && validationResult && validationResult.suggestions.length > 0 && (
            <div
              id="suggestions-list"
              ref={suggestionsRef}
              className="suggestions-dropdown"
              role="listbox"
              aria-label="Search suggestions"
              style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                background: 'var(--dark-panel)',
                border: '2px solid var(--neon-green)',
                borderTop: 'none',
                maxHeight: '200px',
                overflowY: 'auto',
                zIndex: 1000,
                boxShadow: '0 4px 12px rgba(0, 255, 65, 0.3)',
              }}
            >
              {validationResult.suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  id={`suggestion-${index}`}
                  className="suggestion-item"
                  role="option"
                  aria-selected={selectedSuggestionIndex === index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  onMouseEnter={() => setSelectedSuggestionIndex(index)}
                  style={{
                    padding: '0.75rem 1rem',
                    cursor: 'pointer',
                    borderBottom:
                      index < validationResult.suggestions.length - 1
                        ? '1px solid var(--dark-border)'
                        : 'none',
                    color: 'var(--text-primary)',
                    transition: 'background 0.2s',
                    background:
                      selectedSuggestionIndex === index
                        ? 'rgba(0, 255, 65, 0.1)'
                        : 'transparent',
                  }}
                >
                  {suggestion}
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="barcode-group">
          <span className="barcode-label" aria-hidden="true">or</span>
          <label htmlFor="barcode-input" className="visually-hidden">
            Barcode or UPC
          </label>
          <input
            id="barcode-input"
            type="text"
            className="barcode-input neon-input"
            placeholder="Barcode/UPC"
            value={barcode}
            onChange={e => setBarcode(e.target.value)}
            disabled={loading || !!query}
            aria-label="Barcode or UPC"
          />
        </div>
        <button
          type="submit"
          className="search-button neon-button"
          disabled={loading || (!query && !barcode)}
          aria-label={loading ? 'Searching products' : 'Search for products'}
        >
          {loading ? 'SEARCHING...' : 'SEARCH'}
        </button>
      </div>

      <div className="filters">
        <div className="filter-group">
          <label htmlFor="min-price-input">Min Price</label>
          <input
            id="min-price-input"
            type="number"
            className="filter-input neon-input"
            value={minPrice}
            onChange={e => setMinPrice(e.target.value)}
            placeholder="$0.00"
            aria-label="Minimum price filter"
            min="0"
            step="0.01"
          />
        </div>
        <div className="filter-group">
          <label htmlFor="max-price-input">Max Price</label>
          <input
            id="max-price-input"
            type="number"
            className="filter-input neon-input"
            value={maxPrice}
            onChange={e => setMaxPrice(e.target.value)}
            placeholder="$9999.99"
            aria-label="Maximum price filter"
            min="0"
            step="0.01"
          />
        </div>
        <div className="filter-group">
          <label htmlFor="brand-input">Brand</label>
          <input
            id="brand-input"
            type="text"
            className="filter-input neon-input"
            value={brand}
            onChange={e => setBrand(e.target.value)}
            placeholder="Brand name"
            aria-label="Brand filter"
          />
        </div>
        <div className="filter-group checkbox-group">
          <label>
            <input
              type="checkbox"
              checked={includeOutOfStock}
              onChange={e => setIncludeOutOfStock(e.target.checked)}
              aria-label="Include out of stock products"
            />
            Include Out of Stock
          </label>
        </div>
        <div className="filter-group checkbox-group">
          <label>
            <input
              type="checkbox"
              checked={searchDeals}
              onChange={e => {
                setSearchDeals(e.target.checked)
                if (e.target.checked) {
                  setSelectedMerchants(new Set(['duckduckgo']))
                }
              }}
              aria-label="Search deals using DuckDuckGo"
            />
            Search Deals (DuckDuckGo)
          </label>
        </div>
        <div className="filter-group">
          <button
            type="button"
            className="merchant-selection-button neon-button"
            onClick={() => setShowMerchantSelection(!showMerchantSelection)}
            aria-label="Select merchants to search"
            aria-expanded={showMerchantSelection}
          >
            {selectedMerchants.size === merchants.length
              ? 'All Merchants'
              : `${selectedMerchants.size} Merchant${selectedMerchants.size !== 1 ? 's' : ''}`}
          </button>
          {showMerchantSelection && (
            <div className="merchant-selection-panel" role="dialog" aria-label="Merchant selection">
              <div className="merchant-selection-header">
                <span>Select Merchants</span>
                <div className="merchant-selection-actions">
                  <button
                    type="button"
                    className="merchant-action-button"
                    onClick={selectAllMerchants}
                    aria-label="Select all merchants"
                  >
                    Select All
                  </button>
                  <button
                    type="button"
                    className="merchant-action-button"
                    onClick={deselectAllMerchants}
                    aria-label="Deselect all merchants"
                  >
                    Deselect All
                  </button>
                </div>
              </div>
              <div className="merchant-checkboxes">
                {merchants.map(merchant => (
                  <label key={merchant.name} className="merchant-checkbox-label">
                    <input
                      type="checkbox"
                      checked={selectedMerchants.has(merchant.name)}
                      onChange={() => toggleMerchant(merchant.name)}
                      disabled={searchDeals && merchant.name !== 'duckduckgo'}
                      aria-label={`Search ${merchant.name}`}
                    />
                    <span>
                      {merchant.name.charAt(0).toUpperCase() + merchant.name.slice(1)}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>
        <div className="filter-group">
          <button
            type="button"
            className="clear-filters-button neon-button"
            onClick={clearFilters}
            aria-label="Clear all filters"
          >
            Clear Filters
          </button>
        </div>
      </div>
    </form>
  )
}
