import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function ResultsDisplay({ results }) {
  const {
    productName = "Unknown Product",
    productImage,
    totalReviews = 0,
    averageRating = "N/A",
    summary = { pros: [], cons: [] },
    sentiment = { positive: 0, neutral: 0, negative: 0 },
    keyFeatures = [],
    price: priceRaw,
    product_price,
    productPrice
  } = results || {};

  // Prefer productPrice (from backend), then priceRaw, then product_price, else N/A
  let price = productPrice || priceRaw || product_price || null;
  
  // Format price for display
  let formattedPrice = "N/A";
  if (price && price !== "N/A" && price !== null && price !== undefined) {
    const priceStr = String(price).trim();
    if (priceStr) {
      // If price is a number or starts with a digit, add ₹ symbol
      if (/^\d/.test(priceStr)) {
        formattedPrice = `₹${priceStr}`;
      } else if (/^[₹$€£]/.test(priceStr)) {
        // If it already has a currency symbol, use as is
        formattedPrice = priceStr;
      } else {
        // Default to showing as is
        formattedPrice = priceStr;
      }
    }
  }

  return (
    <div className="results-section">
      <div className="container">
        <div className="results-header">
          <div className="product-info">
            <img 
              src={productImage}
              alt={productName}
              className="product-image large-product-image"
              style={{ width: 220, height: 220 }}
            />
            <div className="product-details">
              <h2 className="product-name">{productName}</h2>
              <div className="product-stats">
                <div className="stat">
                  <span className="stat-value">{formattedPrice}</span>
                  <span className="stat-label">Price</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{averageRating}</span>
                  <span className="stat-label">★ Rating</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{Number(totalReviews).toLocaleString()}</span>
                  <span className="stat-label">Reviews</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="results-grid">
          <div className="summary-card pros-card">
            <h3 className="card-title">
              <span className="title-icon">✅</span>
              Key Pros
            </h3>
            <ul className="pros-list">
              {summary.pros.map((pro, index) => (
                <li key={index} className="pro-item">
                  <span className="bullet-point pro-bullet">+</span>
                  {pro}
                </li>
              ))}
            </ul>
          </div>

          <div className="summary-card cons-card">
            <h3 className="card-title">
              <span className="title-icon">⚠️</span>
              Key Cons
            </h3>
            <ul className="cons-list">
              {summary.cons.map((con, index) => (
                <li key={index} className="con-item">
                  <span className="bullet-point con-bullet">-</span>
                  {con}
                </li>
              ))}
            </ul>
          </div>

          <div className="sentiment-card">
            <h3 className="card-title">
              <span className="title-icon">📊</span>
              Sentiment Analysis
            </h3>
            <div className="sentiment-chart">
              <div className="sentiment-bar">
                <div className="sentiment-fill positive" style={{ width: `${sentiment.positive}%` }}></div>
                <div className="sentiment-fill neutral" style={{ width: `${sentiment.neutral}%` }}></div>
                <div className="sentiment-fill negative" style={{ width: `${sentiment.negative}%` }}></div>
              </div>
              <div className="sentiment-legend">
                <div className="legend-item">
                  <span className="legend-color positive"></span>
                  <span>Positive ({sentiment.positive}%)</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color neutral"></span>
                  <span>Neutral ({sentiment.neutral}%)</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color negative"></span>
                  <span>Negative ({sentiment.negative}%)</span>
                </div>
              </div>
            </div>
            {/* Sentiment Bar Chart */}
            <div style={{ width: '100%', height: 180, marginTop: 24 }}>
              <ResponsiveContainer>
                <BarChart data={[
                  { name: 'Positive', value: sentiment.positive },
                  { name: 'Neutral', value: sentiment.neutral },
                  { name: 'Negative', value: sentiment.negative },
                ]}>
                  <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 14 }} />
                  <YAxis stroke="#94a3b8" tick={{ fontSize: 14 }} domain={[0, 100]} />
                  <Tooltip />
                  <Bar dataKey="value">
                    <Cell fill="#22c55e" />
                    <Cell fill="#3b82f6" />
                    <Cell fill="#ef4444" />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="features-card">
            <h3 className="card-title">
              <span className="title-icon">🏷️</span>
              Most Mentioned Features
            </h3>
            <div className="features-list">
              {keyFeatures.map((feature, index) => (
                <div key={index} className="feature-item">
                  <div className="feature-header">
                    <span className="feature-name">{feature.feature}</span>
                    <span className={`feature-sentiment ${feature.sentiment}`}>
                      {feature.sentiment === "positive" ? "😊" : feature.sentiment === "negative" ? "😞" : "😐"}
                    </span>
                  </div>
                  <div className="feature-mentions">
                    <div className="mentions-bar">
                      <div className="mentions-fill" style={{ width: `${feature.mentions}%` }}></div>
                    </div>
                    <span className="mentions-count">{feature.mentions} mentions</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* <div className="action-buttons">
          <button className="action-button primary">
            <span>📋</span>
            Copy Summary
          </button>
          <button className="action-button secondary">
            <span>📤</span>
            Share Results
          </button>
          <button className="action-button secondary">
            <span>💾</span>
            Save Report
          </button>
        </div> */}
      </div>
    </div>
  );
}
