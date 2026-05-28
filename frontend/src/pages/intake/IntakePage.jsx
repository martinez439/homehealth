import { useState } from 'react';
import { apiPost } from '../../api/client';
import { Card } from '../../components/UI';

export default function IntakePage() {
  const [status, setStatus] = useState('');
  async function submit(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.currentTarget).entries());
    await apiPost('/api/intake', data);
    setStatus('Submitted');
  }
  return <Card title="Client Intake"><form onSubmit={submit} className="form-grid"><input name="client_name" placeholder="Client Name" required/><input name="phone" placeholder="Phone"/><textarea name="care_needs" placeholder="Care needs"/><button>Submit Intake</button>{status && <p>{status}</p>}</form></Card>;
}
