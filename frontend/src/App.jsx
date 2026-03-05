import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [cuisines, setCuisines] = useState([])
  const [locations, setLocations] = useState([])
  const [loadingMeta, setLoadingMeta] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [summary, setSummary] = useState('')

  const [form, setForm] = useState({
    cuisine: 'Any',
    location: 'Any',
    price_range: 'Any',
    min_rating: '',
    num_recommendations: 5,
    additional_preferences: '',
  })

  useEffect(() => {
    let cancelled = false
    Promise.all([
      fetch(`${API_BASE}/api/cuisines`).then(r => r.ok ? r.json() : []),
      fetch(`${API_BASE}/api/locations`).then(r => r.ok ? r.json() : []),
    ])
      .then(([c, l]) => {
        if (!cancelled) {
          setCuisines(['Any', ...(c || [])])
          setLocations(['Any', ...(l || [])])
          setError(null)
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setCuisines(['Any'])
          setLocations(['Any'])
          setError('Cannot reach API. Start the backend first: run "python3 -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000" in the project root.')
        }
      })
      .finally(() => { if (!cancelled) setLoadingMeta(false) })
    return () => { cancelled = true }
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    setRecommendations([])
    setSummary('')
    const payload = {
      cuisine: form.cuisine === 'Any' ? null : form.cuisine,
      location: form.location === 'Any' ? null : form.location,
      price_range: form.price_range === 'Any' ? null : form.price_range,
      min_rating: form.min_rating === '' ? null : parseFloat(form.min_rating),
      num_recommendations: form.num_recommendations,
      additional_preferences: form.additional_preferences || '',
    }
    try {
      const res = await fetch(`${API_BASE}/api/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Request failed')
      setRecommendations(data.recommendations || [])
      setSummary(data.summary || '')
    } catch (err) {
      setError(err.message || 'Could not fetch recommendations.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="hero">
        <div className="hero-bg" />
        <div className="hero-content">
          <div className="brand">zomato</div>
          <h1>Restaurant Recommendations</h1>
          <p>Set your preferences and get personalized picks powered by AI.</p>
        </div>
      </header>

      <main className="main">
        {error && (
          <div className="card error-card error-card--connection">
            <p>{error}</p>
          </div>
        )}
        <form className="card form-card" onSubmit={handleSubmit}>
          <h2>Your preferences</h2>
          {loadingMeta && <p className="meta-loading">Loading options…</p>}
          <div className="form-grid">
            <label>
              <span>Cuisine</span>
              <select
                value={form.cuisine}
                onChange={(e) => setForm((f) => ({ ...f, cuisine: e.target.value }))}
                disabled={loadingMeta}
              >
                {cuisines.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </label>
            <label>
              <span>Location</span>
              <select
                value={form.location}
                onChange={(e) => setForm((f) => ({ ...f, location: e.target.value }))}
                disabled={loadingMeta}
              >
                {locations.map((loc) => (
                  <option key={loc} value={loc}>{loc}</option>
                ))}
              </select>
            </label>
            <label>
              <span>Price range</span>
              <select
                value={form.price_range}
                onChange={(e) => setForm((f) => ({ ...f, price_range: e.target.value }))}
              >
                <option value="Any">Any</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="very_high">Very high</option>
              </select>
            </label>
            <label>
              <span>Min rating (0–5)</span>
              <input
                type="number"
                min="0"
                max="5"
                step="0.5"
                placeholder="Any"
                value={form.min_rating}
                onChange={(e) => setForm((f) => ({ ...f, min_rating: e.target.value }))}
              />
            </label>
            <label>
              <span>Number of results</span>
              <input
                type="number"
                min="1"
                max="20"
                value={form.num_recommendations}
                onChange={(e) => setForm((f) => ({ ...f, num_recommendations: parseInt(e.target.value, 10) || 5 }))}
              />
            </label>
          </div>
          <label className="full-width">
            <span>Extra preferences (optional)</span>
            <input
              type="text"
              placeholder="e.g. vegetarian, outdoor seating"
              value={form.additional_preferences}
              onChange={(e) => setForm((f) => ({ ...f, additional_preferences: e.target.value }))}
            />
          </label>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Finding restaurants…' : 'Get recommendations'}
          </button>
        </form>

        {summary && (
          <div className="card summary-card">
            <h3>Summary</h3>
            <p>{summary}</p>
          </div>
        )}

        {recommendations.length > 0 && (
          <section className="results">
            <h2>Recommendations</h2>
            <div className="results-grid">
              {recommendations.map((rec, i) => (
                <article key={i} className="card rec-card">
                  <div className="rec-header">
                    <span className="rec-number">{i + 1}</span>
                    <h3>{rec.name}</h3>
                  </div>
                  <div className="rec-meta">
                    <span className="chip">{rec.cuisine}</span>
                    <span className="chip">{rec.location}</span>
                    <span className="rating">★ {rec.rating}</span>
                    <span className="price">{rec.price_range}</span>
                  </div>
                  {rec.reason && <p className="rec-reason">{rec.reason}</p>}
                </article>
              ))}
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <p><span className="brand-footer">zomato</span> · AI Restaurant Recommendation · Data from Zomato dataset</p>
      </footer>
    </div>
  )
}

export default App
