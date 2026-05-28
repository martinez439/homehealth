import { Card, DataTable, PageHeader, StatusPill } from '../../components/UI';

const rows = [
  { id: 1, cells: ['AK', 'Alex Kim', 'RN', 'Weekdays', '11 Visits', <StatusPill status={{ className: 'completed', text: 'On Shift' }} />] },
  { id: 2, cells: ['SL', 'Sam Lee', 'CNA', 'Nights', '6 Visits', <StatusPill status={{ className: 'scheduled', text: 'Scheduled' }} />] },
];

export default function AdminCaregiversPage() {
  return (
    <>
      <PageHeader title="Caregiver Database" subtitle="Track caregiver readiness, workload, and assignment quality." />
      <Card>
        <DataTable headers={['Avatar', 'Name', 'Certification', 'Availability', 'Today', 'Status']} rows={rows} />
      </Card>
    </>
  );
}
