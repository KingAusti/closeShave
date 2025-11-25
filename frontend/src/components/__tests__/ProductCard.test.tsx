import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ProductCard from '../ProductCard'
import type { Product } from '../../types'

const mockProduct: Product = {
    id: '1',
    title: 'Test Product',
    merchant: 'amazon',
    product_url: 'https://amazon.com/product',
    image_url: 'https://amazon.com/image.jpg',
    direct_image_url: 'https://amazon.com/image.jpg',
    base_price: 100,
    shipping_cost: 10,
    tax: 5,
    total_price: 115,
    availability: 'in_stock',
    brand: 'Test Brand',
    rating: 4.5,
    review_count: 100,
    timestamp: '2023-01-01T00:00:00Z'
}

describe('ProductCard', () => {
    it('renders product details correctly', () => {
        render(<ProductCard product={mockProduct} />)

        expect(screen.getByText('Test Product')).toBeInTheDocument()
        expect(screen.getByText('AMAZON')).toBeInTheDocument()
        expect(screen.getByText('$100.00')).toBeInTheDocument()
        expect(screen.getByText('$115.00')).toBeInTheDocument()
    })

    it('shows out of stock badge when unavailable', () => {
        const outOfStockProduct = { ...mockProduct, availability: 'out_of_stock' }
        render(<ProductCard product={outOfStockProduct} />)

        expect(screen.getByText('OUT OF STOCK')).toBeInTheDocument()
    })

    it('toggles details when button is clicked', () => {
        render(<ProductCard product={mockProduct} />)

        const toggleButton = screen.getByText('Show Details')
        fireEvent.click(toggleButton)

        expect(screen.getByText('Brand:')).toBeInTheDocument()
        expect(screen.getByText('Test Brand')).toBeInTheDocument()
        expect(screen.getByText('Hide Details')).toBeInTheDocument()

        fireEvent.click(screen.getByText('Hide Details'))
        expect(screen.queryByText('Brand:')).not.toBeInTheDocument()
    })
})
