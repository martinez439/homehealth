import { Link } from 'react-router-dom';
import { Card } from '../../components/UI';
export default function CaregiverPage(){return <Card title="Caregiver Check-in / Check-out"><p>Shift controls and visit list.</p><Link to="/caregiver/visits/1">Open Visit #1</Link></Card>;}
