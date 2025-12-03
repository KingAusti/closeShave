import { useState, useEffect, useRef } from 'react'
import SearchBar from './components/SearchBar'
import ResultsGrid from './components/ResultsGrid'
import MatrixText from './components/MatrixText'
import ErrorBoundary from './components/ErrorBoundary'
import Modal from './components/Modal'
import { useScraper } from './hooks/useScraper'
import type { Product, SearchRequest, SearchResponse } from './types'
import './styles/cyberpunk.css'

function App() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [searchMetadata, setSearchMetadata] = useState<SearchResponse | null>(null)
  const [lastSearchQuery, setLastSearchQuery] = useState<string>('')
  const [lastSearchFilters, setLastSearchFilters] = useState<Partial<SearchRequest>>({})
  const [searchingMerchants, setSearchingMerchants] = useState<string[]>([])
  const announcementRef = useRef<HTMLDivElement>(null)
  const { searchProducts } = useScraper()

  const handleSearch = async (query: string, filters: Partial<SearchRequest>) => {
    setLoading(true)
    setError(null)
    setLastSearchQuery(query)
    setLastSearchFilters(filters)
    setSearchMetadata(null)
    
    // Set merchants being searched for progress indicator
    if (filters.merchants && filters.merchants.length > 0) {
      setSearchingMerchants(filters.merchants)
    } else {
      // If no specific merchants, show default list
      setSearchingMerchants(['amazon', 'ebay', 'walmart', 'target', 'bestbuy', 'newegg', 'duckduckgo'])
    }
    
    // Announce search start to screen readers
    if (announcementRef.current) {
      announcementRef.current.textContent = `Searching for ${query}...`
    }
    
    try {
      const results = await searchProducts(query, filters)
      setProducts(results.products || [])
      setSearchMetadata(results)
      setSearchingMerchants([])
      
      // Announce results to screen readers
      if (announcementRef.current) {
        const count = results.products?.length || 0
        announcementRef.current.textContent = `Found ${count} product${count !== 1 ? 's' : ''} for ${query}`
      }
    } catch (err) {
      setSearchingMerchants([])
      const errorMessage = err instanceof Error ? err.message : 'Failed to search products'
      let userFriendlyMessage = errorMessage
      
      // Make error messages more user-friendly
      if (errorMessage.includes('timeout') || errorMessage.includes('timed out')) {
        userFriendlyMessage = 'The search took too long. Please try again with a more specific query or fewer merchants.'
      } else if (errorMessage.includes('Network error') || errorMessage.includes('connection')) {
        userFriendlyMessage = 'Unable to connect to the server. Please check your internet connection and try again.'
      } else if (errorMessage.includes('validation') || errorMessage.includes('empty')) {
        userFriendlyMessage = 'Please enter a search query to find products.'
      }
      
      setError(userFriendlyMessage)
      setModalOpen(true)
      setProducts([])
      
      // Announce error to screen readers
      if (announcementRef.current) {
        announcementRef.current.textContent = `Search failed: ${userFriendlyMessage}`
      }
    } finally {
      setLoading(false)
    }
  }

  const handleRetry = () => {
    setModalOpen(false)
    if (lastSearchQuery) {
      handleSearch(lastSearchQuery, lastSearchFilters)
    }
  }

  return (
    <ErrorBoundary>
      <div className="app">
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        <div
          ref={announcementRef}
          className="visually-hidden"
          role="status"
          aria-live="polite"
          aria-atomic="true"
        />
        <div className="matrix-background">
          <MatrixText />
        </div>
        <div className="content" id="main-content">
          <header className="header">
            <h1 className="title glitch" data-text="CloseShave">
              CloseShave
            </h1>
            <p className="subtitle">Find the cheapest products across all merchants</p>
          </header>

          <SearchBar onSearch={handleSearch} loading={loading} />

          <Modal
            isOpen={modalOpen}
            onClose={() => setModalOpen(false)}
            onRetry={handleRetry}
            title="Search Error"
            type="error"
          >
            {error}
          </Modal>

          <ResultsGrid
            products={products}
            loading={loading}
            searchMetadata={searchMetadata}
            searchingMerchants={searchingMerchants}
          />
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default App
