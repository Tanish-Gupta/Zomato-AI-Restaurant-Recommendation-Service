import { useState, useEffect, useMemo } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const PRICE_ORDER = { low: 1, medium: 2, high: 3, very_high: 4 }
const PAGE_SIZE_OPTIONS = [5, 10, 20, 50]

const CARD_IMAGES = [
  'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=280&fit=crop',
  'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400&h=280&fit=crop',
  'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&h=280&fit=crop',
  'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400&h=280&fit=crop',
  'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=280&fit=crop',
  'https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=400&h=280&fit=crop',
  'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=400&h=280&fit=crop',
  'https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=400&h=280&fit=crop',
]

function App() {
  const [cuisines, setCuisines] = useState(['Any'])
  const [locations, setLocations] = useState(['Any'])
  const [loadingMeta, setLoadingMeta] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [summary, setSummary] = useState('')
  const [sortBy, setSortBy] = useState('default')
  const [pageSize, setPageSize] = useState(10)
  const [currentPage, setCurrentPage] = useState(1)

  const [form, setForm] = useState({
    cuisine: 'Any',
    location: 'Any',
    price_range: 'Any',
    min_rating: '',
    num_recommendations: 10,
    additional_preferences: '',
  })

  // Load cuisines once on mount
  useEffect(() => {
    let cancelled = false
    fetch(`${API_BASE}/api/cuisines`)
      .then(r => r.ok ? r.json() : [])
      .then(c => {
        if (!cancelled) setCuisines(['Any', ...(c || [])])
      })
      .catch(() => { if (!cancelled) setCuisines(['Any']) })
      .finally(() => { if (!cancelled) setLoadingMeta(false) })
    return () => { cancelled = true }
  }, [])

  // Load locations when cuisine changes: after selecting a cuisine, show only locations that have that cuisine
  useEffect(() => {
    let cancelled = false
    const cuisineParam = form.cuisine && form.cuisine !== 'Any' ? `?cuisine=${encodeURIComponent(form.cuisine)}` : ''
    fetch(`${API_BASE}/api/locations${cuisineParam}`)
      .then(r => r.ok ? r.json() : [])
      .then(l => {
        if (!cancelled) {
          const list = ['Any', ...(l || [])]
          setLocations(list)
          setForm(f => (f.location && !list.includes(f.location) ? { ...f, location: 'Any' } : f))
        }
      })
      .catch(() => { if (!cancelled) setLocations(['Any']) })
    return () => { cancelled = true }
  }, [form.cuisine])

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
      const recs = data.recommendations || []
      setRecommendations(recs)
      setSummary(data.summary || (recs.length === 0 ? 'No restaurants match your criteria. Try relaxing filters (e.g. cuisine or location).' : '') || '')
    } catch (err) {
      setError(err.message || 'Could not fetch recommendations.')
    } finally {
      setLoading(false)
    }
  }

  const sortedRecommendations = useMemo(() => {
    if (!recommendations.length) return []
    const list = [...recommendations]
    if (sortBy === 'default') return list
    if (sortBy === 'rating_desc') return list.sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0))
    if (sortBy === 'rating_asc') return list.sort((a, b) => (a.rating ?? 0) - (b.rating ?? 0))
    if (sortBy === 'price_asc') return list.sort((a, b) => (PRICE_ORDER[a.price_range?.toLowerCase()] ?? 2) - (PRICE_ORDER[b.price_range?.toLowerCase()] ?? 2))
    if (sortBy === 'price_desc') return list.sort((a, b) => (PRICE_ORDER[b.price_range?.toLowerCase()] ?? 2) - (PRICE_ORDER[a.price_range?.toLowerCase()] ?? 2))
    return list
  }, [recommendations, sortBy])

  const totalPages = Math.max(1, Math.ceil(sortedRecommendations.length / pageSize))
  const start = (currentPage - 1) * pageSize
  const paginatedRecs = useMemo(() => sortedRecommendations.slice(start, start + pageSize), [sortedRecommendations, start, pageSize])

  useEffect(() => {
    setCurrentPage(1)
  }, [sortBy, recommendations.length])

  const topCuisines = cuisines.filter((c) => c !== 'Any').slice(0, 14)

  return (
    <div className="app">
      <nav className="nav">
        <a href="#" className="nav-brand" onClick={(e) => { e.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }); }}>zomato</a>
        <div className="nav-links">
          <a href="#" className="active" onClick={(e) => e.preventDefault()}>Recommendations</a>
        </div>
      </nav>

      <header className="hero">
        <div className="hero-content">
          <h1>Find your <span className="highlight">favourite</span> restaurants</h1>
          <p className="hero-sub">Set preferences, get personalized picks powered by AI.</p>
        </div>
      </header>

      <main className="main">
        {error && (
          <div className="card error-card error-card--connection">
            <p>{error}</p>
          </div>
        )}

        {!loadingMeta && topCuisines.length > 0 && (
          <div className="cuisine-carousel">
            <h3>Quick pick cuisine</h3>
            <div className="cuisine-scroll">
              <button type="button" className={`cuisine-chip ${form.cuisine === 'Any' ? 'active' : ''}`} onClick={() => setForm((f) => ({ ...f, cuisine: 'Any' }))}>
                Any
              </button>
              {topCuisines.map((c) => (
                <button type="button" key={c} className={`cuisine-chip ${form.cuisine === c ? 'active' : ''}`} onClick={() => setForm((f) => ({ ...f, cuisine: c }))}>
                  {c}
                </button>
              ))}
            </div>
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
              <span>Number of results (max 50)</span>
              <input
                type="number"
                min="1"
                max="50"
                value={form.num_recommendations}
                onChange={(e) => setForm((f) => ({ ...f, num_recommendations: Math.min(50, Math.max(1, parseInt(e.target.value, 10) || 5)) }))}
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
            {loading ? (
              'Finding restaurants…'
            ) : (
              <>
                <span aria-hidden>🔍</span>
                Get recommendations
              </>
            )}
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
            <div className="results-header">
              <h2>Recommendations</h2>
              <div className="results-controls">
                <label className="sort-label">
                  <span>Sort by</span>
                  <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="sort-select">
                    <option value="default">Default order</option>
                    <option value="rating_desc">Rating: high → low</option>
                    <option value="rating_asc">Rating: low → high</option>
                    <option value="price_asc">Price: low → high</option>
                    <option value="price_desc">Price: high → low</option>
                  </select>
                </label>
                <label className="page-size-label">
                  <span>Show per page</span>
                  <select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setCurrentPage(1); }} className="page-size-select">
                    {PAGE_SIZE_OPTIONS.map((n) => (
                      <option key={n} value={n}>{n}</option>
                    ))}
                  </select>
                </label>
              </div>
            </div>
            <div className="results-grid">
              {paginatedRecs.map((rec, i) => (
                <article key={start + i} className="rec-card">
                  <div className="rec-card-image">
                    <img
                      src={CARD_IMAGES[(start + i) % CARD_IMAGES.length]}
                      alt=""
                      onError={(e) => { e.target.style.display = 'none' }}
                    />
                    <span className="rec-number">{start + i + 1}</span>
                  </div>
                  <div className="rec-card-body">
                    <h3>{rec.name}</h3>
                    <div className="rec-meta">
                      <span className="chip">{rec.cuisine}</span>
                      <span className="chip">{rec.location}</span>
                      <span className="rating">★ {Number(rec.rating)?.toFixed(1) || rec.rating}</span>
                      <span className="price-tag">{rec.price_range}</span>
                    </div>
                    {rec.reason && <p className="rec-reason">{rec.reason}</p>}
                  </div>
                </article>
              ))}
            </div>
            <div className="pagination">
              <span className="pagination-info">
                Showing {sortedRecommendations.length ? start + 1 : 0}–{Math.min(start + pageSize, sortedRecommendations.length)} of {sortedRecommendations.length}
              </span>
              <div className="pagination-buttons">
                <button type="button" className="pagination-btn" onClick={() => setCurrentPage((p) => Math.max(1, p - 1))} disabled={currentPage <= 1}>
                  Previous
                </button>
                <span className="pagination-page">Page {currentPage} of {totalPages}</span>
                <button type="button" className="pagination-btn" onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))} disabled={currentPage >= totalPages}>
                  Next
                </button>
              </div>
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
