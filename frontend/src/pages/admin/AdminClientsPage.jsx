import { Card, PlaceholderTable } from '../../components/UI';
export default function AdminClientsPage(){return <Card title="Client Database"><PlaceholderTable headers={['Name','Status','Primary Caregiver']} rows={[['Jane Doe','Active','Alex'],['John Roe','Pending','Unassigned']]}/></Card>;}
