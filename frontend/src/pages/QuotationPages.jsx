import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import apiClient from '../api/client'
import { apiError, Empty, ErrorMessage, Loading, SuccessMessage } from '../components/Ui'

const displayDate = value => new Date(value).toLocaleString()

export function SubmitQuotationPage() {
  const { id } = useParams(); const navigate = useNavigate(); const [rfq, setRfq] = useState(null)
  const [form, setForm] = useState({ quoted_price: '', estimated_delivery_time: '', message: '' }); const [error, setError] = useState(''); const [success, setSuccess] = useState(''); const [loading, setLoading] = useState(true); const [submitting, setSubmitting] = useState(false)
  useEffect(() => { apiClient.get(`/rfqs/${id}/`).then(({ data }) => setRfq(data)).catch(err => setError(apiError(err))).finally(() => setLoading(false)) }, [id])
  async function submit(event) { event.preventDefault(); setError(''); setSuccess(''); setSubmitting(true)
    try { await apiClient.post('/quotations/', { rfq: Number(id), ...form }); setSuccess('Quotation submitted successfully.'); setTimeout(() => navigate('/supplier/quotations'), 650) } catch (err) { setError(apiError(err)) } finally { setSubmitting(false) }
  }
  if (loading) return <Loading />
  return <main className="form-page"><h1>Submit quotation</h1>{rfq && <p>For: <strong>{rfq.product_or_service_name}</strong></p>}<form className="form-card" onSubmit={submit}><ErrorMessage error={error} /><SuccessMessage message={success} />
    <label>Quoted price<input type="number" min="0.01" step="0.01" value={form.quoted_price} onChange={e => setForm({ ...form, quoted_price: e.target.value })} required /></label>
    <label>Estimated delivery time<input placeholder="e.g. 5 business days" value={form.estimated_delivery_time} onChange={e => setForm({ ...form, estimated_delivery_time: e.target.value })} required /></label>
    <label>Message (optional)<textarea value={form.message} onChange={e => setForm({ ...form, message: e.target.value })} /></label>
    <button disabled={submitting}>{submitting ? 'Submitting…' : 'Submit quotation'}</button>
  </form></main>
}

export function MyQuotationsPage() { return <QuotationList url="/quotations/my/" title="My quotations" subtitle="Track the offers you have submitted." supplier /> }

export function ReceivedQuotationsPage() {
  const { id } = useParams()
  return <QuotationList url={`/rfqs/${id}/quotations/`} title="Received quotations" subtitle="Compare offers submitted for this RFQ." />
}

function QuotationList({ url, title, subtitle, supplier = false }) {
  const [quotes, setQuotes] = useState([]); const [loading, setLoading] = useState(true); const [error, setError] = useState('')
  useEffect(() => { let live = true; apiClient.get(url).then(({ data }) => live && setQuotes(data.results ?? data)).catch(err => live && setError(apiError(err))).finally(() => live && setLoading(false)); return () => { live = false } }, [url])
  return <main><div className="page-heading"><div><h1>{title}</h1><p>{subtitle}</p></div></div><ErrorMessage error={error} />{loading ? <Loading /> : quotes.length === 0 ? <Empty>{supplier ? 'You have not submitted any quotations yet.' : 'No quotations have been received for this RFQ yet.'}</Empty> : <div className="card-grid">{quotes.map(quote => <article className="card" key={quote.id}><div className="card-title"><h2>{supplier ? `RFQ #${quote.rfq}` : `Supplier #${quote.supplier}`}</h2><strong>₹{Number(quote.quoted_price).toLocaleString()}</strong></div><dl><dt>Delivery</dt><dd>{quote.estimated_delivery_time}</dd><dt>Submitted</dt><dd>{displayDate(quote.created_at)}</dd></dl>{quote.message && <p className="quote-message">“{quote.message}”</p>}{supplier && <Link className="text-link" to={`/supplier/rfqs/${quote.rfq}`}>View RFQ →</Link>}</article>)}</div>}</main>
}
