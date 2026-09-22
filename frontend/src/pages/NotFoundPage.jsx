import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return <main className="auth-page"><section className="auth-card"><Link className="brand" to="/"><span className="brand-mark">R</span>RFQ Market</Link><p className="eyebrow">404 error</p><h1>Page not found</h1><p>The page you requested does not exist or may no longer be available.</p><Link className="button" to="/">Return to your workspace</Link></section></main>
}
