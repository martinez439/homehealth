import { useEffect, useState } from 'react';
import { apiDelete, apiGet, apiPost, apiPut } from '../../api/client';
import { Card, DataTable, PageHeader, StatusPill } from '../../components/UI';

const initial = { first_name: '', last_name: '', phone: '', email: '', certification: '', availability_notes: '', status: 'available', notes: '' };

export default function AdminCaregiversPage() {
  const [items, setItems] = useState([]); const [form, setForm] = useState(initial); const [editId, setEditId] = useState(null);
  const load = () => apiGet('/api/caregivers').then(setItems);
  useEffect(() => { load(); }, []);
  const submit = async (e) => { e.preventDefault(); editId ? await apiPut(`/api/caregivers/${editId}`, form) : await apiPost('/api/caregivers', form); setForm(initial); setEditId(null); load(); };
  const remove = async (id) => { if (confirm('Delete caregiver?')) { await apiDelete(`/api/caregivers/${id}`); load(); } };

  return <>
    <PageHeader title="Caregiver Database" subtitle="Track caregiver readiness, workload, and assignment quality." />
    <Card title={editId ? 'Edit Caregiver' : 'Create Caregiver'}>
      <form className='form-grid' onSubmit={submit}>
        <input required placeholder='First name' value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
        <input required placeholder='Last name' value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
        <input placeholder='Phone' value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        <input placeholder='Email' value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input placeholder='Certification' value={form.certification} onChange={(e) => setForm({ ...form, certification: e.target.value })} />
        <input placeholder='Status' value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} />
        <div className='actions'><button className='btn'>{editId ? 'Update' : 'Create'} Caregiver</button></div>
      </form>
    </Card>
    <Card>
      <DataTable headers={['Initial', 'Name', 'Certification', 'Availability', 'Status', 'Actions']} rows={items.map((c) => ({ id: c.id, cells: [c.first_name?.[0] || '-', `${c.first_name} ${c.last_name}`, c.certification, c.availability_notes || '-', <StatusPill status={{ className: c.status === 'on_shift' ? 'progress' : 'scheduled', text: c.status }} />, <div className='actions'><button className='btn' onClick={() => { setForm(c); setEditId(c.id); }}>Edit</button><button className='btn' onClick={() => remove(c.id)}>Delete</button></div>] }))} />
    </Card>
  </>;
}
