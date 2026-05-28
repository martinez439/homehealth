import { useEffect, useState } from 'react';
import { apiGet } from '../../api/client';
import { Card, PageHeader, StatCard, StatusPill } from '../../components/UI';

export default function AdminDashboardPage() {
  const [data, setData] = useState(null);
  const [dailySummary, setDailySummary] = useState(null);
  const [reminders, setReminders] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([apiGet('/api/dashboard/summary'), apiGet('/api/schedule/daily-summary'), apiGet('/api/schedule/upcoming-reminders')])
      .then(([summary, daily, reminderData]) => { setData(summary); setDailySummary(daily); setReminders(reminderData); })
      .catch((e) => setError(e.message));
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
        {dailySummary && <Card title="Daily Schedule Summary">
          <p><strong>{dailySummary.total_visits}</strong> total visits today with <strong>{dailySummary.unresolved_conflicts.length}</strong> unresolved conflict(s).</p>
          {dailySummary.upcoming_visits.length === 0 ? <p className="empty-state">No upcoming visits remaining today.</p> : dailySummary.upcoming_visits.map((visit) => <p key={visit.id}>{visit.client_name} • {new Date(visit.scheduled_start).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}</p>)}
        </Card>}
        <Card title="Reminder Notifications">
          {reminders.length === 0 ? <p className="empty-state">No reminders awaiting action.</p> : reminders.slice(0, 5).map((reminder, index) => <div className="reminder-card" key={`${reminder.type}-${index}`}>{reminder.message}</div>)}
        </Card>
      </section>
    </>
  );
}
