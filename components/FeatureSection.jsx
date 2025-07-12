export default function FeatureSection() {
  const features = [
    {
      icon: "🚀",
      title: "Lightning Fast Analysis",
      description: "Get comprehensive review summaries in under 60 seconds using advanced AI processing.",
    },
    {
      icon: "🎯",
      title: "Smart Categorization",
      description: "Automatically identifies and categorizes pros, cons, and key product features.",
    },
    {
      icon: "🌐",
      title: "Multi-Platform Support",
      description: "Works with Amazon, Flipkart, Myntra, Snapdeal, and other major e-commerce sites.",
    },
    {
      icon: "📊",
      title: "Sentiment Analysis",
      description: "Advanced sentiment analysis shows the overall mood and opinion trends.",
    },
    {
      icon: "🔒",
      title: "Privacy Focused",
      description: "No personal data stored. All analysis happens securely and privately.",
    },
    {
      icon: "📤",
      title: "Export & Share",
      description: "Easily export summaries as PDF or share insights with friends and colleagues.",
    },
  ]

  return (
    <section id="features" className="features-section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Why Choose Sumlytic?</h2>
          <p className="section-subtitle">
            Save hours of reading time and make confident purchasing decisions with AI-powered insights
          </p>
        </div>

        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>

        <div className="how-it-works" id="how-it-works">
          <h3 className="subsection-title">How It Works</h3>
          <div className="steps-container">
            <div className="step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h4>Paste URL</h4>
                <p>Copy and paste any product URL from supported e-commerce sites</p>
              </div>
            </div>
            <div className="step-arrow">→</div>
            <div className="step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h4>AI Analysis</h4>
                <p>Our AI scrapes and analyzes all available reviews using advanced NLP</p>
              </div>
            </div>
            <div className="step-arrow">→</div>
            <div className="step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h4>Get Summary</h4>
                <p>Receive clear pros, cons, and insights to make informed decisions</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
