import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { apiGet, apiPost, apiPut } from '../../api/client';
import { Card, PageHeader } from '../../components/UI';

export default function VisitDetailsPage() {
  const { id } = useParams();
  const [visit, setVisit] = useState(null);
  const [notes, setNotes] = useState('');
  const [mileageStart, setMileageStart] = useState('');
  const [mileageEnd, setMileageEnd] = useState('');
  const [msg, setMsg] = useState('');

  const load = () => apiGet(`/api/caregiver/visits/${id}`).then((v) => {
    setVisit(v); setNotes(v.caregiver_notes || ''); setMileageStart(v.mileage_start ?? ''); setMileageEnd(v.mileage_end ?? '');
  });
  useEffect(() => { load(); }, [id]);
  if (!visit) return <Card>Loading visit...</Card>;

  const isMissed = visit.status === 'scheduled' && new Date(visit.scheduled_start) < new Date() && !visit.checked_in_at;
  return (<>
    <PageHeader title={`Visit #${id}`} subtitle="Check in, complete tasks, add notes, and check out." />
    {isMissed && <Card warm>This visit is past scheduled start and still needs check-in.</Card>}
    <Card title="Visit Overview">
      <p><strong>{visit.client_name}</strong></p><p>{visit.service_type}</p><p>{visit.address}, {visit.city}</p>
      <p>{new Date(visit.scheduled_start).toLocaleString()} - {new Date(visit.scheduled_end).toLocaleTimeString()}</p>
      <span className={`pill ${visit.status === 'in_progress' ? 'progress' : visit.status}`}>{visit.status}</span>
    </Card>
    <Card title="Check In / Check Out">
      <div className="actions">
        <button className="btn" disabled={visit.status !== 'scheduled'} onClick={() => apiPost(`/api/caregiver/visits/${id}/check-in`, { location: 'GPS capture coming soon' }).then(load)}>Check In</button>
        <button className="btn" disabled={visit.status !== 'in_progress'} onClick={() => apiPost(`/api/caregiver/visits/${id}/check-out`, { location: 'GPS capture coming soon' }).then(load)}>Check Out</button>
      </div>
    </Card>
    <Card title="Task Checklist">
      {(visit.task_checklist || []).map((task, idx) => <label key={idx}><input type="checkbox" checked={task.completed} onChange={(e) => setVisit({ ...visit, task_checklist: visit.task_checklist.map((t, i) => i === idx ? { ...t, completed: e.target.checked } : t) })} /> {task.label}</label>)}
      <div><button className="btn" onClick={() => apiPut(`/api/caregiver/visits/${id}/tasks`, { task_checklist: visit.task_checklist }).then(() => setMsg('Tasks saved'))}>Save Tasks</button></div>
    </Card>
    <Card title="Visit Notes"><textarea value={notes} onChange={(e) => setNotes(e.target.value)} /><button className="btn" onClick={() => apiPost(`/api/caregiver/visits/${id}/notes`, { caregiver_notes: notes }).then(() => setMsg('Notes saved'))}>Save Note</button></Card>
    <Card title="Mileage / Location"><p>GPS capture coming soon.</p><input placeholder="Mileage start" value={mileageStart} onChange={(e) => setMileageStart(e.target.value)} /><input placeholder="Mileage end" value={mileageEnd} onChange={(e) => setMileageEnd(e.target.value)} /><p>Total: {visit.mileage_total ?? '--'}</p><button className="btn" onClick={() => apiPut(`/api/caregiver/visits/${id}/mileage`, { mileage_start: mileageStart === '' ? null : Number(mileageStart), mileage_end: mileageEnd === '' ? null : Number(mileageEnd) }).then(load)}>Save Mileage</button></Card>
    {msg && <Card>{msg}</Card>}
  </>);
}
