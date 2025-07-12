import { useEffect, useState } from "react"

export default function LoadingState({ currentStep, isLoading, done }) {
  const steps = [
    { id: 1, icon: "🔍", text: "Scraping product reviews..." },
    { id: 2, icon: "🤖", text: "Processing with AI..." },
    { id: 3, icon: "📊", text: "Generating summary..." },
  ]

  // Animated progress state
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    let interval
    if (isLoading && !done) {
      setProgress(0)
      interval = setInterval(() => {
        setProgress((prev) => {
          // Go up to 90% while loading
          if (prev < 90) return prev + Math.random() * 2 + 1
          return prev
        })
      }, 120)
    } else if (done) {
      setProgress(100)
    } else {
      setProgress(0)
    }
    return () => clearInterval(interval)
  }, [isLoading, done])

  // Clamp progress
  const percent = Math.min(Math.round(progress), 100)

  return (
    <div className="loading-section">
      <div className="container">
        <div className="loading-content">
          <div className="classic-progress-bar-wrapper">
            <div className="classic-progress-bar-bg">
              <div
                className="classic-progress-bar-fill"
                style={{ width: `${percent}%` }}
              ></div>
            </div>
            <div className="classic-progress-label">{percent}%</div>
          </div>

          <h3 className="loading-title">Analyzing Reviews</h3>

          <div className="loading-steps">
            {steps.map((step) => (
              <div key={step.id} className={`loading-step ${currentStep >= step.id ? "active" : ""}`}>
                <span className="step-icon">{step.icon}</span>
                <span className="step-text">{step.text}</span>
                {currentStep === step.id && <div className="step-spinner"></div>}
              </div>
            ))}
          </div>

          <p className="loading-subtitle">This may take 30-60 seconds depending on the number of reviews</p>
        </div>
      </div>
    </div>
  )
}
