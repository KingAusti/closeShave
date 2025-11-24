import ProductCard from './ProductCard'
import type { Product } from '../types'
import './ResultsGrid.css'

interface ResultsGridProps {
  products: Product[]
  onNewSearch?: () => void
}

export default function ResultsGrid({ products, onNewSearch }: ResultsGridProps) {
  if (products.length === 0) {
    return (
      <div className="results-grid empty">
        <p className="empty-message">No products found. Try a different search.</p>
      </div>
    )
  }

  return (
    <div className="results-grid">
      <div className="results-header">
        <h2 className="results-title">FOUND {products.length} PRODUCTS</h2>
        <p className="results-subtitle">Sorted by total price (cheapest first)</p>
        {onNewSearch && (
          <button 
            className="new-search-button neon-button"
            onClick={onNewSearch}
            type="button"
          >
            NEW SEARCH
          </button>
        )}
      </div>
      <div className="products-container">
        {products.map((product, index) => (
          <ProductCard key={`${product.merchant}-${product.merchant_id || index}`} product={product} />
        ))}
      </div>
    </div>
  )
}

