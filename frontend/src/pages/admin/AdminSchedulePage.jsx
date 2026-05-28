import { Card, PageHeader, StatusPill } from '../../components/UI';

const visits = [
  ['9:00 AM', 'Jane Doe', 'Alex Kim', { className: 'scheduled', text: 'Scheduled' }],
  ['12:30 PM', 'Michael Roe', 'Sam Lee', { className: 'progress', text: 'In Progress' }],
  ['3:00 PM', 'Ava Patel', 'Jordan Yu', { className: 'completed', text: 'Completed' }],
];

export default function AdminSchedulePage() {
  return (
    <>
      <PageHeader title="Scheduling Calendar" subtitle="A soft, glanceable timeline for visits and staffing." />
      <Card title="Today’s Visit Timeline" warm>
        <div className="table-wrap">
          {visits.map(([time, client, caregiver, status]) => (
            <div className="table-row" key={`${time}-${client}`}>
              <div><strong>{time}</strong></div>
              <div>{client}</div>
              <div>{caregiver}</div>
              <div><StatusPill status={status} /></div>
            </div>
          ))}
        </div>
      </Card>
    </>
  );
}
