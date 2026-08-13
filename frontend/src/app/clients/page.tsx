'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface Client {
  id: string;
  name: string;
  company: string;
  email: string;
  phone: string | null;
  requirement: string | null;
  required_role: string;
  status: string;
}

export default function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Modal States
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);

  // Form Fields
  const [name, setName] = useState('');
  const [company, setCompany] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [requirement, setRequirement] = useState('');
  const [requiredRole, setRequiredRole] = useState('AI_ML');
  const [submitting, setSubmitting] = useState(false);

  const router = useRouter();
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

  const getHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  };

  const fetchClients = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${apiUrl}/clients`, {
        headers: getHeaders(),
      });
      if (res.status === 401 || res.status === 403) {
        router.push('/login');
        return;
      }
      if (!res.ok) {
        throw new Error('Failed to load clients');
      }
      const data = await res.json();
      setClients(data);
    } catch (err: any) {
      setError(err.message || 'An error occurred while fetching clients');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClients();
  }, []);

  const handleAddClient = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${apiUrl}/clients`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          name,
          company,
          email,
          phone: phone || null,
          requirement: requirement || null,
          required_role: requiredRole,
        }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to create client');
      }
      setSuccess('Client added successfully!');
      setName('');
      setCompany('');
      setEmail('');
      setPhone('');
      setRequirement('');
      setRequiredRole('AI_ML');
      setShowAddModal(false);
      fetchClients();
    } catch (err: any) {
      setError(err.message || 'Failed to add client');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditClient = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedClient) return;
    setSubmitting(true);
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${apiUrl}/clients/${selectedClient.id}`, {
        method: 'PATCH',
        headers: getHeaders(),
        body: JSON.stringify({
          name,
          company,
          email,
          phone: phone || null,
          requirement: requirement || null,
          required_role: requiredRole,
        }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to update client');
      }
      setSuccess('Client updated successfully!');
      setShowEditModal(false);
      setSelectedClient(null);
      fetchClients();
    } catch (err: any) {
      setError(err.message || 'Failed to update client');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeactivate = async (id: string) => {
    if (!confirm('Are you sure you want to deactivate this client?')) return;
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${apiUrl}/clients/${id}`, {
        method: 'DELETE',
        headers: getHeaders(),
      });
      if (!res.ok) {
        throw new Error('Failed to deactivate client');
      }
      setSuccess('Client deactivated successfully.');
      fetchClients();
    } catch (err: any) {
      setError(err.message || 'Failed to deactivate client');
    }
  };

  const openEditModal = (client: Client) => {
    setSelectedClient(client);
    setName(client.name);
    setCompany(client.company);
    setEmail(client.email);
    setPhone(client.phone || '');
    setRequirement(client.requirement || '');
    setRequiredRole(client.required_role);
    setShowEditModal(true);
  };

  const openAddModal = () => {
    setName('');
    setCompany('');
    setEmail('');
    setPhone('');
    setRequirement('');
    setRequiredRole('AI_ML');
    setShowAddModal(true);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">Client Management</h1>
            <p className="text-slate-400 mt-2">Manage clients, their resource requirements, and status.</p>
          </div>
          <div className="flex gap-4">
            <Link href="/developers" className="px-4 py-2 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition">
              Developers
            </Link>
            <Link href="/customer-requests" className="px-4 py-2 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition">
              Customer Requests
            </Link>
            <button
              onClick={openAddModal}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition font-medium"
            >
              Add Client
            </button>
          </div>
        </header>

        {error && (
          <div className="mb-6 p-4 bg-red-950/50 border border-red-500/50 text-red-200 rounded-lg text-sm">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-6 p-4 bg-emerald-950/50 border border-emerald-500/50 text-emerald-200 rounded-lg text-sm">
            {success}
          </div>
        )}

        {loading ? (
          <div className="text-center py-12 text-slate-400">Loading clients...</div>
        ) : (
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-900/50">
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase">Client Info</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase">Company</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase">Required Role</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase">Status</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {clients.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-slate-500">
                      No clients found. Click "Add Client" to get started.
                    </td>
                  </tr>
                ) : (
                  clients.map((client) => (
                    <tr key={client.id} className="hover:bg-slate-800/30 transition">
                      <td className="p-4">
                        <div className="font-semibold text-white">{client.name}</div>
                        <div className="text-sm text-slate-400">{client.email}</div>
                        {client.phone && <div className="text-xs text-slate-500">{client.phone}</div>}
                      </td>
                      <td className="p-4 text-slate-300 font-medium">{client.company}</td>
                      <td className="p-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-950 text-indigo-300 border border-indigo-500/30">
                          {client.required_role}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                          client.status === 'active' 
                            ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/30' 
                            : 'bg-rose-950 text-rose-300 border border-rose-500/30'
                        }`}>
                          {client.status}
                        </span>
                      </td>
                      <td className="p-4 text-right space-x-2">
                        <button
                          onClick={() => openEditModal(client)}
                          className="px-3 py-1 text-sm bg-slate-800 text-slate-200 rounded hover:bg-slate-700 transition"
                        >
                          Edit
                        </button>
                        {client.status === 'active' && (
                          <button
                            onClick={() => handleDeactivate(client.id)}
                            className="px-3 py-1 text-sm bg-rose-950/30 text-rose-300 border border-rose-500/30 rounded hover:bg-rose-900/40 transition"
                          >
                            Deactivate
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Client Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Add New Client</h2>
            <form onSubmit={handleAddClient} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Company</label>
                <input
                  type="text"
                  required
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Phone (Optional)</label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Requirement (Optional)</label>
                <textarea
                  value={requirement}
                  onChange={(e) => setRequirement(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2.5 text-white h-20 resize-none focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Required Role</label>
                <select
                  value={requiredRole}
                  onChange={(e) => setRequiredRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="AI_ML">AI / ML</option>
                  <option value="AUTOMATION">Automation</option>
                  <option value="DEVOPS">DevOps</option>
                </select>
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg hover:bg-slate-700 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition font-medium"
                >
                  {submitting ? 'Adding...' : 'Add Client'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Client Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Edit Client</h2>
            <form onSubmit={handleEditClient} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Company</label>
                <input
                  type="text"
                  required
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Phone (Optional)</label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Requirement (Optional)</label>
                <textarea
                  value={requirement}
                  onChange={(e) => setRequirement(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2.5 text-white h-20 resize-none focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Required Role</label>
                <select
                  value={requiredRole}
                  onChange={(e) => setRequiredRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="AI_ML">AI / ML</option>
                  <option value="AUTOMATION">Automation</option>
                  <option value="DEVOPS">DevOps</option>
                </select>
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg hover:bg-slate-700 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition font-medium"
                >
                  {submitting ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
