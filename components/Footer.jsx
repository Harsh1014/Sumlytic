export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-section">
            <div className="footer-logo">
              {/* <span className="logo-icon">🔍</span> */}
              <span className="logo-text">Sumlytic</span><br/>
              <span className="logo-slogan">From Smart People, To Smart Decisions.</span>
            </div>
            <p className="footer-description">
              Making online shopping decisions easier with AI-powered review analysis. 
              Get instant insights from product reviews across multiple platforms.
            </p>
            <div className="footer-social">
              <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="social-link">
                <span>🐦</span>
              </a>
              <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="social-link">
                <span>📦</span>
              </a>
              <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="social-link">
                <span>💼</span>
              </a>
              <a href="mailto:contact@reviewsummarizer.com" className="social-link">
                <span>📧</span>
              </a>
            </div>
          </div>

          <div className="footer-section">
            <h4 className="footer-title">Product</h4>
            <ul className="footer-links">
              <li>
                <a href="#features">✨ Features</a>
              </li>
              <li>
                <a href="#how-it-works">🔄 How it Works</a>
              </li>
              <li>
                <a href="#extension">🔌 Chrome Extension</a>
              </li>
              <li>
                <a href="#api">🔑 API Access</a>
              </li>
              <li>
                <a href="#pricing">💰 Pricing</a>
              </li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 className="footer-title">Support</h4>
            <ul className="footer-links">
              <li>
                <a href="#help">❓ Help Center</a>
              </li>
              <li>
                <a href="#contact">📞 Contact Us</a>
              </li>
              <li>
                <a href="#feedback">💬 Feedback</a>
              </li>
              <li>
                <a href="#status">📊 System Status</a>
              </li>
              <li>
                <a href="#docs">📚 Documentation</a>
              </li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 className="footer-title">Legal</h4>
            <ul className="footer-links">
              <li>
                <a href="#privacy">🔒 Privacy Policy</a>
              </li>
              <li>
                <a href="#terms">📋 Terms of Service</a>
              </li>
              <li>
                <a href="#cookies">🍪 Cookie Policy</a>
              </li>
              <li>
                <a href="#gdpr">🇪🇺 GDPR</a>
              </li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <div className="footer-copyright">
            <p>&copy; 2024 ReviewSummarizer. All rights reserved.</p>
            <p className="footer-version">Version 1.0.0</p>
          </div>
          <div className="footer-actions">
            <a href="#newsletter" className="footer-action-link">
              📧 Subscribe to Newsletter
            </a>
            <a href="#status" className="footer-action-link">
              📊 System Status
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}
