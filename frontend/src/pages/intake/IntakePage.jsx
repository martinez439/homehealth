import { useState } from 'react';
import { apiPost } from '../../api/client';
import { Card, PageHeader } from '../../components/UI';

export default function IntakePage() {
  const [status, setStatus] = useState('');
  async function submit(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.currentTarget).entries());
    await apiPost('/api/intake', data);
    setStatus('Draft saved and intake submitted successfully.');
  }

  return (
    <>
      <PageHeader title="Client Intake" subtitle="Step 1 of 5 • Compassionate onboarding for families and clients." />
      <Card warm>
        <form onSubmit={submit} className="form-grid">
          <input name="client_name" placeholder="Client Full Name" required />
          <input name="phone" placeholder="Preferred Phone" />
          <select name="care_level" defaultValue="">
            <option value="" disabled>Care needs level</option><option>Companion</option><option>Personal Care</option><option>Skilled Nursing</option>
          </select>
          <textarea name="care_needs" placeholder="Care needs, routines, and preferences" rows={5} />
          <textarea name="emergency_contacts" placeholder="Emergency contacts" rows={3} />
          <div className="actions"><button className="btn" type="submit">Save & Continue</button></div>
          {status && <p>{status}</p>}
        </form>
      </Card>
    </>
  );
}
