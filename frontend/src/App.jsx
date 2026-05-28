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

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Navigate to="/intake" replace />} />
        <Route path="/intake" element={<IntakePage />} />
        <Route path="/admin" element={<AdminDashboardPage />} />
        <Route path="/admin/clients" element={<AdminClientsPage />} />
        <Route path="/admin/caregivers" element={<AdminCaregiversPage />} />
        <Route path="/admin/schedule" element={<AdminSchedulePage />} />
        <Route path="/caregiver" element={<CaregiverPage />} />
        <Route path="/caregiver/visits/:id" element={<VisitDetailsPage />} />
        <Route path="/family/:clientId" element={<FamilyViewPage />} />
      </Routes>
    </AppShell>
  );
}
