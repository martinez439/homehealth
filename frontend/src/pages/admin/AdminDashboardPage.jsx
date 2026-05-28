import { Card, PageHeader, StatCard, StatusPill } from '../../components/UI';

const stats = [
  { label: 'Active Clients', value: 128, status: { className: 'completed', text: 'Stable census' } },
  { label: 'Visits Today', value: 42, status: { className: 'scheduled', text: '8 pending' } },
  { label: 'Caregivers On Shift', value: 26, status: { className: 'progress', text: '3 check-ins due' } },
  { label: 'Intake Requests', value: 9, status: { className: 'missed', text: '2 urgent follow-ups' } },
];

export default function AdminDashboardPage() {
  return (
    <>
      <PageHeader title="Operations Dashboard" subtitle="A calm, high-touch overview of today’s care delivery." />
      <section className="grid stats">{stats.map((s) => <StatCard key={s.label} {...s} />)}</section>
      <section className="grid" style={{ gridTemplateColumns: '1.2fr .8fr', marginTop: '1rem' }}>
        <Card title="Recent Notes">
          <p><strong>Maria L.</strong> slept comfortably, vitals within baseline.</p>
          <p><strong>John R.</strong> mobility goals met; family updated at 2:15 PM.</p>
        </Card>
        <Card title="Visit Status Mix">
          <div className="actions">
            <StatusPill status={{ className: 'scheduled', text: 'Scheduled 24' }} />
            <StatusPill status={{ className: 'progress', text: 'In Progress 8' }} />
            <StatusPill status={{ className: 'completed', text: 'Completed 19' }} />
            <StatusPill status={{ className: 'missed', text: 'Missed 1' }} />
          </div>
        </Card>
      </section>
    </>
  );
}
