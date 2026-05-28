import { Link, useLocation, useNavigate } from 'react-router-dom';
import { clearAuth, getStoredUser } from '../api/auth';

const adminLinks = [
  ['/admin', 'Dashboard'],
  ['/admin/clients', 'Clients'],
  ['/admin/caregivers', 'Caregivers'],
  ['/admin/schedule', 'Schedule'],
  ['/admin/audit-logs', 'Audit Logs'],
  ['/intake', 'Intake'],
  ['/family/1', 'Family Preview'],
];

export default function AppShell({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const user = getStoredUser();
  const today = new Date().toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  const links = user?.role === 'admin' ? adminLinks : user?.role === 'caregiver' ? [['/caregiver', 'Visits'], ['/intake', 'Intake']] : user?.role === 'family' ? [[`/family/${user.client_id || 1}`, 'Family Portal'], ['/intake', 'Intake']] : [['/intake', 'Intake'], ['/login', 'Login']];

  function logout() {
    clearAuth();
    navigate('/login');
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1 className="brand-title">CLHS HomeCare</h1>
        <p className="brand-sub">Concierge care operations</p>
        <nav className="nav-group">
          {links.map(([to, label]) => (
            <Link key={label} className={`nav-link ${location.pathname === to ? 'active' : ''}`} to={to}>{label}</Link>
          ))}
        </nav>
      </aside>
      <main className="main-area">
        <header className="topbar">
          <div>
            <strong>Willow Creek Home Health</strong>
            <div className="top-meta">{today}</div>
          </div>
          <input className="search" placeholder="Search clients, caregivers, visits" />
          <div className="top-meta">{user ? `${user.first_name} ${user.last_name} • ${user.role}` : 'Guest'} {user && <button className="link-button" onClick={logout}>Logout</button>}</div>
        </header>
        {children}
      </main>
    </div>
  );
}
