import api from './axios';

export interface Client {
    id: number;
    name: string;
    email: string;
    phone: string;
    address: string;
    created_at: string;
}

export async function getClients(): Promise<Client[]> {
    const response = await api.get<Client[]>('/clients/');
    return response.data;
}

export async function deleteClient(id: number): Promise<void> {
    await api.delete(`/clients/${id}/`);
}