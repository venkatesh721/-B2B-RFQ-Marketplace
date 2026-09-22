import { useEffect, useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function AppLayout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const isBuyer = user?.role === 'BUYER'
  const [menuOpen, setMenuOpen] = useState(false)
  const [theme, setTheme] = useState(() => {
    if (typeof window === 'undefined') return 'light'
    const savedTheme = window.localStorage.getItem('rfq-market-theme')
    return savedTheme || 'light'
  })
  const closeMenu = () => setMenuOpen(false)

  useEffect(() => {
    window.localStorage.setItem('rfq-market-theme', theme)
  }, [theme])

  function signOut() { logout(); navigate('/login') }

  const navItems = isBuyer ? [
    { to: '/buyer/dashboard', label: 'Dashboard' },
    { to: '/buyer/rfqs', label: 'My RFQs' },
    { to: '/buyer/rfqs/new', label: 'Create RFQ' },
  ] : [
    { to: '/supplier/dashboard', label: 'Dashboard' },
    { to: '/supplier/rfqs', label: 'Browse RFQs' },
    { to: '/supplier/quotations', label: 'My Quotations' },
  ]

  return <div className={`app-shell dashboard-app-shell theme-${theme}`} data-theme={theme}>
    <div
      className={`mobile-backdrop ${menuOpen ? 'visible' : ''}`}
      onClick={closeMenu}
      aria-hidden={!menuOpen}
    />

    <aside className={`app-sidebar ${menuOpen ? 'mobile-open' : ''}`}>
      <button type="button" className="drawer-close" aria-label="Close menu" onClick={closeMenu}>×</button>

      <Link onClick={closeMenu} to={isBuyer ? '/buyer/dashboard' : '/supplier/dashboard'} className="brand sidebar-brand">
        <span className="brand-mark">R</span>
        <span>RFQ Market</span>
      </Link>

      <div className="sidebar-section">
        <p className="sidebar-label">Workspace</p>
        <nav className="sidebar-nav" aria-label="Main navigation">
          {navItems.map(({ to, label }) => (
            <NavLink key={to} onClick={closeMenu} to={to} className="sidebar-link">
              <span className="sidebar-link-icon">•</span>
              {label}
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="sidebar-card">
        <p className="sidebar-label">Signed in</p>
        <div className="sidebar-user">
          <div className="user-avatar">{user?.name?.charAt(0)?.toUpperCase() || 'U'}</div>
          <div>
            <strong>{user?.name || 'User'}</strong>
            <span>{isBuyer ? 'Buyer account' : 'Supplier account'}</span>
          </div>
        </div>
        <button type="button" className="button sidebar-signout" onClick={signOut}>Sign out</button>
      </div>
    </aside>

    <div className="app-main">
      <header className="site-header">
        <div className="header-title-block">
          <p className="eyebrow">{isBuyer ? 'Buyer workspace' : 'Supplier workspace'}</p>
          <h1>{isBuyer ? 'Buyer dashboard' : 'Supplier dashboard'}</h1>
        </div>

        <div className="header-actions">
          <button
            className="mobile-menu-button"
            type="button"
            aria-label="Open navigation"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen(!menuOpen)}
          >
            ☰
          </button>
          <button
            type="button"
            className="theme-toggle"
            aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
          >
            {theme === 'light' ? '☾ Dark' : '☀ Light'}
          </button>
          <span className={isBuyer ? 'role-chip buyer-role' : 'role-chip supplier-role'}>{isBuyer ? 'BUYER' : 'SUPPLIER'}</span>
        </div>
      </header>

      <nav id="main-navigation" className={`primary-nav ${menuOpen ? 'open' : ''}`}>
        {navItems.map(({ to, label }) => (
          <NavLink key={to} onClick={closeMenu} to={to}>{label}</NavLink>
        ))}
        <button type="button" className="link-button" onClick={signOut}>Sign out</button>
      </nav>

      <div className="content-pane">{children}</div>
    </div>
  </div>
}
