import { useEffect, useState } from 'react';
import { apiGet, apiPost, apiPut } from '../../api/client';
import { Card, PageHeader } from '../../components/UI';
import Modal from '../../components/ui/Modal';

const initial = { client_name: '', phone: '', email: '', city: '', care_needs: '', preferred_schedule: '', urgency: 'normal', status: 'new', notes: '' };

export default function IntakePage() {
  const [form, setForm] = useState(initial); const [status, setStatus] = useState(''); const [requests, setRequests] = useState([]); const [editId, setEditId] = useState(null); const [createOpen, setCreateOpen] = useState(false);
  const load = () => apiGet('/api/intake').then(setRequests);
  useEffect(() => { load(); }, []);
  const submit = async (e, mode = 'create') => {
    e.preventDefault();
    mode === 'edit' && editId ? await apiPut(`/api/intake/${editId}`, form) : await apiPost('/api/intake', form);
    setStatus('Intake submitted successfully.'); setForm(initial); setEditId(null); setCreateOpen(false); load();
  };

  return <>
    <PageHeader title="Client Intake" subtitle="Step 1 of 5 • Compassionate onboarding for families and clients." />
    <div className='section-actions'><button className='btn' onClick={() => { setForm(initial); setCreateOpen(true); }}>Create New Intake Request</button></div>

    {editId && <Card warm title='Edit Intake Request'>
      <form onSubmit={(e) => submit(e, 'edit')} className="form-grid">
        <input value={form.client_name} onChange={(e) => setForm({ ...form, client_name: e.target.value })} placeholder="Client Full Name" required />
        <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="Preferred Phone" />
        <input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="Email (optional)" />
        <input value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} placeholder="City" />
        <textarea value={form.care_needs} onChange={(e) => setForm({ ...form, care_needs: e.target.value })} placeholder="Care needs" rows={4} />
        <input value={form.preferred_schedule} onChange={(e) => setForm({ ...form, preferred_schedule: e.target.value })} placeholder="Preferred schedule" />
        <div className="actions"><button className="btn" type="submit">Update Intake</button><button className='btn' type='button' onClick={() => { setForm(initial); setEditId(null); }}>Cancel</button></div>
      </form>
    </Card>}

    <Modal isOpen={createOpen} title='Create Intake Request' onClose={() => setCreateOpen(false)}>
      <form onSubmit={submit} className="form-grid">
        <input value={form.client_name} onChange={(e) => setForm({ ...form, client_name: e.target.value })} placeholder="Client Full Name" required />
        <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="Preferred Phone" />
        <input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="Email (optional)" />
        <input value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} placeholder="City" />
        <textarea value={form.care_needs} onChange={(e) => setForm({ ...form, care_needs: e.target.value })} placeholder="Care needs" rows={4} />
        <input value={form.preferred_schedule} onChange={(e) => setForm({ ...form, preferred_schedule: e.target.value })} placeholder="Preferred schedule" />
        <div className="actions"><button className='btn' type='button' onClick={() => setCreateOpen(false)}>Cancel</button><button className="btn" type="submit">Submit Intake</button></div>
        {status && <p>{status}</p>}
      </form>
    </Modal>

    <Card title='Recent Intake Requests'>{requests.map((r) => <p key={r.id}><button className='btn' onClick={() => { setForm(r); setEditId(r.id); }}>Edit</button> {r.client_name} — {r.status}</p>)}</Card>
  </>;
}
