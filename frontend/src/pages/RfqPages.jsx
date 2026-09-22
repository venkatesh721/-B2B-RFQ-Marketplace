import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import apiClient from '../api/client'
import { useAuth } from '../context/AuthContext'
import { apiError, Empty, ErrorMessage, Loading, SuccessMessage } from '../components/Ui'

const blank = { product_or_service_name: '', requirement_description: '', quantity: '', delivery_location: '', deadline: '' }
const displayDate = value => new Date(value).toLocaleString()

export function RfqListPage() {
  const { user } = useAuth(); const buyer = user.role === 'BUYER'
  const [items, setItems] = useState([]); const [loading, setLoading] = useState(true); const [error, setError] = useState('')
  const [filters, setFilters] = useState({ search: '', product_or_service_name: '', delivery_location: '' })
  async function load() { setLoading(true); setError(''); try { const { data } = await apiClient.get('/rfqs/', { params: filters }); setItems(data.results ?? data) } catch (err) { setError(apiError(err)) } finally { setLoading(false) } }
  useEffect(() => { load() }, [])
  function submit(event) { event.preventDefault(); load() }
  return <main><div className="page-heading"><div><h1>{buyer ? 'My RFQs' : 'Browse RFQs'}</h1><p>{buyer ? 'Create, update, and review your requests.' : 'Open requests available for quotation.'}</p></div>{buyer && <Link className="button" to="/buyer/rfqs/new">Create RFQ</Link>}</div>
    {!buyer && <form className="filter-bar" onSubmit={submit}><input placeholder="Search product or location" value={filters.search} onChange={e => setFilters({ ...filters, search: e.target.value })} /><input placeholder="Product or service" value={filters.product_or_service_name} onChange={e => setFilters({ ...filters, product_or_service_name: e.target.value })} /><input placeholder="Delivery location" value={filters.delivery_location} onChange={e => setFilters({ ...filters, delivery_location: e.target.value })} /><button>Search</button></form>}
    <ErrorMessage error={error} />{loading ? <Loading /> : items.length === 0 ? <Empty>{buyer ? 'You have not created any RFQs yet.' : 'No open RFQs match your search.'}</Empty> : <div className="card-grid">{items.map(rfq => <article className="card" key={rfq.id}><div className="card-title"><h2>{rfq.product_or_service_name}</h2><span className="badge">{rfq.status}</span></div><p>{rfq.requirement_description}</p><dl><dt>Quantity</dt><dd>{rfq.quantity}</dd><dt>Location</dt><dd>{rfq.delivery_location}</dd><dt>Deadline</dt><dd>{displayDate(rfq.deadline)}</dd></dl><Link className="text-link" to={`${buyer ? '/buyer' : '/supplier'}/rfqs/${rfq.id}`}>View details →</Link></article>)}</div>}
  </main>
}

export function RfqFormPage({ edit = false }) {
  const { id } = useParams(); const navigate = useNavigate(); const [form, setForm] = useState(blank)
  const [loading, setLoading] = useState(edit); const [error, setError] = useState(''); const [success, setSuccess] = useState(''); const [submitting, setSubmitting] = useState(false)
  useEffect(() => { if (!edit) return; apiClient.get(`/rfqs/${id}/`).then(({ data }) => setForm({ ...data, deadline: data.deadline.slice(0, 16) })).catch(err => setError(apiError(err))).finally(() => setLoading(false)) }, [edit, id])
  function change(field, value) { setForm({ ...form, [field]: value }) }
  async function submit(event) { event.preventDefault(); setError(''); setSuccess(''); setSubmitting(true)
    const payload = { ...form, quantity: Number(form.quantity), deadline: new Date(form.deadline).toISOString() }
    try { const { data } = edit ? await apiClient.patch(`/rfqs/${id}/`, payload) : await apiClient.post('/rfqs/', payload); setSuccess(`RFQ ${edit ? 'updated' : 'created'} successfully.`); setTimeout(() => navigate(`/buyer/rfqs/${data.id}`), 650) } catch (err) { setError(apiError(err)) } finally { setSubmitting(false) }
  }
  if (loading) return <Loading />
  return <main className="form-page rfq-form-page"><div className="rfq-form-heading"><p className="eyebrow">Procurement request</p><h1>{edit ? 'Edit RFQ' : 'Create RFQ'}</h1><p>Provide enough detail for suppliers to prepare a meaningful quotation.</p></div><form className="form-card rfq-form-card" onSubmit={submit}><ErrorMessage error={error} /><SuccessMessage message={success} />
    <label>Product or service name<input value={form.product_or_service_name} onChange={e => change('product_or_service_name', e.target.value)} required /></label>
    <label>Requirement description<textarea value={form.requirement_description} onChange={e => change('requirement_description', e.target.value)} required /></label>
    <div className="two-col"><label>Quantity<input type="number" min="1" value={form.quantity} onChange={e => change('quantity', e.target.value)} required /></label><label>Delivery location<input value={form.delivery_location} onChange={e => change('delivery_location', e.target.value)} required /></label></div>
    <label>Deadline<input type="datetime-local" value={form.deadline} onChange={e => change('deadline', e.target.value)} required /></label>
    <button disabled={submitting}>{submitting ? 'Saving…' : edit ? 'Save changes' : 'Create RFQ'}</button>
  </form></main>
}

export function RfqDetailsPage() {
  const { id } = useParams(); const { user } = useAuth(); const buyer = user.role === 'BUYER'; const navigate = useNavigate()
  const [rfq, setRfq] = useState(null); const [error, setError] = useState(''); const [loading, setLoading] = useState(true); const [success, setSuccess] = useState(''); const [deleting, setDeleting] = useState(false)
  useEffect(() => { apiClient.get(`/rfqs/${id}/`).then(({ data }) => setRfq(data)).catch(err => setError(apiError(err))).finally(() => setLoading(false)) }, [id])
  async function remove() { if (!window.confirm('Delete this RFQ? This cannot be undone.')) return; setDeleting(true); setError(''); try { await apiClient.delete(`/rfqs/${id}/`); navigate('/buyer/rfqs') } catch (err) { setError(apiError(err)); setDeleting(false) } }
  if (loading) return <Loading />; if (error) return <main><ErrorMessage error={error} /></main>; if (!rfq) return null
  return <main><div className="page-heading"><div><p className="eyebrow">RFQ #{rfq.id}</p><h1>{rfq.product_or_service_name}</h1><span className="badge">{rfq.status}</span></div><div className="actions">{buyer ? <><Link className="button secondary" to={`/buyer/rfqs/${id}/edit`}>Edit</Link><Link className="button" to={`/buyer/rfqs/${id}/quotations`}>Received quotations</Link><button className="danger" onClick={remove} disabled={deleting}>{deleting ? 'Deleting…' : 'Delete'}</button></> : <Link className="button" to={`/supplier/rfqs/${id}/quote`}>Submit quotation</Link>}</div></div><SuccessMessage message={success} /><section className="detail-card"><h2>Requirement</h2><p>{rfq.requirement_description}</p><dl><dt>Quantity</dt><dd>{rfq.quantity}</dd><dt>Delivery location</dt><dd>{rfq.delivery_location}</dd><dt>Deadline</dt><dd>{displayDate(rfq.deadline)}</dd>{buyer && <><dt>Created</dt><dd>{displayDate(rfq.created_at)}</dd></>}</dl></section></main>
}
