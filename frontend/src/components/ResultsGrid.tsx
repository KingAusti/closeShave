import { useState, useMemo } from 'react'
import ProductCard from './ProductCard'
import type { Product, SearchResponse } from '../types'
import './ResultsGrid.css'

interface ResultsGridProps {
  products: Product[]
  loading: boolean
  searchMetadata?: SearchResponse | null
  searchingMerchants?: string[]
}

type SortOption = 'price-low' | 'price-high' | 'rating' | 'newest'

export default function ResultsGrid({ products, loading, searchMetadata, searchingMerchants }: ResultsGridProps) {
  const [sortBy, setSortBy] = useState<SortOption>('price-low')
  const [filterMerchant, setFilterMerchant] = useState<string>('all')
  const [filterAvailability, setFilterAvailability] = useState<string>('all')
  const [minRating, setMinRating] = useState<number>(0)

  const availableMerchants = useMemo(() => {
    const merchants = new Set(products.map(p => p.merchant))
    return Array.from(merchants).sort()
  }, [products])

  const sortedAndFilteredProducts = useMemo(() => {
    let filtered = [...products]

    // Filter by merchant
    if (filterMerchant !== 'all') {
      filtered = filtered.filter(p => p.merchant === filterMerchant)
    }

    // Filter by availability
    if (filterAvailability === 'in-stock') {
      filtered = filtered.filter(p => p.availability === 'in_stock')
    } else if (filterAvailability === 'out-of-stock') {
      filtered = filtered.filter(p => p.availability === 'out_of_stock')
    }

    // Filter by rating
    if (minRating > 0) {
      filtered = filtered.filter(p => p.rating && p.rating >= minRating)
    }

    // Sort
    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'price-low':
          return a.total_price - b.total_price
        case 'price-high':
          return b.total_price - a.total_price
        case 'rating':
          const aRating = a.rating || 0
          const bRating = b.rating || 0
          return bRating - aRating
        case 'newest':
          // Since we don't have a date field, we'll use merchant_id as a proxy
          return 0
        default:
          return 0
      }
    })

    return sorted
  }, [products, sortBy, filterMerchant, filterAvailability, minRating])

  if (loading) {
    return (
      <div className="results-grid loading" role="status" aria-label="Loading search results">
        <div className="loading-spinner">
          <div className="spinner" aria-hidden="true"></div>
          <p className="loading-text">SCANNING MERCHANTS...</p>
          {searchingMerchants && searchingMerchants.length > 0 && (
            <div className="merchant-progress" aria-live="polite">
              <p className="merchant-progress-title">Searching:</p>
              <div className="merchant-progress-list">
                {searchingMerchants.map(merchant => (
                  <span key={merchant} className="merchant-progress-item">
                    {merchant.charAt(0).toUpperCase() + merchant.slice(1)}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  if (products.length === 0) {
    return (
      <div className="results-grid empty">
        <p className="empty-message">No products found. Try a different search.</p>
        <div className="empty-suggestions">
          <p>Suggestions:</p>
          <ul>
            <li>Check your spelling</li>
            <li>Try more general search terms</li>
            <li>Remove some filters</li>
            <li>Try searching on different merchants</li>
          </ul>
        </div>
      </div>
    )
  }

  const locationInfo = searchMetadata?.location
    ? `${searchMetadata.location.city || ''}${searchMetadata.location.state ? `, ${searchMetadata.location.state}` : ''}`
    : null

  return (
    <div className="results-grid">
      <div className="results-header">
        <div className="results-title-section">
          <h2 className="results-title">FOUND {sortedAndFilteredProducts.length} PRODUCTS</h2>
          {searchMetadata && (
            <div className="search-metadata" role="status" aria-live="polite">
              <span className="metadata-item">
                Search time: {searchMetadata.search_time.toFixed(2)}s
              </span>
              {searchMetadata.cached && (
                <span className="metadata-item" title="Results from cache">
                  Cached
                </span>
              )}
              {locationInfo && (
                <span className="metadata-item" title="Location used for tax/shipping calculation">
                  Location: {locationInfo}
                </span>
              )}
            </div>
          )}
        </div>
        <div className="results-controls">
          <div className="control-group">
            <label htmlFor="sort-select" className="control-label">
              Sort by:
            </label>
            <select
              id="sort-select"
              value={sortBy}
              onChange={e => setSortBy(e.target.value as SortOption)}
              className="control-select"
              aria-label="Sort products"
            >
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
              <option value="rating">Rating: Highest First</option>
              <option value="newest">Newest First</option>
            </select>
          </div>
          <div className="control-group">
            <label htmlFor="merchant-filter" className="control-label">
              Merchant:
            </label>
            <select
              id="merchant-filter"
              value={filterMerchant}
              onChange={e => setFilterMerchant(e.target.value)}
              className="control-select"
              aria-label="Filter by merchant"
            >
              <option value="all">All Merchants</option>
              {availableMerchants.map(merchant => (
                <option key={merchant} value={merchant}>
                  {merchant.charAt(0).toUpperCase() + merchant.slice(1)}
                </option>
              ))}
            </select>
          </div>
          <div className="control-group">
            <label htmlFor="availability-filter" className="control-label">
              Availability:
            </label>
            <select
              id="availability-filter"
              value={filterAvailability}
              onChange={e => setFilterAvailability(e.target.value)}
              className="control-select"
              aria-label="Filter by availability"
            >
              <option value="all">All</option>
              <option value="in-stock">In Stock</option>
              <option value="out-of-stock">Out of Stock</option>
            </select>
          </div>
          <div className="control-group">
            <label htmlFor="rating-filter" className="control-label">
              Min Rating:
            </label>
            <select
              id="rating-filter"
              value={minRating}
              onChange={e => setMinRating(Number(e.target.value))}
              className="control-select"
              aria-label="Filter by minimum rating"
            >
              <option value="0">Any</option>
              <option value="1">1+ Stars</option>
              <option value="2">2+ Stars</option>
              <option value="3">3+ Stars</option>
              <option value="4">4+ Stars</option>
              <option value="4.5">4.5+ Stars</option>
            </select>
          </div>
        </div>
      </div>
      <div className="products-container" role="list" aria-label="Product search results">
        {sortedAndFilteredProducts.map((product, index) => (
          <ProductCard
            key={`${product.merchant}-${product.merchant_id || index}`}
            product={product}
          />
        ))}
      </div>
    </div>
  )
}
