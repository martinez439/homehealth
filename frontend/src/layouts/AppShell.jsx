import { Link, useLocation } from 'react-router-dom';

const links = [
  ['/admin', 'Dashboard'],
  ['/admin/clients', 'Clients'],
  ['/admin/caregivers', 'Caregivers'],
  ['/admin/schedule', 'Schedule'],
  ['/caregiver', 'Visits'],
  ['/intake', 'Intake'],
  ['/family/1', 'Family Portal'],
  ['#', 'Settings'],
];

export default function AppShell({ children }) {
  const location = useLocation();
  const today = new Date().toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1 className="brand-title">CLHS HomeCare</h1>
        <p className="brand-sub">Concierge care operations</p>
        <nav className="nav-group">
          {links.map(([to, label]) => (
            <Link key={label} className={`nav-link ${location.pathname === to ? 'active' : ''}`} to={to === '#' ? location.pathname : to}>{label}</Link>
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
          <div className="top-meta">Notifications • Profile</div>
        </header>
        {children}
      </main>
    </div>
  );
}
