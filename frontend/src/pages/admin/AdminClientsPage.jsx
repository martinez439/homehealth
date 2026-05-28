import { Card, DataTable, PageHeader, StatusPill } from '../../components/UI';

const rows = [
  { id: 1, cells: ['JD', 'Jane Doe', 'Level 2', 'Alex Kim', 'Tomorrow 9:00 AM', <StatusPill status={{ className: 'completed', text: 'Active' }} />] },
  { id: 2, cells: ['MR', 'Michael Roe', 'Level 3', 'Sam Lee', 'Today 4:30 PM', <StatusPill status={{ className: 'progress', text: 'At Risk' }} />] },
];

export default function AdminClientsPage() {
  return (
    <>
      <PageHeader title="Client Database" subtitle="People-first records with quick care actions." />
      <Card>
        <DataTable headers={['Avatar', 'Name', 'Care Level', 'Assigned Caregiver', 'Next Visit', 'Status']} rows={rows} />
      </Card>
    </>
  );
}
