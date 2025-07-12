"use client"

import { useState, useEffect } from "react"

export default function WebsiteManager() {
  const [websites, setWebsites] = useState([])
  const [categories, setCategories] = useState({})
  const [scrapers, setScrapers] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const [newWebsite, setNewWebsite] = useState({
    key: '',
    name: '',
    domains: [''],
    patterns: [''],
    category: 'ecommerce',
    scraper: 'universal',
    enabled: true,
    priority: 3,
    description: '',
    icon: '🌐'
  })

  useEffect(() => {
    loadWebsites()
  }, [])

  const loadWebsites = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch('/api/websites')
      if (response.ok) {
        const data = await response.json()
        
        if (data.success) {
          setWebsites(data.websites || [])
          setCategories(data.categories || {})
          setScrapers(data.scrapers || {})
        } else {
          setError('Failed to load websites')
        }
      } else {
        setError('Failed to load websites')
      }
    } catch (error) {
      console.error('Error loading websites:', error)
      setError('Failed to load websites')
    } finally {
      setLoading(false)
    }
  }

  const handleEnableWebsite = async (websiteKey) => {
    try {
      const response = await fetch(`/api/websites/${websiteKey}/enable`, {
        method: 'POST'
      })
      
      if (response.ok) {
        await loadWebsites() // Reload the list
      } else {
        setError('Failed to enable website')
      }
    } catch (error) {
      console.error('Error enabling website:', error)
      setError('Failed to enable website')
    }
  }

  const handleDisableWebsite = async (websiteKey) => {
    try {
      const response = await fetch(`/api/websites/${websiteKey}/disable`, {
        method: 'POST'
      })
      
      if (response.ok) {
        await loadWebsites() // Reload the list
      } else {
        setError('Failed to disable website')
      }
    } catch (error) {
      console.error('Error disabling website:', error)
      setError('Failed to disable website')
    }
  }

  const handleRemoveWebsite = async (websiteKey) => {
    if (!confirm(`Are you sure you want to remove ${websiteKey}?`)) {
      return
    }
    
    try {
      const response = await fetch(`/api/websites/${websiteKey}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        await loadWebsites() // Reload the list
      } else {
        setError('Failed to remove website')
      }
    } catch (error) {
      console.error('Error removing website:', error)
      setError('Failed to remove website')
    }
  }

  const handleAddWebsite = async (e) => {
    e.preventDefault()
    
    try {
      const response = await fetch('/api/websites', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          key: newWebsite.key,
          config: {
            name: newWebsite.name,
            domains: newWebsite.domains.filter(d => d.trim()),
            patterns: newWebsite.patterns.filter(p => p.trim()),
            category: newWebsite.category,
            scraper: newWebsite.scraper,
            enabled: newWebsite.enabled,
            priority: newWebsite.priority,
            description: newWebsite.description,
            icon: newWebsite.icon
          }
        })
      })
      
      if (response.ok) {
        setShowAddForm(false)
        setNewWebsite({
          key: '',
          name: '',
          domains: [''],
          patterns: [''],
          category: 'ecommerce',
          scraper: 'universal',
          enabled: true,
          priority: 3,
          description: '',
          icon: '🌐'
        })
        await loadWebsites() // Reload the list
      } else {
        const errorData = await response.json()
        setError(errorData.error || 'Failed to add website')
      }
    } catch (error) {
      console.error('Error adding website:', error)
      setError('Failed to add website')
    }
  }

  const addDomain = () => {
    setNewWebsite(prev => ({
      ...prev,
      domains: [...prev.domains, '']
    }))
  }

  const removeDomain = (index) => {
    setNewWebsite(prev => ({
      ...prev,
      domains: prev.domains.filter((_, i) => i !== index)
    }))
  }

  const updateDomain = (index, value) => {
    setNewWebsite(prev => ({
      ...prev,
      domains: prev.domains.map((d, i) => i === index ? value : d)
    }))
  }

  const addPattern = () => {
    setNewWebsite(prev => ({
      ...prev,
      patterns: [...prev.patterns, '']
    }))
  }

  const removePattern = (index) => {
    setNewWebsite(prev => ({
      ...prev,
      patterns: prev.patterns.filter((_, i) => i !== index)
    }))
  }

  const updatePattern = (index, value) => {
    setNewWebsite(prev => ({
      ...prev,
      patterns: prev.patterns.map((p, i) => i === index ? value : p)
    }))
  }

  if (loading) {
    return <div className="loading">Loading websites...</div>
  }

  return (
    <div className="website-manager">
      <div className="manager-header">
        <h2>Website Manager</h2>
        <button 
          className="add-button"
          onClick={() => setShowAddForm(true)}
        >
          + Add Website
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <div className="websites-list">
        {websites.map((website) => (
          <div key={website.key} className="website-item">
            <div className="website-info">
              <span className="website-icon">{website.icon}</span>
              <div className="website-details">
                <h3>{website.name}</h3>
                <p className="website-key">Key: {website.key}</p>
                <p className="website-description">{website.description}</p>
                <div className="website-meta">
                  <span className="category">
                    {website.category?.icon} {website.category?.name}
                  </span>
                  <span className="scraper">
                    {website.scraper?.name}
                  </span>
                  <span className="priority">
                    Priority: {website.priority}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="website-actions">
              {website.enabled ? (
                <button 
                  className="disable-button"
                  onClick={() => handleDisableWebsite(website.key)}
                  title="Disable website"
                >
                  Disable
                </button>
              ) : (
                <button 
                  className="enable-button"
                  onClick={() => handleEnableWebsite(website.key)}
                  title="Enable website"
                >
                  Enable
                </button>
              )}
              
              <button 
                className="remove-button"
                onClick={() => handleRemoveWebsite(website.key)}
                title="Remove website"
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>

      {showAddForm && (
        <div className="add-form-overlay">
          <div className="add-form">
            <h3>Add New Website</h3>
            <form onSubmit={handleAddWebsite}>
              <div className="form-group">
                <label>Website Key:</label>
                <input
                  type="text"
                  value={newWebsite.key}
                  onChange={(e) => setNewWebsite(prev => ({ ...prev, key: e.target.value }))}
                  placeholder="e.g., mywebsite"
                  required
                />
              </div>

              <div className="form-group">
                <label>Display Name:</label>
                <input
                  type="text"
                  value={newWebsite.name}
                  onChange={(e) => setNewWebsite(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., My Website"
                  required
                />
              </div>

              <div className="form-group">
                <label>Description:</label>
                <input
                  type="text"
                  value={newWebsite.description}
                  onChange={(e) => setNewWebsite(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Brief description"
                />
              </div>

              <div className="form-group">
                <label>Icon:</label>
                <input
                  type="text"
                  value={newWebsite.icon}
                  onChange={(e) => setNewWebsite(prev => ({ ...prev, icon: e.target.value }))}
                  placeholder="🌐"
                />
              </div>

              <div className="form-group">
                <label>Domains:</label>
                {newWebsite.domains.map((domain, index) => (
                  <div key={index} className="input-group">
                    <input
                      type="text"
                      value={domain}
                      onChange={(e) => updateDomain(index, e.target.value)}
                      placeholder="e.g., mywebsite.com"
                      required
                    />
                    <button 
                      type="button" 
                      onClick={() => removeDomain(index)}
                      className="remove-input"
                    >
                      ✕
                    </button>
                  </div>
                ))}
                <button type="button" onClick={addDomain} className="add-input">
                  + Add Domain
                </button>
              </div>

              <div className="form-group">
                <label>URL Patterns:</label>
                {newWebsite.patterns.map((pattern, index) => (
                  <div key={index} className="input-group">
                    <input
                      type="text"
                      value={pattern}
                      onChange={(e) => updatePattern(index, e.target.value)}
                      placeholder="e.g., /product/"
                      required
                    />
                    <button 
                      type="button" 
                      onClick={() => removePattern(index)}
                      className="remove-input"
                    >
                      ✕
                    </button>
                  </div>
                ))}
                <button type="button" onClick={addPattern} className="add-input">
                  + Add Pattern
                </button>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Category:</label>
                  <select
                    value={newWebsite.category}
                    onChange={(e) => setNewWebsite(prev => ({ ...prev, category: e.target.value }))}
                  >
                    {Object.entries(categories).map(([key, cat]) => (
                      <option key={key} value={key}>
                        {cat.icon} {cat.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Scraper:</label>
                  <select
                    value={newWebsite.scraper}
                    onChange={(e) => setNewWebsite(prev => ({ ...prev, scraper: e.target.value }))}
                  >
                    {Object.entries(scrapers).map(([key, scraper]) => (
                      <option key={key} value={key}>
                        {scraper.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Priority:</label>
                  <input
                    type="number"
                    value={newWebsite.priority}
                    onChange={(e) => setNewWebsite(prev => ({ ...prev, priority: parseInt(e.target.value) }))}
                    min="1"
                    max="10"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={newWebsite.enabled}
                    onChange={(e) => setNewWebsite(prev => ({ ...prev, enabled: e.target.checked }))}
                  />
                  Enabled
                </label>
              </div>

              <div className="form-actions">
                <button type="submit" className="submit-button">
                  Add Website
                </button>
                <button 
                  type="button" 
                  className="cancel-button"
                  onClick={() => setShowAddForm(false)}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
} 