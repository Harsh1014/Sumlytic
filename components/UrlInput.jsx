"use client"

import { useState, useEffect } from "react"

export default function UrlInput({ onAnalyze, isLoading, onCancel }) {
  const [url, setUrl] = useState("")
  const [isValidUrl, setIsValidUrl] = useState(true)
  const [supportedSites, setSupportedSites] = useState([])
  const [siteBadges, setSiteBadges] = useState([])
  const [loadingSites, setLoadingSites] = useState(true)

  useEffect(() => {
    // Load supported sites from API
    loadSupportedSites()
  }, [])

  const loadSupportedSites = async () => {
    try {
      setLoadingSites(true)
      
      // Fetch from API
      const response = await fetch('/api/websites')
      if (response.ok) {
        const data = await response.json()
        
        if (data.success && data.websites) {
          // Extract site keys for validation
          const sites = data.websites.map(site => site.key)
          setSupportedSites(sites)
          
          // Create badges for display
          const badges = data.websites
            .filter(site => site.enabled)
            .map(site => ({
              name: site.name,
              icon: site.icon,
              category: site.category?.name || '',
              description: site.description
            }))
            .sort((a, b) => a.name.localeCompare(b.name))
          
          setSiteBadges(badges)
        }
      } else {
        // Fallback to basic sites if API fails
        console.warn('Failed to load websites from API, using fallback')
        setFallbackSites()
      }
    } catch (error) {
      console.error('Failed to load supported sites:', error)
      setFallbackSites()
    } finally {
      setLoadingSites(false)
    }
  }

  const setFallbackSites = () => {
    // Fallback to basic sites
    const fallbackSites = ['amazon', 'flipkart', 'myntra', 'snapdeal']
    setSupportedSites(fallbackSites)
    
    const fallbackBadges = [
      { name: 'Amazon', icon: '🛒' },
      { name: 'Flipkart', icon: '🛒' },
      { name: 'Myntra', icon: '👕' },
      { name: 'Snapdeal', icon: '🛒' }
    ]
    setSiteBadges(fallbackBadges)
  }

  const validateUrl = (inputUrl) => {
    // Accepts http(s):// or www. at the start
    const urlPattern = /^(https?:\/\/|www\.)[^\s]+/
    if (!urlPattern.test(inputUrl)) return false
    return supportedSites.some((site) => inputUrl.toLowerCase().includes(site))
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    if (!url.trim()) {
      setIsValidUrl(false)
      return
    }

    let normalizedUrl = url.trim()
    if (normalizedUrl.startsWith('www.')) {
      normalizedUrl = 'https://' + normalizedUrl
    }
    onAnalyze(normalizedUrl)
  }

  const handleUrlChange = (e) => {
    setUrl(e.target.value)
    if (!isValidUrl) setIsValidUrl(true)
  }

  const handleCancel = () => {
    setUrl("")
    setIsValidUrl(true)
    if (onCancel) onCancel()
  }

  return (
    <div className="url-input-section">
      <form onSubmit={handleSubmit} className="url-form">
        <div className="input-group">
          <div className="input-wrapper">
            <input
              type="url"
              value={url}
              onChange={handleUrlChange}
              placeholder="Paste product URL from Amazon, Flipkart, etc."
              className={`url-input ${!isValidUrl ? "error" : ""}`}
              disabled={isLoading}
            />
            <span className="input-icon">🔗</span>
          </div>

          <button type="submit" className="analyze-button" disabled={isLoading || !url.trim()}>
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Analyzing...
              </>
            ) : (
              <>
                <span>✨</span>
                Analyze Reviews
              </>
            )}
          </button>

          {(url.trim() || isLoading) && (
            <button 
              type="button" 
              className="cancel-button compact" 
              onClick={handleCancel}
              disabled={isLoading}
            >
              <span>✕</span>
              Cancel
            </button>
          )}
        </div>

        {!isValidUrl && (
          <p className="input-error">Please enter a valid product URL from supported sites (Amazon, Flipkart, etc.)</p>
        )}
      </form>

      <div className="supported-sites">
        <span className="supported-label">
          Supported sites:
          {loadingSites && <span className="loading-indicator"> (loading...)</span>}
        </span>
        <div className="site-badges">
          {siteBadges.slice(0, 8).map((site, index) => (
            <span key={index} className="site-badge" title={site.description || site.name}>
              {site.icon} {site.name}
            </span>
          ))}
          {siteBadges.length > 8 && (
            <span className="site-badge more" title={`+${siteBadges.length - 8} more sites`}>
              +{siteBadges.length - 8} more
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
