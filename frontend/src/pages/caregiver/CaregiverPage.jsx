import { Link } from 'react-router-dom';
import { Card, PageHeader } from '../../components/UI';

export default function CaregiverPage() {
  return (
    <>
      <PageHeader title="Caregiver Mobile View" subtitle="Today’s visits, quick actions, and communication tools." />
      <Card>
        <p><strong>Next Visit:</strong> Jane Doe at 9:00 AM</p>
        <div className="actions mobile-actions">
          <button className="btn">Check-In</button>
          <button className="btn">Add Notes</button>
          <button className="btn">Directions</button>
          <Link className="btn" to="/caregiver/visits/1">Visit Details</Link>
        </div>
      </Card>
    </>
  );
}
