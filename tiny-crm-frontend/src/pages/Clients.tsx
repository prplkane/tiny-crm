import { useEffect, useState } from 'react';
import { getClients, deleteClient } from '../api/clients';
import type { Client } from '../api/clients';
import CreateClientForm from '../components/CreateClientForm';


function Clients() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getClients();
        console.log("Fetched clients:", data);
        setClients(data);
      } catch (error) {
        console.error("Error fetching clients:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const handleClientCreated = (newClient: Client) => {
    setClients(prevClients => [...prevClients, newClient])
  }
  if (loading) return <div>Loading...</div>;

   const handleDelete = async (id: number) => {
    try {
      await deleteClient(id);
      setClients(prev => prev.filter(client => client.id !== id));
    } catch (error) {
      console.error("Failed to delete client:", error);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Clients</h2>
      <CreateClientForm onClientCreated={handleClientCreated} existingClients={clients} />
      <ul className="space-y-2">
        {clients.map(client => (
          <li key={client.id} className="bg-white p-4 shadow rounded">
            <div>
              <p><strong>Name:</strong> {client.name}</p>
              <p><strong>Email:</strong> {client.email}</p>
              <p><strong>Created At:</strong> {new Date(client.created_at).toLocaleString()}</p>
            </div>
            <button  onClick={() => handleDelete(client.id)}
              className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Clients;