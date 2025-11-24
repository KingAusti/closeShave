export interface Product {
  title: string
  price: number
  base_price: number
  shipping_cost: number
  tax: number
  total_price: number
  image_url: string
  direct_image_url: string
  product_url: string
  merchant: string
  availability: string
  merchant_id?: string
  brand?: string
  rating?: number
  review_count?: number
}

export interface SearchRequest {
  query: string
  merchants?: string[]
  max_results?: number
  min_price?: number
  max_price?: number
  brand?: string
  barcode?: string
  include_out_of_stock?: boolean
}

export interface SearchResponse {
  products: Product[]
  total_results: number
  search_time: number
  cached: boolean
  location?: {
    country: string
    region: string
    state: string
    city: string
    zip: string
  }
}

export interface ValidationRequest {
  query: string
}

export interface ValidationResponse {
  is_valid: boolean
  has_results: boolean
  suggestions: string[]
  confidence: number
}

