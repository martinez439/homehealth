export function PageHeader({ title, subtitle }) {
  return (
    <header>
      <h1 className="page-title">{title}</h1>
      {subtitle && <p className="page-subtitle">{subtitle}</p>}
    </header>
  );
}

export function Card({ title, children, warm = false }) {
  return (
    <section className={`card ${warm ? 'warm' : ''}`}>
      {title && <h2>{title}</h2>}
      {children}
    </section>
  );
}

export function StatCard({ label, value, status }) {
  return (
    <article className="card warm">
      <div className="label">{label}</div>
      <div className="stat-value">{value}</div>
      {status && <span className={`pill ${status.className}`}>{status.text}</span>}
    </article>
  );
}

export function DataTable({ headers, rows }) {
  return (
    <div className="table-wrap">
      <div className="table-row table-head">{headers.map((h) => <div key={h}>{h}</div>)}</div>
      {rows.map((r) => <div className="table-row" key={r.id}>{r.cells.map((c, i) => <div key={i}>{c}</div>)}</div>)}
    </div>
  );
}

export const StatusPill = ({ status }) => <span className={`pill ${status.className}`}>{status.text}</span>;
