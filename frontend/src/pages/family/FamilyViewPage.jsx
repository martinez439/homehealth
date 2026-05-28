import { useParams } from 'react-router-dom';
import { Card, PageHeader, StatusPill } from '../../components/UI';

export default function FamilyViewPage() {
  const { clientId } = useParams();
  return (
    <>
      <PageHeader title={`Family Portal • Client #${clientId}`} subtitle="Reassuring updates and transparent daily care progress." />
      <Card warm>
        <p><strong>Upcoming Visit:</strong> Tomorrow at 9:00 AM with Alex Kim</p>
        <p><strong>Latest Summary:</strong> Nutrition goals met, medication reminder completed, mood positive.</p>
        <StatusPill status={{ className: 'completed', text: 'Last visit completed' }} />
      </Card>
    </>
  );
}
