import { useParams } from 'react-router-dom';
import { Card } from '../../components/UI';
export default function FamilyViewPage(){const {clientId}=useParams();return <Card title={`Family Updates: Client #${clientId}`}><p>Recent visit summaries and caregiver updates.</p></Card>;}
