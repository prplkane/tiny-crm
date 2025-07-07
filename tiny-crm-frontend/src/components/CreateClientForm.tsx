// src/components/CreateClientForm.tsx

import { useState } from 'react';
import type { Client } from '../api/clients';
import api from '../api/axios';

interface Props {
  onClientCreated: (client: Client) => void;
  existingClients: Client[]
}

function CreateClientForm({ onClientCreated, existingClients }: Props) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!name.trim() || !email.trim()) {
      setError('Name and Email are required.');
      return;
    }

    const isDuplicate = existingClients.some(
      client => client.name.toLowerCase() === name.toLowerCase() || client.email.toLowerCase() === email.toLowerCase()
    )

    if (isDuplicate) {
      setError('Client with this name or email already exists.');
      return;
    }

    try {
      const response = await api.post<Client>('/clients/', { name, email, phone, address });
      onClientCreated(response.data);
      setName('');
      setEmail('');
      setPhone('');
      setAddress('');
    } catch (err) {
      setError('Failed to create client.');
      console.error(err);
    }
  };

  return (
   <form onSubmit={handleSubmit} className="mb-6 bg-white p-4 rounded shadow space-y-4">
  <h3 className="text-lg font-semibold">Add New Client</h3>
  {error && <p className="text-red-600">{error}</p>}
  <div>
    <label className="block text-sm font-medium">Name</label>
    <input
      type="text"
      className="border p-2 rounded w-full"
      value={name}
      onChange={(e) => setName(e.target.value)}
      placeholder="Client Name"
    />
  </div>
  <div>
    <label className="block text-sm font-medium">Email</label>
    <input
      type="email"
      className="border p-2 rounded w-full"
      value={email}
      onChange={(e) => setEmail(e.target.value)}
      placeholder="client@example.com"
    />
  </div>
  {/* Add phone input */}
  <div>
    <label className="block text-sm font-medium">Phone</label>
    <input
      type="text"
      className="border p-2 rounded w-full"
      value={phone}
      onChange={(e) => setPhone(e.target.value)}
      placeholder="Phone Number"
    />
  </div>
  {/* Add address input */}
  <div>
    <label className="block text-sm font-medium">Address</label>
    <input
      type="text"
      className="border p-2 rounded w-full"
      value={address}
      onChange={(e) => setAddress(e.target.value)}
      placeholder="Address"
    />
  </div>
  <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
    Create Client
  </button>
</form>
  );
}

export default CreateClientForm;
