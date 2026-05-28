import { useEffect, useMemo, useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import { apiDelete, apiGet, apiPost, apiPut } from '../../api/client';
import { Card, PageHeader, StatCard, StatusPill } from '../../components/UI';
import Modal from '../../components/ui/Modal';

const initialVisit = { client_id: '', caregiver_id: '', scheduled_start: '', scheduled_end: '', status: 'scheduled', service_type: '', notes: '' };
const initialFilters = { caregiver_id: '', client_id: '', status: '' };
const statusClass = (s) => ({ scheduled: 'scheduled', in_progress: 'progress', completed: 'completed', missed: 'missed' }[s] || 'scheduled');
const statusColors = { scheduled: '#67c9c7', in_progress: '#c7a86d', completed: '#79b77a', missed: '#d98282' };

const toLocalInput = (value) => (value ? value.slice(0, 16) : '');
const names = (items) => items.reduce((acc, item) => ({ ...acc, [item.id]: `${item.first_name} ${item.last_name}` }), {});

function conflictMessage(error) {
  try {
    const parsed = JSON.parse(error.message);
    return parsed.detail?.message || parsed.detail || error.message;
  } catch {
    return error.message;
  }
}

export default function AdminSchedulePage() {
  const [visits, setVisits] = useState([]);
  const [clients, setClients] = useState([]);
  const [caregivers, setCaregivers] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [reminders, setReminders] = useState([]);
  const [form, setForm] = useState(initialVisit);
  const [filters, setFilters] = useState(initialFilters);
  const [editId, setEditId] = useState(null);
  const [modalVisit, setModalVisit] = useState(null);
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurrenceRule, setRecurrenceRule] = useState('weekly');
  const [recurrenceEndDate, setRecurrenceEndDate] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => value && params.set(key, value));
      const calendarPath = `/api/schedule/calendar${params.toString() ? `?${params}` : ''}`;
      const [visitData, clientData, caregiverData, conflictData, summaryData, reminderData] = await Promise.all([
        apiGet(calendarPath),
        apiGet('/api/clients'),
        apiGet('/api/caregivers'),
        apiGet('/api/schedule/conflicts'),
        apiGet('/api/schedule/daily-summary'),
        apiGet('/api/schedule/upcoming-reminders'),
      ]);
      setVisits(visitData);
      setClients(clientData);
      setCaregivers(caregiverData);
      setConflicts(conflictData);
      setSummary(summaryData);
      setReminders(reminderData);
    } catch (e) {
      setError(`Unable to load schedule: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [filters]);

  const clientNames = useMemo(() => names(clients), [clients]);
  const caregiverNames = useMemo(() => names(caregivers), [caregivers]);
  const conflictVisitIds = useMemo(() => new Set(conflicts.flatMap((c) => c.visit_ids || [])), [conflicts]);
  const selectedVisit = modalVisit ? visits.find((v) => v.id === modalVisit.id) || modalVisit : null;

  const events = visits.map((visit) => ({
    id: String(visit.id),
    title: `${visit.client_name} • ${visit.service_type || 'Care Visit'}`,
    start: visit.scheduled_start,
    end: visit.scheduled_end,
    backgroundColor: statusColors[visit.status] || statusColors.scheduled,
    borderColor: conflictVisitIds.has(visit.id) || visit.has_conflict ? '#8b3b3b' : statusColors[visit.status] || statusColors.scheduled,
    classNames: conflictVisitIds.has(visit.id) || visit.has_conflict ? ['calendar-conflict'] : [],
    extendedProps: visit,
  }));

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    const payload = { ...form, client_id: Number(form.client_id), caregiver_id: Number(form.caregiver_id) };
    try {
      if (isRecurring && !editId) {
        await apiPost('/api/schedule/recurring', { ...payload, recurrence_rule: recurrenceRule, recurrence_end_date: recurrenceEndDate });
      } else if (editId) {
        await apiPut(`/api/schedule/visits/${editId}`, payload);
      } else {
        await apiPost('/api/schedule/visits', payload);
      }
      setForm(initialVisit);
      setEditId(null);
      setIsRecurring(false);
      setRecurrenceEndDate('');
      await load();
    } catch (e) {
      setError(conflictMessage(e));
    } finally {
      setSaving(false);
    }
  };

  const editVisit = (visit) => {
    setForm({
      client_id: visit.client_id,
      caregiver_id: visit.caregiver_id,
      scheduled_start: toLocalInput(visit.scheduled_start),
      scheduled_end: toLocalInput(visit.scheduled_end),
      status: visit.status,
      service_type: visit.service_type || '',
      notes: visit.notes || '',
    });
    setEditId(visit.id);
    setIsRecurring(false);
    setModalVisit(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const deleteVisit = async (id) => {
    if (!confirm('Delete visit?')) return;
    await apiDelete(`/api/schedule/visits/${id}`);
    setModalVisit(null);
    load();
  };

  const moveVisit = async (info) => {
    const visitId = info.event.id;
    try {
      await apiPost(`/api/schedule/visits/${visitId}/move`, {
        scheduled_start: info.event.start.toISOString(),
        scheduled_end: (info.event.end || info.event.start).toISOString(),
      });
      await load();
    } catch (e) {
      info.revert();
      setError(conflictMessage(e));
    }
  };

  return <>
    <PageHeader title="Scheduling Operations" subtitle="Recurring visits, conflict-aware calendar moves, reminders, and daily staffing clarity." />

    {error && <Card warm><strong>Scheduling warning:</strong> {error}</Card>}
    {loading && <Card>Loading polished concierge schedule…</Card>}

    {summary && <section className="grid stats schedule-summary">
      <StatCard label="Visits Today" value={summary.total_visits} />
      <StatCard label="Completed" value={summary.completed_visits} />
      <StatCard label="Missed" value={summary.missed_visits} />
      <StatCard label="Caregivers On Shift" value={summary.caregivers_on_shift} />
    </section>}

    <section className="grid schedule-operational-grid">
      <Card title="Reminder Center">
        {reminders.length === 0 ? <p className="empty-state">No reminder-ready alerts right now.</p> : <div className="reminder-list">{reminders.map((reminder, index) => <div className="reminder-card" key={`${reminder.type}-${reminder.visit_id}-${index}`}>{reminder.message}</div>)}</div>}
      </Card>
      <Card title="Unresolved Conflicts">
        {conflicts.length === 0 ? <p className="empty-state">No conflicts detected.</p> : <div className="reminder-list">{conflicts.map((conflict, index) => <div className={`conflict-card ${conflict.severity}`} key={`${conflict.type}-${index}`}><strong>{conflict.type.replace('_', ' ')}</strong><span>{conflict.message}</span></div>)}</div>}
      </Card>
    </section>

    <Card title={editId ? 'Edit Visit' : 'Create Visit'}>
      <form className="form-grid schedule-form" onSubmit={submit}>
        <select required value={form.client_id} onChange={(e) => setForm({ ...form, client_id: e.target.value })}><option value="">Client</option>{clients.map((c) => <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>)}</select>
        <select required value={form.caregiver_id} onChange={(e) => setForm({ ...form, caregiver_id: e.target.value })}><option value="">Caregiver</option>{caregivers.map((c) => <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>)}</select>
        <input required type="datetime-local" value={form.scheduled_start} onChange={(e) => setForm({ ...form, scheduled_start: e.target.value })} />
        <input required type="datetime-local" value={form.scheduled_end} onChange={(e) => setForm({ ...form, scheduled_end: e.target.value })} />
        <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}><option>scheduled</option><option>in_progress</option><option>completed</option><option>missed</option></select>
        <input placeholder="Service type" value={form.service_type} onChange={(e) => setForm({ ...form, service_type: e.target.value })} />
        <textarea placeholder="Visit notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        {!editId && <label className="checkbox-row"><input type="checkbox" checked={isRecurring} onChange={(e) => setIsRecurring(e.target.checked)} /> Create recurring visit series</label>}
        {isRecurring && !editId && <>
          <select value={recurrenceRule} onChange={(e) => setRecurrenceRule(e.target.value)}><option value="daily">Daily</option><option value="weekly">Weekly</option><option value="biweekly">Biweekly</option><option value="monthly">Monthly</option></select>
          <input required type="date" value={recurrenceEndDate} onChange={(e) => setRecurrenceEndDate(e.target.value)} />
        </>}
        <div className="actions"><button className="btn" disabled={saving}>{saving ? 'Saving…' : editId ? 'Update Visit' : 'Create Visit'}</button>{editId && <button className="btn subtle" type="button" onClick={() => { setForm(initialVisit); setEditId(null); }}>Cancel</button>}</div>
      </form>
    </Card>

    <Card title="Operational Calendar">
      <div className="calendar-filters">
        <select value={filters.caregiver_id} onChange={(e) => setFilters({ ...filters, caregiver_id: e.target.value })}><option value="">All caregivers</option>{caregivers.map((c) => <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>)}</select>
        <select value={filters.client_id} onChange={(e) => setFilters({ ...filters, client_id: e.target.value })}><option value="">All clients</option>{clients.map((c) => <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>)}</select>
        <select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}><option value="">All statuses</option><option>scheduled</option><option>in_progress</option><option>completed</option><option>missed</option></select>
        <button className="btn subtle" onClick={() => setFilters(initialFilters)}>Reset filters</button>
      </div>
      {!loading && visits.length === 0 ? <p className="empty-state">No visits match the current filters.</p> : <div className="calendar-shell">
        <FullCalendar
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="timeGridWeek"
          headerToolbar={{ left: 'prev,next today', center: 'title', right: 'dayGridMonth,timeGridWeek,timeGridDay' }}
          events={events}
          editable
          eventDrop={moveVisit}
          eventResize={moveVisit}
          eventClick={(info) => setModalVisit(info.event.extendedProps)}
          height="auto"
          slotMinTime="06:00:00"
          slotMaxTime="22:00:00"
          eventContent={(arg) => {
            const visit = arg.event.extendedProps;
            return <div className="calendar-event-card"><strong>{visit.client_name}</strong><span>{visit.caregiver_name}</span><span>{arg.timeText} • {visit.service_type || 'Care Visit'}</span><em>{visit.status.replace('_', ' ')}</em></div>;
          }}
        />
      </div>}
    </Card>

    <Modal isOpen={!!selectedVisit} title="Visit Details" onClose={() => setModalVisit(null)}>
      {selectedVisit && <div className="visit-modal">
        {conflictVisitIds.has(selectedVisit.id) && <div className="conflict-card severe"><strong>Conflict detected</strong><span>Review caregiver availability and overlapping appointments before operating this visit.</span></div>}
        <p><strong>Client:</strong> {clientNames[selectedVisit.client_id] || selectedVisit.client_name}</p>
        <p><strong>Caregiver:</strong> {caregiverNames[selectedVisit.caregiver_id] || selectedVisit.caregiver_name}</p>
        <p><strong>Time:</strong> {new Date(selectedVisit.scheduled_start).toLocaleString()} – {new Date(selectedVisit.scheduled_end).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}</p>
        <p><strong>Service:</strong> {selectedVisit.service_type || 'General Care'}</p>
        <p><strong>Status:</strong> <StatusPill status={{ className: statusClass(selectedVisit.status), text: selectedVisit.status }} /></p>
        <p><strong>Notes:</strong> {selectedVisit.notes || 'No notes yet.'}</p>
        <div className="actions"><button className="btn" onClick={() => editVisit(selectedVisit)}>Edit</button><button className="btn danger subtle" onClick={() => deleteVisit(selectedVisit.id)}>Delete</button></div>
      </div>}
    </Modal>
  </>;
}
