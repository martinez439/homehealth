import { useEffect, useState } from 'react';
import { apiGet } from '../../api/client';

export default function AdminAuditLogsPage() {
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    const qs = filter ? `?action=${encodeURIComponent(filter)}` : '';
    apiGet(`/api/admin/audit-logs${qs}`).then(setLogs).catch(() => setLogs([]));
  }, [filter]);

  return (
    <section className="page-card">
      <div className="section-heading">
        <div><p className="eyebrow">Admin</p><h2>Audit Logs</h2></div>
        <input className="search compact" placeholder="Filter by action" value={filter} onChange={(e) => setFilter(e.target.value)} />
      </div>
      <div className="table-wrap">
        <table className="data-table">
          <thead><tr><th>Time</th><th>Actor</th><th>Role</th><th>Action</th><th>Entity</th><th>Description</th></tr></thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td>{new Date(log.created_at).toLocaleString()}</td>
                <td>{log.actor_email || 'System'}</td>
                <td>{log.actor_role || '—'}</td>
                <td>{log.action}</td>
                <td>{log.entity_type}{log.entity_id ? ` #${log.entity_id}` : ''}</td>
                <td>{log.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
