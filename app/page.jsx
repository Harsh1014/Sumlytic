"use client"

import { useState, useRef } from "react"
import Header from "@/components/Header"
import UrlInput from "@/components/UrlInput"
import LoadingState from "@/components/LoadingState"
import ResultsDisplay from "@/components/ResultsDisplay"
import FeatureSection from "@/components/FeatureSection"
import Footer from "@/components/Footer"
import { analyzeProductReviews } from "@/services/api"

export default function Home() {
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [loadingStep, setLoadingStep] = useState(0)
  const loadingRef = useRef(null)

  const handleAnalyze = async (url) => {
    setIsLoading(true)
    setError(null)
    setResults(null)
    setLoadingStep(0)

    // Scroll to loading section
    setTimeout(() => {
      if (loadingRef.current) {
        loadingRef.current.scrollIntoView({ behavior: "smooth" })
      }
    }, 100)

    try {
      // Step 1: Scraping
      setLoadingStep(1)

      // Step 2: AI Processing
      setTimeout(() => setLoadingStep(2), 2000)

      // Step 3: Generating Summary
      setTimeout(() => setLoadingStep(3), 4000)

      const data = await analyzeProductReviews(url)
      setResults(data)
    } catch (err) {
      setError(err.message || "Failed to analyze reviews. Please try again.")
    } finally {
      setIsLoading(false)
      setLoadingStep(0)
    }
  }

  return (
    <div className="app">
      <Header />

      <main className="main-content">
        <div className="hero-section">
          <div className="container">
            <h1 className="hero-title">Smart Review Summarizer</h1>
            <p className="hero-subtitle">
            Transform customer reviews into actionable insights with our AI-powered analysis tool. Get comprehensive sentiment analysis, feature breakdowns, and market intelligence in seconds.
            </p>

            <UrlInput onAnalyze={handleAnalyze} isLoading={isLoading} onCancel={() => {
              setResults(null)
              setError(null)
              setIsLoading(false)
              setLoadingStep(0)
            }} />

            {error && (
              <div className="error-message">
                <span className="error-icon">⚠️</span>
                {error}
              </div>
            )}
          </div>
        </div>

        <div ref={loadingRef} />
        {isLoading && <LoadingState currentStep={loadingStep} isLoading={isLoading} done={!!results || !!error} />}

        {results && <ResultsDisplay results={results} />}

        {!isLoading && !results && <FeatureSection />}
      </main>

      <Footer />
    </div>
  )
}
