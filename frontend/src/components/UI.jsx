export function Card({ title, children }) {
  return <section className="card"><h2>{title}</h2>{children}</section>;
}

export function PlaceholderTable({ headers, rows }) {
  return (
    <table>
      <thead><tr>{headers.map((h) => <th key={h}>{h}</th>)}</tr></thead>
      <tbody>{rows.map((r, idx) => <tr key={idx}>{r.map((c, i) => <td key={i}>{c}</td>)}</tr>)}</tbody>
    </table>
  );
}
