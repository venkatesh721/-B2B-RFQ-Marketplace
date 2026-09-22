export function ErrorMessage({ error }) { return error ? <div className="notice error" role="alert">{error}</div> : null }
export function SuccessMessage({ message }) { return message ? <div className="notice success" role="status">{message}</div> : null }
export function Loading() { return <div className="page-state loading-stack" role="status" aria-label="Loading content"><span className="skeleton" /><span className="skeleton short" /><span className="skeleton" /></div> }
export function Empty({ children, title = 'Nothing here yet', action }) { return <section className="empty-state"><h2>{title}</h2><p>{children}</p>{action}</section> }

export function apiError(error) {
  const data = error.response?.data
  if (!data) return 'Unable to reach the server. Please try again.'
  if (typeof data === 'string') return data
  if (data.detail) return data.detail
  return Object.entries(data).map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(' ') : messages}`).join(' ')
}
