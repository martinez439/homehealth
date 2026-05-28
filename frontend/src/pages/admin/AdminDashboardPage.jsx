import { useEffect, useState } from 'react';
import { apiGet } from '../../api/client';
import { Card, PageHeader, StatCard, StatusPill } from '../../components/UI';

export default function AdminDashboardPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    apiGet('/api/dashboard/summary').then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <Card>Failed to load dashboard: {error}</Card>;
  if (!data) return <Card>Loading dashboard…</Card>;

  const stats = [
    { label: 'Active Clients', value: data.active_clients_count },
    { label: 'Visits Today', value: data.visits_today_count },
    { label: 'Caregivers On Shift', value: data.caregivers_on_shift_count },
    { label: 'Intake Requests', value: data.intake_requests_count },
  ];

  return (
    <>
      <PageHeader title="Operations Dashboard" subtitle="A calm, high-touch overview of today’s care delivery." />
      <section className="grid stats">{stats.map((s) => <StatCard key={s.label} {...s} />)}</section>
      <section className="grid" style={{ gridTemplateColumns: '1.2fr .8fr', marginTop: '1rem' }}>
        <Card title="Recent Activity">{data.recent_activity.map((a) => <p key={a.id}>{a.message}</p>)}</Card>
        <Card title="Visit Status Mix">
          <div className="actions">
            <StatusPill status={{ className: 'scheduled', text: `Scheduled ${data.pending_visits_count}` }} />
            <StatusPill status={{ className: 'completed', text: `Completed ${data.completed_visits_count}` }} />
            <StatusPill status={{ className: 'missed', text: `Missed ${data.missed_visits_count}` }} />
          </div>
        </Card>
      </section>
    </>
  );
}
