import { useState } from 'react'
import SearchBar from './components/SearchBar'
import ResultsGrid from './components/ResultsGrid'
import MatrixText from './components/MatrixText'
import ErrorBoundary from './components/ErrorBoundary'
import { useScraper } from './hooks/useScraper'
import type { Product } from './types'
import './styles/cyberpunk.css'

function App() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { searchProducts } = useScraper()

  const handleSearch = async (query: string, filters: any) => {
    setLoading(true)
    setError(null)
    try {
      const results = await searchProducts(query, filters)
      setProducts(results.products || [])
    } catch (err: any) {
      setError(err.message || 'Failed to search products')
      setProducts([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <ErrorBoundary>
      <div className="app">
        <div className="matrix-background">
          <MatrixText />
        </div>
        <div className="content">
          <header className="header">
            <h1 className="title glitch" data-text="CloseShave">
              CloseShave
            </h1>
            <p className="subtitle">Find the cheapest products across all merchants</p>
          </header>
          
          <SearchBar onSearch={handleSearch} loading={loading} />
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          <ResultsGrid products={products} loading={loading} />
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default App

