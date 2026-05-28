import { Link } from 'react-router-dom';

const links = [
  ['/intake', 'Intake'],
  ['/admin', 'Admin'],
  ['/admin/clients', 'Clients'],
  ['/admin/caregivers', 'Caregivers'],
  ['/admin/schedule', 'Schedule'],
  ['/caregiver', 'Caregiver'],
  ['/family/1', 'Family'],
];

export default function AppShell({ children }) {
  return (
    <div className="app-shell">
      <header className="topbar">
        <h1>Home Health Care Platform</h1>
        <nav>
          {links.map(([to, label]) => (
            <Link key={to} to={to}>{label}</Link>
          ))}
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
}
