import axios from "axios"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api"

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 150000, // 2 minutes timeout for scraping
  headers: {
    "Content-Type": "application/json",
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log("Making API request:", config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error("API Error:", error.response?.data || error.message)

    if (error.response?.status === 429) {
      throw new Error("Too many requests. Please wait a moment and try again.")
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data.error || "Invalid request")
    } else if (error.response?.status === 500) {
      throw new Error("Server error. Please try again later.")
    } else if (error.code === "ECONNABORTED") {
      throw new Error("Request timeout. The analysis is taking longer than expected.")
    }

    throw new Error(error.response?.data?.error || "Network error occurred")
  },
)

export const analyzeProductReviews = async (productUrl) => {
  try {
    const response = await api.post("/analyze", {
      url: productUrl,
    })

    return response.data
  } catch (error) {
    throw error
  }
}

export const getAnalysisHistory = async () => {
  try {
    const response = await api.get("/history")
    return response.data
  } catch (error) {
    throw error
  }
}

export const getAnalysisById = async (analysisId) => {
  try {
    const response = await api.get(`/analysis/${analysisId}`)
    return response.data
  } catch (error) {
    throw error
  }
}

export default api
