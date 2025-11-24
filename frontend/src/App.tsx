import { useState } from 'react'
import SearchBar from './components/SearchBar'
import ResultsGrid from './components/ResultsGrid'
import MatrixText from './components/MatrixText'
import SearchingAnimation from './components/SearchingAnimation'
import ErrorBoundary from './components/ErrorBoundary'
import { useScraper } from './hooks/useScraper'
import type { Product, SearchRequest } from './types'
import './styles/cyberpunk.css'

function App() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchKey, setSearchKey] = useState(0)
  const { searchProducts } = useScraper()

  const handleSearch = async (query: string, filters: Partial<SearchRequest>) => {
    setLoading(true)
    setError(null)
    try {
      const results = await searchProducts(query, filters)
      setProducts(results.products || [])
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to search products'
      setError(errorMessage)
      setProducts([])
    } finally {
      setLoading(false)
    }
  }

  const handleNewSearch = () => {
    setProducts([])
    setError(null)
    setSearchKey(prev => prev + 1) // Force SearchBar to reset
    // Scroll to top to show search bar
    window.scrollTo({ top: 0, behavior: 'smooth' })
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
          
          {loading ? (
            <SearchingAnimation />
          ) : (
            <SearchBar key={searchKey} onSearch={handleSearch} loading={loading} />
          )}
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          {!loading && !error && (
            <ResultsGrid products={products} onNewSearch={handleNewSearch} />
          )}
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default App

