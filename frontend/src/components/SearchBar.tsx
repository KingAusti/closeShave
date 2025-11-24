import { useState, useEffect, useRef } from 'react'
import { useValidation } from '../hooks/useValidation'
import './SearchBar.css'

import type { SearchRequest } from '../types'

interface SearchBarProps {
  onSearch: (query: string, filters: Partial<SearchRequest>) => void
  loading: boolean
}

export default function SearchBar({ onSearch, loading }: SearchBarProps) {
  const [query, setQuery] = useState('')
  const [barcode, setBarcode] = useState('')
  const [minPrice, setMinPrice] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const [brand, setBrand] = useState('')
  const [includeOutOfStock, setIncludeOutOfStock] = useState(true)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const suppressAutoShowRef = useRef(false)
  
  const { validateQueryDebounced, validationResult, loading: validating, clearValidation } = useValidation()

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const searchQuery = barcode || query
    if (!searchQuery.trim()) return

    setShowSuggestions(false)
    onSearch(searchQuery, {
      barcode: barcode || undefined,
      min_price: minPrice ? parseFloat(minPrice) : undefined,
      max_price: maxPrice ? parseFloat(maxPrice) : undefined,
      brand: brand || undefined,
      include_out_of_stock: includeOutOfStock
    })
  }

  const handleSuggestionClick = (suggestion: string) => {
    // Suppress auto-showing suggestions when query is updated programmatically
    suppressAutoShowRef.current = true
    setQuery(suggestion)
    setShowSuggestions(false)
    // Trigger search with suggestion
    onSearch(suggestion, {
      min_price: minPrice ? parseFloat(minPrice) : undefined,
      max_price: maxPrice ? parseFloat(maxPrice) : undefined,
      brand: brand || undefined,
      include_out_of_stock: includeOutOfStock
    })
  }

  const getValidationStatus = () => {
    if (!validationResult || validating) return null
    if (validationResult.is_valid && validationResult.has_results) return 'valid'
    if (validationResult.is_valid) return 'warning'
    return 'invalid'
  }

  const validationStatus = getValidationStatus()

  const bothFieldsEmpty = !query && !barcode

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      {bothFieldsEmpty && (
        <div className="requirement-notice">
          <span className="requirement-asterisk">*</span>
          <span className="requirement-text">Either Product Search OR Barcode is required</span>
        </div>
      )}
      <div className="search-input-group">
        <div className="search-input-wrapper" style={{ position: 'relative', flex: 1, minWidth: '300px' }}>
          <label className="field-label">
            Product Search
            <span className="help-text">Enter a product name, description, or keywords</span>
          </label>
          <input
            type="text"
            className={`search-input neon-input ${validationStatus ? `validation-${validationStatus}` : ''} ${bothFieldsEmpty ? 'required-empty' : ''}`}
            placeholder="Search for products..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading || !!barcode}
            onFocus={() => validationResult && validationResult.suggestions.length > 0 && setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          />
          {validating && (
            <span className="validation-indicator" style={{ 
              position: 'absolute', 
              right: '10px', 
              top: '50%', 
              transform: 'translateY(-50%)',
              color: 'var(--neon-green)',
              fontSize: '0.8rem'
            }}>
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
                fontSize: '0.8rem'
              }}
              title={
                validationStatus === 'valid' ? 'Query looks good!' :
                validationStatus === 'warning' ? 'Query may have limited results' :
                'Query may not return results'
              }
            >
              {validationStatus === 'valid' ? '✓' : validationStatus === 'warning' ? '⚠' : '✗'}
            </span>
          )}
          {showSuggestions && validationResult && validationResult.suggestions.length > 0 && (
            <div className="suggestions-dropdown" style={{
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
              boxShadow: '0 4px 12px rgba(0, 255, 65, 0.3)'
            }}>
              {validationResult.suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="suggestion-item"
                  onClick={() => handleSuggestionClick(suggestion)}
                  style={{
                    padding: '0.75rem 1rem',
                    cursor: 'pointer',
                    borderBottom: index < validationResult.suggestions.length - 1 ? '1px solid var(--dark-border)' : 'none',
                    color: 'var(--text-primary)',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(0, 255, 65, 0.1)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'transparent'
                  }}
                >
                  {suggestion}
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="barcode-group">
          <span className="barcode-label">or</span>
          <div className="barcode-wrapper">
            <label className="field-label">
              Barcode/UPC
              <span className="help-text">Enter product barcode or UPC code</span>
            </label>
            <input
              type="text"
              className={`barcode-input neon-input ${bothFieldsEmpty ? 'required-empty' : ''}`}
              placeholder="Barcode/UPC"
              value={barcode}
              onChange={(e) => setBarcode(e.target.value)}
              disabled={loading || !!query}
            />
          </div>
        </div>
        <button
          type="submit"
          className="search-button neon-button"
          disabled={loading || (!query && !barcode)}
        >
          {loading ? 'SEARCHING...' : 'SEARCH'}
        </button>
      </div>
      
      <div className="filters">
        <div className="filter-group">
          <label className="field-label">
            Min Price
            <span className="help-text">Minimum price filter (optional)</span>
          </label>
          <input
            type="number"
            className="filter-input neon-input"
            value={minPrice}
            onChange={(e) => setMinPrice(e.target.value)}
            placeholder="$0.00"
            min="0"
            step="0.01"
          />
        </div>
        <div className="filter-group">
          <label className="field-label">
            Max Price
            <span className="help-text">Maximum price filter (optional)</span>
          </label>
          <input
            type="number"
            className="filter-input neon-input"
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
            placeholder="$9999.99"
            min="0"
            step="0.01"
          />
        </div>
        <div className="filter-group">
          <label className="field-label">
            Brand
            <span className="help-text">Filter by specific brand (optional)</span>
          </label>
          <input
            type="text"
            className="filter-input neon-input"
            value={brand}
            onChange={(e) => setBrand(e.target.value)}
            placeholder="Brand name"
          />
        </div>
        <div className="filter-group checkbox-group">
          <label className="field-label">
            <input
              type="checkbox"
              checked={includeOutOfStock}
              onChange={(e) => setIncludeOutOfStock(e.target.checked)}
            />
            Include Out of Stock
            <span className="help-text">Show products that are currently out of stock</span>
          </label>
        </div>
      </div>
    </form>
  )
}

