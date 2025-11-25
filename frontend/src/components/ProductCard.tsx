import { useState } from 'react'
import GlitchEffect from './GlitchEffect'
import type { Product } from '../types'
import './ProductCard.css'

interface ProductCardProps {
  product: Product
}

export default function ProductCard({ product }: ProductCardProps) {
  const [showDetails, setShowDetails] = useState(false)
  const isOutOfStock = product.availability === 'out_of_stock'

  const imageUrl = product.image_url
    ? `/api/image-proxy?url=${encodeURIComponent(product.image_url)}`
    : ''

  return (
    <div className={`product-card ${isOutOfStock ? 'out-of-stock' : ''}`}>
      {isOutOfStock && (
        <div className="out-of-stock-badge">
          <GlitchEffect text="OUT OF STOCK" />
        </div>
      )}

      <div className="product-image-container">
        <img
          src={imageUrl || product.direct_image_url}
          alt={product.title}
          className="product-image"
          onError={e => {
            ;(e.target as HTMLImageElement).src = product.direct_image_url
          }}
        />
        <div className="merchant-badge">{product.merchant.toUpperCase()}</div>
      </div>

      <div className="product-info">
        <h3 className="product-title">{product.title}</h3>

        <div className="product-pricing">
          <div className="price-breakdown">
            <div className="price-item">
              <span className="price-label">Base:</span>
              <span className="price-value">${product.base_price.toFixed(2)}</span>
            </div>
            {product.shipping_cost > 0 && (
              <div className="price-item">
                <span className="price-label">Shipping:</span>
                <span className="price-value">${product.shipping_cost.toFixed(2)}</span>
              </div>
            )}
            {product.tax > 0 && (
              <div className="price-item">
                <span className="price-label">Tax:</span>
                <span className="price-value">${product.tax.toFixed(2)}</span>
              </div>
            )}
          </div>

          <div className="total-price">
            <span className="total-label">TOTAL:</span>
            <span className="total-value neon-text">${product.total_price.toFixed(2)}</span>
          </div>
        </div>

        <button
          className="product-link-button neon-button"
          onClick={() => window.open(product.product_url, '_blank')}
        >
          VIEW ON {product.merchant.toUpperCase()}
        </button>

        {showDetails && (
          <div className="product-details">
            {product.brand && (
              <p>
                <strong>Brand:</strong> {product.brand}
              </p>
            )}
            {product.rating && (
              <p>
                <strong>Rating:</strong> {product.rating}/5 ({product.review_count} reviews)
              </p>
            )}
            <p>
              <strong>Availability:</strong> {product.availability}
            </p>
          </div>
        )}

        <button className="details-toggle" onClick={() => setShowDetails(!showDetails)}>
          {showDetails ? 'Hide Details' : 'Show Details'}
        </button>
      </div>
    </div>
  )
}
