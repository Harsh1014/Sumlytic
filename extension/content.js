// Content script for Review Summarizer Chrome Extension

class ReviewSummarizerExtension {
  constructor() {
    this.apiUrl = "http://localhost:5000/api"
    this.isAnalyzing = false
    this.init()
  }

  init() {
    this.detectPlatform()
    this.injectSummarizeButton()
    this.setupMessageListener()
  }

  detectPlatform() {
    const hostname = window.location.hostname.toLowerCase()

    if (hostname.includes("amazon")) {
      this.platform = "amazon"
    } else if (hostname.includes("flipkart")) {
      this.platform = "flipkart"
    } else if (hostname.includes("myntra")) {
      this.platform = "myntra"
    } else if (hostname.includes("snapdeal")) {
      this.platform = "snapdeal"
    } else {
      this.platform = "unknown"
    }
  }

  injectSummarizeButton() {
    if (this.platform === "unknown") return

    // Remove existing button if any
    const existingButton = document.getElementById("review-summarizer-btn")
    if (existingButton) {
      existingButton.remove()
    }

    const button = this.createSummarizeButton()
    const targetElement = this.findButtonContainer()

    if (targetElement) {
      targetElement.appendChild(button)
    }
  }

  createSummarizeButton() {
    const button = document.createElement("button")
    button.id = "review-summarizer-btn"
    button.className = "review-summarizer-button"
    button.innerHTML = `
      <span class="button-icon">✨</span>
      <span class="button-text">Summarize Reviews</span>
    `

    button.addEventListener("click", () => this.handleSummarizeClick())

    return button
  }

  findButtonContainer() {
    let selectors = []

    switch (this.platform) {
      case "amazon":
        selectors = ["#buybox", "#rightCol", "#apex_desktop", ".a-section.a-spacing-none"]
        break
      case "flipkart":
        selectors = ["._1YokD2._2GoDe3", "._1AtVbE", ".col-5-12"]
        break
      case "myntra":
        selectors = [".pdp-actions-container", ".pdp-add-to-bag"]
        break
      case "snapdeal":
        selectors = [".buy-button-container", ".product-price-row"]
        break
    }

    for (const selector of selectors) {
      const element = document.querySelector(selector)
      if (element) {
        return element
      }
    }

    // Fallback: append to body
    return document.body
  }

  async handleSummarizeClick() {
    if (this.isAnalyzing) return

    const button = document.getElementById("review-summarizer-btn")
    this.setButtonLoading(button, true)
    this.isAnalyzing = true

    try {
      const currentUrl = window.location.href
      const result = await this.analyzeReviews(currentUrl)

      if (result.success) {
        this.showSummaryModal(result.data)
      } else {
        this.showError(result.error)
      }
    } catch (error) {
      this.showError("Failed to analyze reviews. Please try again.")
    } finally {
      this.setButtonLoading(button, false)
      this.isAnalyzing = false
    }
  }

  setButtonLoading(button, loading) {
    const icon = button.querySelector(".button-icon")
    const text = button.querySelector(".button-text")

    if (loading) {
      icon.textContent = "⏳"
      text.textContent = "Analyzing..."
      button.disabled = true
      button.classList.add("loading")
    } else {
      icon.textContent = "✨"
      text.textContent = "Summarize Reviews"
      button.disabled = false
      button.classList.remove("loading")
    }
  }

  async analyzeReviews(url) {
    try {
      const response = await fetch(`${this.apiUrl}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        return { success: false, error: errorData.error || "Analysis failed" }
      }

      const data = await response.json()
      return { success: true, data }
    } catch (error) {
      return { success: false, error: "Network error occurred" }
    }
  }

  showSummaryModal(data) {
    // Remove existing modal
    const existingModal = document.getElementById("review-summary-modal")
    if (existingModal) {
      existingModal.remove()
    }

    const modal = this.createSummaryModal(data)
    document.body.appendChild(modal)

    // Show modal with animation
    setTimeout(() => {
      modal.classList.add("show")
    }, 10)
  }

  createSummaryModal(data) {
    const modal = document.createElement("div")
    modal.id = "review-summary-modal"
    modal.className = "review-summary-modal"

    modal.innerHTML = `
      <div class="modal-overlay"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h2>Review Summary</h2>
          <button class="close-button" onclick="this.closest('.review-summary-modal').remove()">×</button>
        </div>
        
        <div class="modal-body">
          <div class="product-info">
            <img src="${data.product_image || "/placeholder.svg"}" alt="Product" class="product-image">
            <div class="product-details">
              <h3>${data.product_name}</h3>
              <div class="product-stats">
                <span class="rating">★ ${data.average_rating?.toFixed(1) || "N/A"}</span>
                <span class="reviews-count">${data.total_reviews} reviews</span>
              </div>
            </div>
          </div>

          <div class="summary-sections">
            <div class="pros-section">
              <h4>✅ Key Pros</h4>
              <ul class="pros-list">
                ${data.summary.pros.map((pro) => `<li>${pro}</li>`).join("")}
              </ul>
            </div>

            <div class="cons-section">
              <h4>⚠️ Key Cons</h4>
              <ul class="cons-list">
                ${data.summary.cons.map((con) => `<li>${con}</li>`).join("")}
              </ul>
            </div>

            <div class="sentiment-section">
              <h4>📊 Sentiment Analysis</h4>
              <div class="sentiment-bar">
                <div class="sentiment-positive" style="width: ${data.sentiment.positive}%"></div>
                <div class="sentiment-neutral" style="width: ${data.sentiment.neutral}%"></div>
                <div class="sentiment-negative" style="width: ${data.sentiment.negative}%"></div>
              </div>
              <div class="sentiment-legend">
                <span class="positive">Positive (${data.sentiment.positive}%)</span>
                <span class="neutral">Neutral (${data.sentiment.neutral}%)</span>
                <span class="negative">Negative (${data.sentiment.negative}%)</span>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" onclick="this.closest('.review-summary-modal').remove()">Close</button>
          <button class="btn-primary" onclick="navigator.clipboard.writeText(this.getAttribute('data-summary'))">Copy Summary</button>
        </div>
      </div>
    `

    // Add click outside to close
    modal.querySelector(".modal-overlay").addEventListener("click", () => {
      modal.remove()
    })

    return modal
  }

  showError(message) {
    const errorDiv = document.createElement("div")
    errorDiv.className = "review-summarizer-error"
    errorDiv.innerHTML = `
      <div class="error-content">
        <span class="error-icon">⚠️</span>
        <span class="error-message">${message}</span>
        <button class="error-close" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
    `

    document.body.appendChild(errorDiv)

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (errorDiv.parentElement) {
        errorDiv.remove()
      }
    }, 5000)
  }

  setupMessageListener() {
    window.chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === "summarize") {
        this.handleSummarizeClick()
      }
    })
  }
}

// Initialize extension when page loads
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    new ReviewSummarizerExtension()
  })
} else {
  new ReviewSummarizerExtension()
}
