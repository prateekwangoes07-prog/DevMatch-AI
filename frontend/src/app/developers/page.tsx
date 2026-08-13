'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface Developer {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  role: string;
  is_active: boolean;
  active_project_count: number;
}

export default function DevelopersPage() {
  const [developers, setDevelopers] = useState<Developer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Modal States
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedDeveloper, setSelectedDeveloper] = useState<Developer | null>(null);

  // Form Fields
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [role, setRole] = useState('AI_ML');
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

  const fetchDevelopers = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${apiUrl}/developers`, {
        headers: getHeaders(),
      });
      if (res.status === 401 || res.status === 403) {
        router.push('/login');
        return;
      }
      if (!res.ok) {
        throw new Error('Failed to retrieve developers');
      }
      const data = await res.json();
      setDevelopers(data);
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    } else {
      fetchDevelopers();
    }
  }, []);

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${apiUrl}/developers`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ name, email, phone: phone || null, role }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to create developer');
      }
      setSuccess('Developer added successfully!');
      setShowAddModal(false);
      setName('');
      setEmail('');
      setPhone('');
      setRole('AI_ML');
      fetchDevelopers();
    } catch (err: any) {
      setError(err.message || 'Failed to create developer');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDeveloper) return;
    setSubmitting(true);
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${apiUrl}/developers/${selectedDeveloper.id}`, {
        method: 'PATCH',
        headers: getHeaders(),
        body: JSON.stringify({ name, email, phone: phone || null, role }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to update developer');
      }
      setSuccess('Developer updated successfully!');
      setShowEditModal(false);
      setSelectedDeveloper(null);
      setName('');
      setEmail('');
      setPhone('');
      fetchDevelopers();
    } catch (err: any) {
      setError(err.message || 'Failed to update developer');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeactivate = async (id: string) => {
    if (!confirm('Are you sure you want to deactivate this developer?')) return;
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${apiUrl}/developers/${id}`, {
        method: 'DELETE',
        headers: getHeaders(),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to deactivate developer');
      }
      setSuccess('Developer deactivated successfully!');
      fetchDevelopers();
    } catch (err: any) {
      setError(err.message || 'Failed to deactivate developer');
    }
  };

  const openEditModal = (dev: Developer) => {
    setSelectedDeveloper(dev);
    setName(dev.name);
    setEmail(dev.email);
    setPhone(dev.phone || '');
    setRole(dev.role);
    setShowEditModal(true);
  };

  const logout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  return (
    <main className="min-h-screen bg-[#0b0f19] text-white p-8 relative overflow-hidden">
      {/* Glow Effects */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-blue-500/5 blur-[120px]" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] rounded-full bg-indigo-500/5 blur-[120px]" />

      <div className="max-w-6xl mx-auto z-10 relative">
        <header className="flex justify-between items-center mb-10 pb-6 border-b border-slate-800">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white mb-1">
              Developer Management
            </h1>
            <p className="text-sm text-slate-400">
              Manage IT company engineers and roles
            </p>
          </div>
          <div className="flex space-x-4">
            <button
              onClick={() => setShowAddModal(true)}
              className="px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 font-medium text-sm transition duration-200"
            >
              Add Developer
            </button>
            <button
              onClick={logout}
              className="px-5 py-2.5 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 font-medium text-sm transition duration-200"
            >
              Log Out
            </button>
          </div>
        </header>

        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-sm text-emerald-400">
            {success}
          </div>
        )}

        {loading ? (
          <div className="text-center py-20 text-slate-400">
            <p className="animate-pulse">Loading engineers...</p>
          </div>
        ) : developers.length === 0 ? (
          <div className="text-center py-20 rounded-2xl border border-dashed border-slate-800 bg-slate-950/20">
            <p className="text-slate-500 text-sm mb-4">No developers registered yet</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-xs font-semibold text-white transition duration-200"
            >
              Register your first developer
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/40 backdrop-blur-md">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-900/50 text-slate-400 text-xs uppercase tracking-wider font-semibold">
                  <th className="px-6 py-4">Developer</th>
                  <th className="px-6 py-4">Role</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Active Projects</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {developers.map((dev) => (
                  <tr key={dev.id} className="hover:bg-slate-900/30 transition">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-white">{dev.name}</div>
                      <div className="text-xs text-slate-500">{dev.email}</div>
                      {dev.phone && <div className="text-xs text-slate-500 mt-0.5">{dev.phone}</div>}
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-300">
                        {dev.role}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {dev.is_active ? (
                        <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          Active
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-500">
                          Inactive
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-semibold text-slate-300">
                        {dev.active_project_count}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <button
                        onClick={() => openEditModal(dev)}
                        className="px-3 py-1.5 rounded bg-slate-900 border border-slate-800 hover:bg-slate-800 text-xs font-medium transition duration-200"
                      >
                        Edit
                      </button>
                      {dev.is_active && (
                        <button
                          onClick={() => handleDeactivate(dev.id)}
                          className="px-3 py-1.5 rounded bg-red-650/10 hover:bg-red-650/20 text-red-400 border border-red-500/10 text-xs font-medium transition duration-200"
                        >
                          Deactivate
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-md p-8 rounded-2xl bg-slate-900 border border-slate-800">
            <h2 className="text-xl font-bold mb-6 text-white">Add Developer</h2>
            <form onSubmit={handleAddSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-2.5 rounded bg-slate-950 border border-slate-800 focus:outline-none focus:border-blue-500 text-white text-sm"
                  placeholder="Alice Smith"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Email</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-2.5 rounded bg-slate-950 border border-slate-800 focus:outline-none focus:border-blue-500 text-white text-sm"
                  placeholder="alice@company.com"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Phone</label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full px-4 py-2.5 rounded bg-slate-950 border border-slate-800 focus:outline-none focus:border-blue-500 text-white text-sm"
                  placeholder="+1 (555) 0199"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-4 py-2.5 rounded bg-slate-950 border border-slate-800 focus:outline-none focus:border-blue-500 text-white text-sm"
                >
                  <option value="AI_ML">AI_ML</option>
                  <option value="AUTOMATION">AUTOMATION</option>
                  <option value="DEVOPS">DEVOPS</option>
                </select>
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded bg-slate-800 hover:bg-slate-750 text-slate-300 text-sm font-medium transition duration-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition duration-200"
                >
                  {submitting ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-md p-8 rounded-2xl bg-slate-900 border border-slate-800">
            <h2 className="text-xl font-bold mb-6 text-white">Edit Developer</h2>
            <form onSubmit={handleEditSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-2.5 rounded bg-slate-950 border border-slate-800 focus:outline-none focus:border-blue-500 text-white text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Email</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-2.5 rounded bg-slate-950 border border-slate-800 focus:outline-none focus:border-blue-500 text-white text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Phone</label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full px-4 py-2.5 rounded bg-slate-950 border border-slate-800 focus:outline-none focus:border-blue-500 text-white text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-4 py-2.5 rounded bg-slate-950 border border-slate-800 focus:outline-none focus:border-blue-500 text-white text-sm"
                >
                  <option value="AI_ML">AI_ML</option>
                  <option value="AUTOMATION">AUTOMATION</option>
                  <option value="DEVOPS">DEVOPS</option>
                </select>
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="px-4 py-2 rounded bg-slate-800 hover:bg-slate-750 text-slate-300 text-sm font-medium transition duration-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition duration-200"
                >
                  {submitting ? 'Saving...' : 'Save'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}
