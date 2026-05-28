import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiGet } from '../../api/client';
import { Card, PageHeader } from '../../components/UI';

const today = new Date().toISOString().slice(0, 10);

export default function CaregiverPage() {
  const [visits, setVisits] = useState([]);
  const [alerts, setAlerts] = useState({ count: 0, visits: [] });
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([apiGet('/api/caregiver/visits'), apiGet('/api/caregiver/alerts/missed-check-ins'), apiGet('/api/schedule/upcoming-reminders')])
      .then(([visitData, alertData, reminderData]) => {
        setVisits(visitData);
        setAlerts(alertData);
        setReminders(reminderData);
      })
      .catch((e) => setError(`Unable to load caregiver visits: ${e.message}`))
      .finally(() => setLoading(false));
  }, []);

  const todaysVisits = useMemo(() => visits.filter((v) => v.scheduled_start.slice(0, 10) === today), [visits]);

  return (<>
    <PageHeader title="Caregiver Daily Visits" subtitle="Simple, mobile-friendly workflow for today’s client visits." />
    {alerts.count > 0 && <Card warm><strong>{alerts.count} missed check-in alert(s).</strong> Scheduled visits are past due.</Card>}
    {reminders.length > 0 && <Card title="Care Reminders"><div className="reminder-list">{reminders.slice(0, 4).map((reminder, index) => <div className="reminder-card" key={`${reminder.type}-${index}`}>{reminder.message}</div>)}</div></Card>}
    {loading && <Card>Loading visits...</Card>}
    {error && <Card>{error}</Card>}
    {!loading && !error && todaysVisits.length === 0 && <Card>No visits scheduled for today.</Card>}
    <div className="grid">
      {todaysVisits.map((visit) => (
        <Card key={visit.id}>
          <h3>{visit.client_name}</h3>
          <p>{new Date(visit.scheduled_start).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })} • {visit.service_type || 'General Care'}</p>
          <p>{visit.address}, {visit.city}</p>
          <p><span className={`pill ${visit.status === 'in_progress' ? 'progress' : visit.status}`}>{visit.status.replace('_', ' ')}</span></p>
          <p>{visit.checked_in_at ? 'Checked in' : 'Not checked in'}</p>
          <Link className="btn" to={`/caregiver/visits/${visit.id}`}>View Details</Link>
        </Card>
      ))}
    </div>
  </>);
}
