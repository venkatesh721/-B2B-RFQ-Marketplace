import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import apiClient from '../api/client'
import { apiError, Empty, ErrorMessage, Loading } from '../components/Ui'
import { useAuth } from '../context/AuthContext'

const formatCurrency = value => `₹${Number(value || 0).toLocaleString('en-IN')}`

function normalizeList(payload) {
  if (Array.isArray(payload)) return payload
  if (payload && Array.isArray(payload.results)) return payload.results
  return []
}

export default function DashboardPage() {
  const { user } = useAuth()
  const buyer = user?.role === 'BUYER'
  const [state, setState] = useState({ loading: true, error: '', rfqs: [], quotations: [] })

  useEffect(() => {
    let live = true

    async function loadBuyerMetrics() {
      const { data: rfqData } = await apiClient.get('/rfqs/')
      const rfqs = normalizeList(rfqData)

      const quoteRequests = rfqs.map(rfq => apiClient.get(`/rfqs/${rfq.id}/quotations/`))
      const quoteResponses = await Promise.all(quoteRequests)
      const quotations = quoteResponses.flatMap(({ data }) => normalizeList(data))

      if (live) {
        setState({
          loading: false,
          error: '',
          rfqs,
          quotations,
        })
      }
    }

    async function loadSupplierMetrics() {
      const [rfqResponse, quoteResponse] = await Promise.all([
        apiClient.get('/rfqs/'),
        apiClient.get('/quotations/my/'),
      ])

      if (live) {
        setState({
          loading: false,
          error: '',
          rfqs: normalizeList(rfqResponse.data),
          quotations: normalizeList(quoteResponse.data),
        })
      }
    }

    async function load() {
      try {
        setState({ loading: true, error: '', rfqs: [], quotations: [] })
        if (buyer) {
          await loadBuyerMetrics()
        } else {
          await loadSupplierMetrics()
        }
      } catch (err) {
        if (live) {
          setState({ loading: false, error: apiError(err), rfqs: [], quotations: [] })
        }
      }
    }

    load()
    return () => { live = false }
  }, [buyer])

  if (state.loading) {
    return <main className="dashboard-overview"><Loading /></main>
  }

  if (state.error) {
    return <main className="dashboard-overview"><ErrorMessage error={state.error} /></main>
  }

  if (buyer) {
    const totalRfqs = state.rfqs.length
    const activeRfqs = state.rfqs.filter(rfq => rfq.status === 'OPEN').length
    const quotationsReceived = state.quotations.length
    const recentRfqs = [...state.rfqs].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 4)
    const recentQuotations = [...state.quotations].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 4)

    return <main className="dashboard-overview">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">Overview</p>
          <h1>Hello, {user.name}</h1>
          <p>Monitor RFQs, compare offers, and keep your procurement pipeline on track.</p>
        </div>
        <Link className="button" to="/buyer/rfqs/new">Create RFQ</Link>
      </header>

      <section className="stat-grid">
        <StatCard icon="◎" label="Total RFQs" value={totalRfqs} tone="navy" />
        <StatCard icon="◔" label="Active RFQs" value={activeRfqs} tone="blue" />
        <StatCard icon="▣" label="Quotations Received" value={quotationsReceived} tone="slate" />
      </section>

      <section className="dashboard-panels">
        <section className="panel-card">
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Pipeline</p>
              <h2>Recent RFQs</h2>
            </div>
            <Link className="text-link" to="/buyer/rfqs">View all</Link>
          </div>
          {recentRfqs.length ? <div className="list-stack">
            {recentRfqs.map(rfq => (
              <Link key={rfq.id} className="list-item" to={`/buyer/rfqs/${rfq.id}`}>
                <div>
                  <strong>{rfq.product_or_service_name}</strong>
                  <span>{rfq.delivery_location}</span>
                </div>
                <div className="list-meta">
                  <span className={`badge ${rfq.status === 'OPEN' ? 'badge-open' : 'badge-closed'}`}>{rfq.status}</span>
                  <small>{rfq.quantity}</small>
                </div>
              </Link>
            ))}
          </div> : <Empty title="No RFQs yet">Create your first procurement request to begin receiving supplier quotes.</Empty>}
        </section>

        <section className="panel-card">
          <div className="panel-header">
            <div>
              <p className="panel-kicker">Suppliers</p>
              <h2>Recent Quotations</h2>
            </div>
            <Link className="text-link" to="/buyer/rfqs">Compare offers</Link>
          </div>
          {recentQuotations.length ? <div className="list-stack">
            {recentQuotations.map(quote => (
              <div key={`${quote.id}-${quote.rfq}`} className="list-item quote-item">
                <div>
                  <strong>RFQ #{quote.rfq}</strong>
                  <span>Supplier #{quote.supplier}</span>
                </div>
                <div className="list-meta">
                  <strong>{formatCurrency(quote.quoted_price)}</strong>
                  <small>{quote.estimated_delivery_time}</small>
                </div>
              </div>
            ))}
          </div> : <Empty title="No quotes yet">Your RFQ results will appear here as suppliers respond.</Empty>}
        </section>
      </section>
    </main>
  }

  const availableRfqs = state.rfqs.length
  const submittedQuotations = state.quotations.length
  const pendingActive = Math.max(state.quotations.length, 0)
  const recentRfqs = [...state.rfqs].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 4)
  const recentQuotations = [...state.quotations].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 4)

  return <main className="dashboard-overview">
    <header className="dashboard-header">
      <div>
        <p className="eyebrow">Overview</p>
        <h1>Hello, {user.name}</h1>
        <p>Review open opportunities, track submitted offers, and respond to buyer requests.</p>
      </div>
      <Link className="button" to="/supplier/rfqs">Browse RFQs</Link>
    </header>

    <section className="stat-grid">
      <StatCard icon="◌" label="Available RFQs" value={availableRfqs} tone="navy" />
      <StatCard icon="▤" label="Submitted Quotations" value={submittedQuotations} tone="blue" />
      <StatCard icon="◍" label="Pending / Active Quotations" value={pendingActive} tone="slate" />
    </section>

    <section className="dashboard-panels">
      <section className="panel-card">
        <div className="panel-header">
          <div>
            <p className="panel-kicker">Marketplace</p>
            <h2>Recent RFQs</h2>
          </div>
          <Link className="text-link" to="/supplier/rfqs">Open bids</Link>
        </div>
        {recentRfqs.length ? <div className="list-stack">
          {recentRfqs.map(rfq => (
            <Link key={rfq.id} className="list-item" to={`/supplier/rfqs/${rfq.id}`}>
              <div>
                <strong>{rfq.product_or_service_name}</strong>
                <span>{rfq.delivery_location}</span>
              </div>
              <div className="list-meta">
                <span className={`badge ${rfq.status === 'OPEN' ? 'badge-open' : 'badge-closed'}`}>{rfq.status}</span>
                <small>{rfq.quantity}</small>
              </div>
            </Link>
          ))}
        </div> : <Empty title="No RFQs currently open">New buyer requests will appear here when they are published.</Empty>}
      </section>

      <section className="panel-card">
        <div className="panel-header">
          <div>
            <p className="panel-kicker">Offers</p>
            <h2>Recent Quotations</h2>
          </div>
          <Link className="text-link" to="/supplier/quotations">My quotes</Link>
        </div>
        {recentQuotations.length ? <div className="list-stack">
          {recentQuotations.map(quote => (
            <div key={`${quote.id}-${quote.rfq}`} className="list-item quote-item">
              <div>
                <strong>RFQ #{quote.rfq}</strong>
                <span>{quote.estimated_delivery_time}</span>
              </div>
              <div className="list-meta">
                <strong>{formatCurrency(quote.quoted_price)}</strong>
                <small>{new Date(quote.created_at).toLocaleDateString('en-IN')}</small>
              </div>
            </div>
          ))}
        </div> : <Empty title="No quotations submitted yet">Submit your first quotation to start tracking your pipeline.</Empty>}
      </section>
    </section>
  </main>
}

function StatCard({ icon, label, value, tone }) {
  return <article className={`stat-card stat-card-${tone}`}>
    <div className="stat-icon">{icon}</div>
    <div>
      <p>{label}</p>
      <strong>{value}</strong>
    </div>
  </article>
}
