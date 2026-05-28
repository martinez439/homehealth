import { useParams } from 'react-router-dom';
import { Card } from '../../components/UI';
export default function VisitDetailsPage(){const {id}=useParams();return <Card title={`Visit Notes - #${id}`}><textarea placeholder="Enter visit notes"/><button>Save Note</button></Card>;}
