import { useEffect, useState } from 'react';
import { apiDelete, apiGet, apiPost, apiPut } from '../../api/client';
import { Card, PageHeader, StatusPill } from '../../components/UI';

const init = { client_id: '', caregiver_id: '', scheduled_start: '', scheduled_end: '', status: 'scheduled', service_type: '', notes: '' };
const styleFor = (s) => ({ scheduled: 'scheduled', in_progress: 'progress', completed: 'completed', missed: 'missed' }[s] || 'scheduled');

export default function AdminSchedulePage() {
  const [visits, setVisits] = useState([]); const [clients, setClients] = useState([]); const [caregivers, setCaregivers] = useState([]); const [form, setForm] = useState(init); const [editId, setEditId] = useState(null);
  const load = async () => { const [v, c, g] = await Promise.all([apiGet('/api/visits'), apiGet('/api/clients'), apiGet('/api/caregivers')]); setVisits(v); setClients(c); setCaregivers(g); };
  useEffect(() => { load(); }, []);
  const submit = async (e) => { e.preventDefault(); const payload = { ...form, client_id: Number(form.client_id), caregiver_id: Number(form.caregiver_id) }; editId ? await apiPut(`/api/visits/${editId}`, payload) : await apiPost('/api/visits', payload); setForm(init); setEditId(null); load(); };

  return <>
    <PageHeader title="Scheduling Calendar" subtitle="A soft, glanceable timeline for visits and staffing." />
    <Card title={editId ? 'Edit Visit' : 'Create Visit'}>
      <form className='form-grid' onSubmit={submit}>
        <select required value={form.client_id} onChange={(e) => setForm({ ...form, client_id: e.target.value })}><option value=''>Client</option>{clients.map((c) => <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>)}</select>
        <select required value={form.caregiver_id} onChange={(e) => setForm({ ...form, caregiver_id: e.target.value })}><option value=''>Caregiver</option>{caregivers.map((c) => <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>)}</select>
        <input required type='datetime-local' value={form.scheduled_start} onChange={(e) => setForm({ ...form, scheduled_start: e.target.value })} />
        <input required type='datetime-local' value={form.scheduled_end} onChange={(e) => setForm({ ...form, scheduled_end: e.target.value })} />
        <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}><option>scheduled</option><option>in_progress</option><option>completed</option><option>missed</option></select>
        <input placeholder='Service type' value={form.service_type} onChange={(e) => setForm({ ...form, service_type: e.target.value })} />
        <div className='actions'><button className='btn'>{editId ? 'Update' : 'Create'} Visit</button></div>
      </form>
    </Card>
    <Card title="Visits">
      <div className='table-wrap'>{visits.map((v) => <div className='table-row' key={v.id}><div>#{v.id}</div><div>{new Date(v.scheduled_start).toLocaleString()}</div><div>{v.service_type || '-'}</div><div><StatusPill status={{ className: styleFor(v.status), text: v.status }} /></div><div className='actions'><button className='btn' onClick={() => { setForm({ ...v, scheduled_start: v.scheduled_start.slice(0, 16), scheduled_end: v.scheduled_end.slice(0, 16) }); setEditId(v.id); }}>Edit</button><button className='btn' onClick={async () => { if (confirm('Delete visit?')) { await apiDelete(`/api/visits/${v.id}`); load(); } }}>Delete</button></div></div>)}</div>
    </Card>
  </>;
}
