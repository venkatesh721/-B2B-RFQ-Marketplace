import { Route, Routes } from 'react-router-dom'
import NotFoundPage from './pages/NotFoundPage'
import AppLayout from './components/AppLayout'
import { HomeRedirect, ProtectedRoute } from './components/RouteGuards'
import { LoginPage, RegisterPage } from './pages/AuthPages'
import DashboardPage from './pages/DashboardPage'
import { RfqDetailsPage, RfqFormPage, RfqListPage } from './pages/RfqPages'
import { MyQuotationsPage, ReceivedQuotationsPage, SubmitQuotationPage } from './pages/QuotationPages'

export default function App() {
  return <Routes>
    <Route path="/" element={<HomeRedirect />} />
    <Route path="/login" element={<LoginPage />} /><Route path="/register" element={<RegisterPage />} />
    <Route element={<ProtectedRoute role="BUYER" />}><Route element={<AppLayout><DashboardPage /></AppLayout>} path="/buyer/dashboard" /><Route element={<AppLayout><RfqListPage /></AppLayout>} path="/buyer/rfqs" /><Route element={<AppLayout><RfqFormPage /></AppLayout>} path="/buyer/rfqs/new" /><Route element={<AppLayout><RfqDetailsPage /></AppLayout>} path="/buyer/rfqs/:id" /><Route element={<AppLayout><RfqFormPage edit /></AppLayout>} path="/buyer/rfqs/:id/edit" /><Route element={<AppLayout><ReceivedQuotationsPage /></AppLayout>} path="/buyer/rfqs/:id/quotations" /></Route>
    <Route element={<ProtectedRoute role="SUPPLIER" />}><Route element={<AppLayout><DashboardPage /></AppLayout>} path="/supplier/dashboard" /><Route element={<AppLayout><RfqListPage /></AppLayout>} path="/supplier/rfqs" /><Route element={<AppLayout><RfqDetailsPage /></AppLayout>} path="/supplier/rfqs/:id" /><Route element={<AppLayout><SubmitQuotationPage /></AppLayout>} path="/supplier/rfqs/:id/quote" /><Route element={<AppLayout><MyQuotationsPage /></AppLayout>} path="/supplier/quotations" /></Route>
    <Route path="*" element={<NotFoundPage />} />
  </Routes>
}
