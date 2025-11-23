import { useState } from 'react'
import './SearchBar.css'

interface SearchBarProps {
  onSearch: (query: string, filters: any) => void
  loading: boolean
}

export default function SearchBar({ onSearch, loading }: SearchBarProps) {
  const [query, setQuery] = useState('')
  const [barcode, setBarcode] = useState('')
  const [minPrice, setMinPrice] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const [brand, setBrand] = useState('')
  const [includeOutOfStock, setIncludeOutOfStock] = useState(true)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const searchQuery = barcode || query
    if (!searchQuery.trim()) return

    onSearch(searchQuery, {
      barcode: barcode || undefined,
      min_price: minPrice ? parseFloat(minPrice) : undefined,
      max_price: maxPrice ? parseFloat(maxPrice) : undefined,
      brand: brand || undefined,
      include_out_of_stock: includeOutOfStock
    })
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <div className="search-input-group">
        <input
          type="text"
          className="search-input neon-input"
          placeholder="Search for products..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading || !!barcode}
        />
        <div className="barcode-group">
          <span className="barcode-label">or</span>
          <input
            type="text"
            className="barcode-input neon-input"
            placeholder="Barcode/UPC"
            value={barcode}
            onChange={(e) => setBarcode(e.target.value)}
            disabled={loading || !!query}
          />
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
          <label>Min Price</label>
          <input
            type="number"
            className="filter-input neon-input"
            value={minPrice}
            onChange={(e) => setMinPrice(e.target.value)}
            placeholder="$0.00"
          />
        </div>
        <div className="filter-group">
          <label>Max Price</label>
          <input
            type="number"
            className="filter-input neon-input"
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
            placeholder="$9999.99"
          />
        </div>
        <div className="filter-group">
          <label>Brand</label>
          <input
            type="text"
            className="filter-input neon-input"
            value={brand}
            onChange={(e) => setBrand(e.target.value)}
            placeholder="Brand name"
          />
        </div>
        <div className="filter-group checkbox-group">
          <label>
            <input
              type="checkbox"
              checked={includeOutOfStock}
              onChange={(e) => setIncludeOutOfStock(e.target.checked)}
            />
            Include Out of Stock
          </label>
        </div>
      </div>
    </form>
  )
}

