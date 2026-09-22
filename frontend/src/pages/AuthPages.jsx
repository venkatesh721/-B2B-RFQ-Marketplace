import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import apiClient from '../api/client'
import { useAuth } from '../context/AuthContext'
import { apiError, ErrorMessage } from '../components/Ui'

export function LoginPage() {
  const { user, saveSession } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState(''); const [submitting, setSubmitting] = useState(false)
  if (user) return <Navigate to={user.role === 'BUYER' ? '/buyer/dashboard' : '/supplier/dashboard'} replace />
  async function submit(event) {
    event.preventDefault(); setError(''); setSubmitting(true)
    try { const { data } = await apiClient.post('/auth/login/', form); saveSession(data); navigate(data.user.role === 'BUYER' ? '/buyer/dashboard' : '/supplier/dashboard') }
    catch (err) {
      const messages = err.response?.data?.non_field_errors
      setError(Array.isArray(messages) ? 'We couldn’t sign you in with that email and password. Please try again.' : apiError(err))
    } finally { setSubmitting(false) }
  }
  return <main className="login-page"><div className="login-background" aria-hidden="true"><div className="login-orb login-orb-one" /><div className="login-orb login-orb-two" /><div className="login-halo login-halo-one" /><div className="login-halo login-halo-two" /><div className="login-dots" /></div>
    <section className="login-card" aria-labelledby="login-title"><div className="login-brand"><span className="login-brand-icon" aria-hidden="true">R</span><div><Link to="/" className="login-brand-name">RFQ Market</Link><p>Business sourcing, simplified</p></div></div><div className="login-intro"><h1 id="login-title">Welcome back</h1><p>Sign in to manage your RFQs and quotations.</p></div>
      <form onSubmit={submit}><div className={error ? 'login-error' : ''}><ErrorMessage error={error} /></div><Field label="Email" type="email" autoComplete="email" placeholder="name@company.com" value={form.email} onChange={email => setForm({ ...form, email })} required /><Field label="Password" type="password" autoComplete="current-password" placeholder="Enter your password" value={form.password} onChange={password => setForm({ ...form, password })} required />
        <button className="login-submit" disabled={submitting}>{submitting && <span className="button-spinner" aria-hidden="true" />}{submitting ? 'Signing in...' : 'Sign in'}</button><p className="form-footnote login-register">New here? <Link to="/register">Create an account</Link></p>
      </form>
    </section>
  </main>
}

export function RegisterPage() {
  const { user } = useAuth(); const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'BUYER' })
  const [error, setError] = useState(''); const [success, setSuccess] = useState(''); const [submitting, setSubmitting] = useState(false)
  if (user) return <Navigate to={user.role === 'BUYER' ? '/buyer/dashboard' : '/supplier/dashboard'} replace />
  async function submit(event) {
    event.preventDefault(); setError(''); setSuccess(''); setSubmitting(true)
    try { await apiClient.post('/auth/register/', form); setSuccess('Account created. You can now sign in.'); setTimeout(() => navigate('/login'), 700) }
    catch (err) { setError(apiError(err)) } finally { setSubmitting(false) }
  }
  return <AuthCard title="Create your account" subtitle="Choose the role that matches your marketplace activity."><form onSubmit={submit}>
    <ErrorMessage error={error} />{success && <div className="notice success">{success}</div>}
    <Field label="Name" value={form.name} onChange={name => setForm({ ...form, name })} required />
    <Field label="Email" type="email" value={form.email} onChange={email => setForm({ ...form, email })} required />
    <Field label="Password" type="password" value={form.password} onChange={password => setForm({ ...form, password })} minLength="8" required />
    <label>Account type<select value={form.role} onChange={e => setForm({ ...form, role: e.target.value })}><option value="BUYER">Buyer</option><option value="SUPPLIER">Supplier</option></select></label>
    <button disabled={submitting}>{submitting ? 'Creating account...' : 'Create account'}</button>
    <p className="form-footnote">Already registered? <Link to="/login">Sign in</Link></p>
  </form></AuthCard>
}

function AuthCard({ title, subtitle, children }) { return <main className="auth-page"><section className="auth-card"><Link className="brand" to="/">RFQ Market</Link><h1>{title}</h1><p>{subtitle}</p>{children}</section></main> }
function Field({ label, onChange, ...props }) { return <label>{label}<input {...props} onChange={e => onChange(e.target.value)} /></label> }
