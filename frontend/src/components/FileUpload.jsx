import { useState } from 'react';
import { getStoredToken } from '../api/auth';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function FileUpload({ ownerType = 'admin', ownerId = '' }) {
  const [status, setStatus] = useState('');

  async function handleChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    const form = new FormData();
    form.append('upload', file);
    form.append('owner_type', ownerType);
    if (ownerId) form.append('owner_id', ownerId);
    setStatus('Uploading…');
    const response = await fetch(`${API_URL}/api/files/upload`, { method: 'POST', headers: { Authorization: `Bearer ${getStoredToken()}` }, body: form });
    setStatus(response.ok ? 'File uploaded securely.' : 'Upload failed. Check file type and size.');
  }

  return <label className="file-upload">Secure file upload<input type="file" onChange={handleChange} accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" /><span>{status}</span></label>;
}
