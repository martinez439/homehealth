import { useEffect, useState } from 'react';
import { apiDelete, apiGet, apiPost, apiPut } from '../../api/client';
import { Card, DataTable, PageHeader, StatusPill } from '../../components/UI';

const initial = { first_name: '', last_name: '', phone: '', care_level: '', status: 'active', city: '', state: '' };

export default function AdminClientsPage() {
  const [clients, setClients] = useState([]); const [form, setForm] = useState(initial); const [editId, setEditId] = useState(null); const [error, setError] = useState('');
  const load = () => apiGet('/api/clients').then(setClients).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    const payload = { ...initial, ...form };
    if (editId) await apiPut(`/api/clients/${editId}`, payload); else await apiPost('/api/clients', payload);
    setForm(initial); setEditId(null); load();
  };
  const remove = async (id) => { if (confirm('Delete this client?')) { await apiDelete(`/api/clients/${id}`); load(); } };
  const rows = clients.map((c) => ({
    id: c.id,
    cells: [
      c.first_name || '-',
      c.last_name || '-',
      c.phone || '-',
      <StatusPill status={{ className: c.status === 'active' ? 'completed' : 'scheduled', text: c.status }} />,
      <div className='actions'><button className='btn' onClick={() => { setForm(c); setEditId(c.id); }}>Edit</button><button className='btn' onClick={() => remove(c.id)}>Delete</button></div>,
    ],
  }));

  return <>
    <PageHeader title="Client Database" subtitle="People-first records with quick care actions." />
    {error && <Card>{error}</Card>}
    <Card title={editId ? 'Edit Client' : 'Create Client'}>
      <form onSubmit={submit} className="form-grid">
        <input placeholder='First name' value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} required />
        <input placeholder='Last name' value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} required />
        <input placeholder='Phone' value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} required />
        <input placeholder='Care level' value={form.care_level} onChange={(e) => setForm({ ...form, care_level: e.target.value })} />
        <input placeholder='City' value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} />
        <input placeholder='State' value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })} />
        <div className='actions'><button className='btn' type='submit'>{editId ? 'Update' : 'Create'} Client</button></div>
      </form>
    </Card>
    <Card>
      <DataTable headers={['First Name', 'Last Name', 'Phone', 'Status', 'Actions']} rows={rows} />
    </Card>
  </>;
}
