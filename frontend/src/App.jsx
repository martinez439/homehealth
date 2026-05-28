import { Navigate, Route, Routes } from 'react-router-dom';
import AppShell from './layouts/AppShell';
import IntakePage from './pages/intake/IntakePage';
import AdminDashboardPage from './pages/admin/AdminDashboardPage';
import AdminClientsPage from './pages/admin/AdminClientsPage';
import AdminCaregiversPage from './pages/admin/AdminCaregiversPage';
import AdminSchedulePage from './pages/admin/AdminSchedulePage';
import CaregiverPage from './pages/caregiver/CaregiverPage';
import VisitDetailsPage from './pages/caregiver/VisitDetailsPage';
import FamilyViewPage from './pages/family/FamilyViewPage';
import LoginPage from './pages/LoginPage';
import ForbiddenPage from './pages/ForbiddenPage';
import ProtectedRoute from './components/ProtectedRoute';
import AdminAuditLogsPage from './pages/admin/AdminAuditLogsPage';

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Navigate to="/intake" replace />} />
        <Route path="/intake" element={<IntakePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forbidden" element={<ForbiddenPage />} />
        <Route path="/admin" element={<ProtectedRoute roles={['admin']}><AdminDashboardPage /></ProtectedRoute>} />
        <Route path="/admin/clients" element={<ProtectedRoute roles={['admin']}><AdminClientsPage /></ProtectedRoute>} />
        <Route path="/admin/clients/:clientId/family" element={<ProtectedRoute roles={['admin']}><FamilyViewPage /></ProtectedRoute>} />
        <Route path="/admin/caregivers" element={<ProtectedRoute roles={['admin']}><AdminCaregiversPage /></ProtectedRoute>} />
        <Route path="/admin/schedule" element={<ProtectedRoute roles={['admin']}><AdminSchedulePage /></ProtectedRoute>} />
        <Route path="/admin/audit-logs" element={<ProtectedRoute roles={['admin']}><AdminAuditLogsPage /></ProtectedRoute>} />
        <Route path="/caregiver" element={<ProtectedRoute roles={['admin', 'caregiver']}><CaregiverPage /></ProtectedRoute>} />
        <Route path="/caregiver/visits/:id" element={<ProtectedRoute roles={['admin', 'caregiver']}><VisitDetailsPage /></ProtectedRoute>} />
        <Route path="/family/:clientId" element={<ProtectedRoute roles={['admin', 'family']}><FamilyViewPage /></ProtectedRoute>} />
      </Routes>
    </AppShell>
  );
}
