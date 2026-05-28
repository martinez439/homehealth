import { useEffect, useState } from 'react';
import { apiDelete, apiGet, apiPost, apiPut } from '../../api/client';
import { Card, DataTable, PageHeader, StatusPill } from '../../components/UI';
import Modal from '../../components/ui/Modal';

const initial = { first_name: '', last_name: '', phone: '', email: '', certification: '', availability_notes: '', status: 'available', notes: '' };

export default function AdminCaregiversPage() {
  const [items, setItems] = useState([]); const [form, setForm] = useState(initial); const [editId, setEditId] = useState(null); const [createOpen, setCreateOpen] = useState(false);
  const [availability, setAvailability] = useState({}); const [availabilityError, setAvailabilityError] = useState('');
  const loadAvailability = async (caregivers) => { const entries = await Promise.all(caregivers.map(async (c) => [c.id, await apiGet(`/api/caregivers/${c.id}/availability`)])); setAvailability(Object.fromEntries(entries)); };
  const load = () => apiGet('/api/caregivers').then((caregivers) => { setItems(caregivers); return loadAvailability(caregivers); }).catch((e) => setAvailabilityError(e.message));
  useEffect(() => { load(); }, []);
  const submit = async (e, mode = 'create') => { e.preventDefault(); mode === 'edit' && editId ? await apiPut(`/api/caregivers/${editId}`, form) : await apiPost('/api/caregivers', form); setForm(initial); setEditId(null); setCreateOpen(false); load(); };
  const remove = async (id) => { if (confirm('Delete caregiver?')) { await apiDelete(`/api/caregivers/${id}`); load(); } };
  const updateAvailability = async (caregiverId, row, patch) => {
    setAvailabilityError('');
    const payload = { day_of_week: row.day_of_week, available: row.available, start_time: row.start_time, end_time: row.end_time, notes: row.notes || '', ...patch };
    if (!payload.available) { payload.start_time = null; payload.end_time = null; }
    else { payload.start_time = payload.start_time || '08:00'; payload.end_time = payload.end_time || '17:00'; }
    try {
      if (row.id) await apiPut(`/api/caregivers/availability/${row.id}`, payload);
      else await apiPost(`/api/caregivers/${caregiverId}/availability`, payload);
      const refreshed = await apiGet(`/api/caregivers/${caregiverId}/availability`);
      setAvailability((current) => ({ ...current, [caregiverId]: refreshed }));
    } catch (e) { setAvailabilityError(e.message); }
  };
  const rowsFor = (caregiverId) => Array.from({ length: 7 }, (_, day) => (availability[caregiverId] || []).find((row) => row.day_of_week === day) || { day_of_week: day, available: false, start_time: '', end_time: '', notes: '' });
  const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  return <>
    <PageHeader title="Caregiver Database" subtitle="Track caregiver readiness, workload, and assignment quality." />
    <div className='section-actions'><button className='btn' onClick={() => { setForm(initial); setCreateOpen(true); }}>Create New Caregiver</button></div>

    {editId && <Card title='Edit Caregiver'>
      <form className='form-grid' onSubmit={(e) => submit(e, 'edit')}>
        <input required placeholder='First name' value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
        <input required placeholder='Last name' value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
        <input placeholder='Phone' value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        <input placeholder='Email' value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input placeholder='Certification' value={form.certification} onChange={(e) => setForm({ ...form, certification: e.target.value })} />
        <input placeholder='Status' value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} />
        <div className='actions'><button className='btn'>Update Caregiver</button><button className='btn' type='button' onClick={() => { setForm(initial); setEditId(null); }}>Cancel</button></div>
      </form>
    </Card>}

    <Modal isOpen={createOpen} title='Create Caregiver' onClose={() => setCreateOpen(false)}>
      <form className='form-grid' onSubmit={submit}>
        <input required placeholder='First name' value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
        <input required placeholder='Last name' value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
        <input placeholder='Phone' value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        <input placeholder='Email' value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input placeholder='Certification' value={form.certification} onChange={(e) => setForm({ ...form, certification: e.target.value })} />
        <input placeholder='Status' value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} />
        <div className='actions'><button className='btn' type='button' onClick={() => setCreateOpen(false)}>Cancel</button><button className='btn'>Create Caregiver</button></div>
      </form>
    </Modal>

    <Card>
      <DataTable headers={['Initial', 'Name', 'Certification', 'Availability', 'Status', 'Actions']} rows={items.map((c) => ({ id: c.id, cells: [c.first_name?.[0] || '-', `${c.first_name} ${c.last_name}`, c.certification, c.availability_notes || 'Weekly windows below', <StatusPill status={{ className: c.status === 'on_shift' ? 'progress' : 'scheduled', text: c.status }} />, <div className='actions'><button className='btn' onClick={() => { setForm(c); setEditId(c.id); }}>Edit</button><button className='btn' onClick={() => remove(c.id)}>Delete</button></div>] }))} />
    </Card>

    <Card title='Availability'>
      {availabilityError && <p className='empty-state'>Unable to save availability: {availabilityError}</p>}
      {items.length === 0 ? <p className='empty-state'>Create a caregiver to manage weekly availability.</p> : <div className='availability-grid'>
        {items.map((caregiver) => <div className='availability-card' key={caregiver.id}>
          <h3>{caregiver.first_name} {caregiver.last_name}</h3>
          {rowsFor(caregiver.id).map((row) => <div className='availability-row' key={row.day_of_week}>
            <label className='checkbox-row'><input type='checkbox' checked={!!row.available} onChange={(e) => updateAvailability(caregiver.id, row, { available: e.target.checked })} /> {dayNames[row.day_of_week]}</label>
            {row.available ? <div className='availability-times'><input type='time' value={row.start_time || '08:00'} onChange={(e) => updateAvailability(caregiver.id, row, { start_time: e.target.value })} /><span>to</span><input type='time' value={row.end_time || '17:00'} onChange={(e) => updateAvailability(caregiver.id, row, { end_time: e.target.value })} /></div> : <span className='muted'>Unavailable</span>}
          </div>)}
        </div>)}
      </div>}
    </Card>
  </>;
}
