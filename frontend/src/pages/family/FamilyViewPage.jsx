import { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { apiDelete, apiGet, apiPost, apiPut } from '../../api/client';
import { Card, PageHeader, StatusPill } from '../../components/UI';
import Modal from '../../components/ui/Modal';

const contactInitial = { first_name: '', last_name: '', relationship: '', phone: '', email: '', is_primary: false, receives_updates: true };
const messageInitial = { sender_name: '', sender_email: '', message_type: 'general_question', subject: '', message: '' };

const messageTypes = [
  ['general_question', 'General question'],
  ['schedule_request', 'Schedule request'],
  ['care_update_request', 'Care update request'],
  ['billing_question', 'Billing question'],
  ['other', 'Other'],
];

function formatDate(value, options = {}) {
  if (!value) return 'Not yet recorded';
  return new Intl.DateTimeFormat('en-US', { dateStyle: 'medium', timeStyle: 'short', ...options }).format(new Date(value));
}

function formatStatus(status) {
  return (status || 'scheduled').replaceAll('_', ' ');
}

function statusClass(status) {
  if (status === 'completed') return 'completed';
  if (status === 'in_progress') return 'progress';
  if (status === 'missed') return 'missed';
  return 'scheduled';
}

function EmptyState({ children }) {
  return <p className="empty-state">{children}</p>;
}

function TimelineIcon({ type }) {
  const icons = { completed_visit: '✓', care_note: '✍', check_in: '↘', check_out: '↗', family_message: '✉', contact_update: '★' };
  return <span className="timeline-icon" aria-hidden="true">{icons[type] || '•'}</span>;
}

export default function FamilyViewPage() {
  const { clientId } = useParams();
  const [client, setClient] = useState(null);
  const [upcoming, setUpcoming] = useState([]);
  const [completed, setCompleted] = useState([]);
  const [notes, setNotes] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [messages, setMessages] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [contactOpen, setContactOpen] = useState(false);
  const [editingContact, setEditingContact] = useState(null);
  const [contactForm, setContactForm] = useState(contactInitial);
  const [messageForm, setMessageForm] = useState(messageInitial);
  const [messageSuccess, setMessageSuccess] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const [clientData, upcomingData, completedData, notesData, contactsData, messagesData, timelineData] = await Promise.all([
        apiGet(`/api/family/client/${clientId}`),
        apiGet(`/api/family/client/${clientId}/visits/upcoming`),
        apiGet(`/api/family/client/${clientId}/visits/completed`),
        apiGet(`/api/family/client/${clientId}/notes`),
        apiGet(`/api/family/client/${clientId}/contacts`),
        apiGet(`/api/family/client/${clientId}/messages`),
        apiGet(`/api/family/client/${clientId}/timeline`),
      ]);
      setClient(clientData);
      setUpcoming(upcomingData);
      setCompleted(completedData);
      setNotes(notesData);
      setContacts(contactsData);
      setMessages(messagesData);
      setTimeline(timelineData);
    } catch (e) {
      setError('We could not load the family portal right now. Please try again shortly.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [clientId]);

  const lastUpdated = useMemo(() => {
    const timestamps = [client?.last_updated, ...timeline.map((item) => item.timestamp)].filter(Boolean);
    if (!timestamps.length) return 'No updates yet';
    return formatDate(timestamps.sort().at(-1));
  }, [client, timeline]);

  const openCreateContact = () => {
    setEditingContact(null);
    setContactForm(contactInitial);
    setContactOpen(true);
  };

  const openEditContact = (contact) => {
    setEditingContact(contact);
    setContactForm({ ...contact });
    setContactOpen(true);
  };

  const saveContact = async (e) => {
    e.preventDefault();
    if (editingContact) await apiPut(`/api/family/contacts/${editingContact.id}`, contactForm);
    else await apiPost(`/api/family/client/${clientId}/contacts`, contactForm);
    setContactOpen(false);
    setContactForm(contactInitial);
    setEditingContact(null);
    load();
  };

  const deleteContact = async (id) => {
    if (!confirm('Remove this family contact?')) return;
    await apiDelete(`/api/family/contacts/${id}`);
    load();
  };

  const submitMessage = async (e) => {
    e.preventDefault();
    setMessageSuccess('');
    await apiPost(`/api/family/client/${clientId}/messages`, messageForm);
    setMessageForm(messageInitial);
    setMessageSuccess('Thank you — your message was sent to the care team.');
    load();
  };

  if (loading) {
    return <Card warm><p className="family-loading">Preparing the latest care updates...</p></Card>;
  }

  if (error) {
    return <Card warm><p>{error}</p><button className="btn" onClick={load}>Try again</button></Card>;
  }

  return (
    <div className="family-portal">
      <section className="family-hero">
        <div>
          <p className="eyebrow">Family Portal</p>
          <PageHeader title={client?.full_name || `Client #${clientId}`} subtitle="Here’s the latest care activity for your loved one." />
          <div className="family-hero-pills">
            <StatusPill status={{ className: statusClass(client?.status), text: client?.status || 'active' }} />
            {client?.care_level && <span className="pill gold">{client.care_level}</span>}
          </div>
        </div>
        <div className="last-updated-card">
          <span>Last updated</span>
          <strong>{lastUpdated}</strong>
          <p>Care updates are gathered from visits, caregiver notes, and family requests.</p>
        </div>
      </section>

      <div className="family-grid two-col">
        <Card title="Upcoming Visits" warm>
          <div className="visit-list">
            {upcoming.length === 0 && <EmptyState>No upcoming visits are scheduled right now.</EmptyState>}
            {upcoming.map((visit) => (
              <article className="visit-card" key={visit.id}>
                <div>
                  <h3>{formatDate(visit.scheduled_start)}</h3>
                  <p>{visit.caregiver_name} • {visit.service_type || 'Care visit'}</p>
                  {(visit.address || visit.city) && <p className="muted">{[visit.address, visit.city].filter(Boolean).join(', ')}</p>}
                </div>
                <StatusPill status={{ className: statusClass(visit.status), text: formatStatus(visit.status) }} />
              </article>
            ))}
          </div>
        </Card>

        <Card title="Last Updated Timeline">
          <div className="timeline-list">
            {timeline.length === 0 && <EmptyState>No timeline activity yet.</EmptyState>}
            {timeline.map((item) => (
              <article className="timeline-item" key={item.id}>
                <TimelineIcon type={item.type} />
                <div>
                  <h3>{item.title}</h3>
                  <p>{item.description}</p>
                  <time>{formatDate(item.timestamp)}</time>
                </div>
              </article>
            ))}
          </div>
        </Card>
      </div>

      <Card title="Completed Visit Summaries">
        <div className="summary-list">
          {completed.length === 0 && <EmptyState>No completed visits are available yet.</EmptyState>}
          {completed.map((visit) => {
            const completedTasks = (visit.task_checklist || []).filter((task) => task.completed).map((task) => task.label);
            return (
              <article className="summary-card" key={visit.id}>
                <div className="summary-head">
                  <div>
                    <h3>{visit.service_type || 'Completed visit'}</h3>
                    <p>{formatDate(visit.scheduled_start)} with {visit.caregiver_name}</p>
                  </div>
                  <StatusPill status={{ className: 'completed', text: 'completed' }} />
                </div>
                <div className="check-times">
                  <span>Check-in: {formatDate(visit.checked_in_at)}</span>
                  <span>Check-out: {formatDate(visit.checked_out_at)}</span>
                </div>
                <p>{visit.caregiver_notes || visit.notes || 'The visit was completed and documented by the care team.'}</p>
                <div className="task-pills">
                  {completedTasks.length === 0 ? <span className="muted">No completed tasks were marked.</span> : completedTasks.map((task) => <span className="pill completed" key={task}>{task}</span>)}
                </div>
              </article>
            );
          })}
        </div>
      </Card>

      <div className="family-grid two-col">
        <Card title="Care Notes" warm>
          <div className="notes-list">
            {notes.length === 0 && <EmptyState>No family-facing care notes have been added yet.</EmptyState>}
            {notes.map((note) => (
              <article className="note-card" key={note.id}>
                <p>“{note.note}”</p>
                <span>{note.caregiver_name} • {formatDate(note.timestamp)}</span>
              </article>
            ))}
          </div>
        </Card>

        <Card title="Message / Request">
          <form className="form-grid" onSubmit={submitMessage}>
            {messageSuccess && <p className="success-message">{messageSuccess}</p>}
            <input placeholder="Your name" value={messageForm.sender_name} onChange={(e) => setMessageForm({ ...messageForm, sender_name: e.target.value })} required />
            <input type="email" placeholder="Email (optional)" value={messageForm.sender_email || ''} onChange={(e) => setMessageForm({ ...messageForm, sender_email: e.target.value })} />
            <select value={messageForm.message_type} onChange={(e) => setMessageForm({ ...messageForm, message_type: e.target.value })}>
              {messageTypes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
            <input placeholder="Subject" value={messageForm.subject} onChange={(e) => setMessageForm({ ...messageForm, subject: e.target.value })} required />
            <textarea rows="5" placeholder="How can the care team help?" value={messageForm.message} onChange={(e) => setMessageForm({ ...messageForm, message: e.target.value })} required />
            <button className="btn" type="submit">Send Request</button>
          </form>
          <div className="message-history">
            <h3>Recent messages</h3>
            {messages.length === 0 && <EmptyState>No family messages yet.</EmptyState>}
            {messages.slice(0, 3).map((message) => <p key={message.id}><strong>{message.subject}</strong> <span className="muted">({formatStatus(message.status)})</span></p>)}
          </div>
        </Card>
      </div>

      <Card title="Family Contacts">
        <div className="section-actions"><button className="btn" type="button" onClick={openCreateContact}>Add Family Contact</button></div>
        <div className="contacts-grid">
          {contacts.length === 0 && <EmptyState>No family contacts are on file.</EmptyState>}
          {contacts.map((contact) => (
            <article className="contact-card" key={contact.id}>
              <div>
                <h3>{contact.first_name} {contact.last_name}</h3>
                <p>{contact.relationship || 'Family contact'}</p>
                <p className="muted">{contact.phone || 'No phone'} • {contact.email || 'No email'}</p>
              </div>
              <div className="task-pills">
                {contact.is_primary && <span className="pill gold">Primary contact</span>}
                {contact.receives_updates && <span className="pill scheduled">Receives updates</span>}
              </div>
              <div className="actions">
                <button className="btn subtle" type="button" onClick={() => openEditContact(contact)}>Edit</button>
                <button className="btn subtle danger" type="button" onClick={() => deleteContact(contact.id)}>Delete</button>
              </div>
            </article>
          ))}
        </div>
      </Card>

      <Modal isOpen={contactOpen} title={editingContact ? 'Edit Family Contact' : 'Add Family Contact'} onClose={() => setContactOpen(false)}>
        <form className="form-grid" onSubmit={saveContact}>
          <input placeholder="First name" value={contactForm.first_name} onChange={(e) => setContactForm({ ...contactForm, first_name: e.target.value })} required />
          <input placeholder="Last name" value={contactForm.last_name} onChange={(e) => setContactForm({ ...contactForm, last_name: e.target.value })} required />
          <input placeholder="Relationship" value={contactForm.relationship} onChange={(e) => setContactForm({ ...contactForm, relationship: e.target.value })} />
          <input placeholder="Phone" value={contactForm.phone} onChange={(e) => setContactForm({ ...contactForm, phone: e.target.value })} />
          <input type="email" placeholder="Email" value={contactForm.email} onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })} />
          <label className="checkbox-row"><input type="checkbox" checked={contactForm.is_primary} onChange={(e) => setContactForm({ ...contactForm, is_primary: e.target.checked })} /> Primary contact</label>
          <label className="checkbox-row"><input type="checkbox" checked={contactForm.receives_updates} onChange={(e) => setContactForm({ ...contactForm, receives_updates: e.target.checked })} /> Receives care updates</label>
          <div className="actions"><button className="btn subtle" type="button" onClick={() => setContactOpen(false)}>Cancel</button><button className="btn" type="submit">Save Contact</button></div>
        </form>
      </Modal>
    </div>
  );
}
