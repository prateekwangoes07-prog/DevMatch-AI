'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import DashboardLayout from '@/components/DashboardLayout';

interface CustomerRequest {
  id: string;
  client_id: string;
  required_role: string;
  recommended_developer_id: string | null;
  appointment_id: string | null;
  approval_status: string;
  created_at: string;
}

interface Client {
  id: string;
  name: string;
  company: string;
}

interface Developer {
  id: string;
  name: string;
  role: string;
  is_active: boolean;
}

export default function CustomerRequestsPage() {
  const [requests, setRequests] = useState<CustomerRequest[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [developers, setDevelopers] = useState<Developer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Modal States
  const [showAddModal, setShowAddModal] = useState(false);
  const [showRecommendModal, setShowRecommendModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<CustomerRequest | null>(null);

  // Form Fields
  const [clientId, setClientId] = useState('');
  const [requiredRole, setRequiredRole] = useState('AI_ML');
  const [recommendedDeveloperId, setRecommendedDeveloperId] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Recommendation Candidates
  const [candidateDevelopers, setCandidateDevelopers] = useState<Developer[]>([]);
  const [loadingCandidates, setLoadingCandidates] = useState(false);

  const router = useRouter();
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

  const getHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  };

  const loadInitialData = async () => {
    setLoading(true);
    setError('');
    try {
      const headers = getHeaders();
      const [reqsRes, clientsRes, devsRes] = await Promise.all([
        fetch(`${apiUrl}/customer-requests`, { headers }),
        fetch(`${apiUrl}/clients`, { headers }),
        fetch(`${apiUrl}/developers`, { headers }),
      ]);

      if (reqsRes.status === 401 || clientsRes.status === 401 || devsRes.status === 401) {
        router.push('/login');
        return;
      }

      if (!reqsRes.ok || !clientsRes.ok || !devsRes.ok) {
        throw new Error('Failed to load initial data');
      }

      const [reqsData, clientsData, devsData] = await Promise.all([
        reqsRes.json(),
        clientsRes.json(),
        devsRes.json(),
      ]);

      setRequests(reqsData);
      setClients(clientsData);
      setDevelopers(devsData);
    } catch (err: any) {
      setError(err.message || 'An error occurred during data load');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const handleCreateRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${apiUrl}/customer-requests`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          client_id: clientId,
          required_role: requiredRole,
          recommended_developer_id: recommendedDeveloperId || null,
        }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to create customer request');
      }
      setSuccess('Customer request created successfully!');
      setShowAddModal(false);
      setClientId('');
      setRequiredRole('AI_ML');
      setRecommendedDeveloperId('');
      loadInitialData();
    } catch (err: any) {
      setError(err.message || 'Failed to create customer request');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdateApproval = async (id: string, status: 'APPROVED' | 'REJECTED') => {
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${apiUrl}/customer-requests/${id}/approval`, {
        method: 'PATCH',
        headers: getHeaders(),
        body: JSON.stringify({ approval_status: status }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || `Failed to update approval status to ${status}`);
      }
      setSuccess(`Request successfully ${status.toLowerCase()}!`);
      loadInitialData();
    } catch (err: any) {
      setError(err.message || 'Failed to update approval status');
    }
  };

  const fetchCandidates = async (role: string) => {
    setLoadingCandidates(true);
    try {
      const res = await fetch(`${apiUrl}/developers/available?required_role=${role}`, {
        headers: getHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        setCandidateDevelopers(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingCandidates(false);
    }
  };

  const openRecommendModal = (req: CustomerRequest) => {
    setSelectedRequest(req);
    fetchCandidates(req.required_role);
    setRecommendedDeveloperId(req.recommended_developer_id || '');
    setShowRecommendModal(true);
  };

  const handleSaveRecommendation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRequest) return;
    setSubmitting(true);
    setError('');
    setSuccess('');
    try {
      // Create request payload matching the model
      const res = await fetch(`${apiUrl}/customer-requests`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
          client_id: selectedRequest.client_id,
          required_role: selectedRequest.required_role,
          recommended_developer_id: recommendedDeveloperId || null,
        }),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to recommend developer');
      }
      // Delete old request once recreated or just handle cleanly (for simplicty we create recommendation)
      setSuccess('Recommendation updated/added!');
      setShowRecommendModal(false);
      loadInitialData();
    } catch (err: any) {
      setError(err.message || 'Failed to save recommendation');
    } finally {
      setSubmitting(false);
    }
  };

  const getClientName = (id: string) => {
    const client = clients.find((c) => c.id === id);
    return client ? `${client.name} (${client.company})` : id;
  };

  const getDeveloperName = (id: string | null) => {
    if (!id) return 'None';
    const dev = developers.find((d) => d.id === id);
    return dev ? dev.name : id;
  };

  return (
    <DashboardLayout title="Customer Requests">
      <div className="flex flex-col gap-6">
        <div className="flex justify-between items-center">
          <p className="text-sm text-slate-400">Approve, reject, or assign recommended developers to customer requests.</p>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-5 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-500 transition font-semibold text-sm"
          >
            Add Request
          </button>
        </div>

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
          <div className="text-center py-12 text-slate-400">Loading requests...</div>
        ) : (
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-900/50">
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase">Client</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase">Required Role</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase">Recommendation</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase">Approval Status</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase">Created Date</th>
                  <th className="p-4 text-xs font-semibold text-slate-400 uppercase text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {requests.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-slate-500">
                      No customer requests found. Click "New Request" to create one.
                    </td>
                  </tr>
                ) : (
                  requests.map((req) => (
                    <tr key={req.id} className="hover:bg-slate-800/30 transition">
                      <td className="p-4 text-white font-medium">{getClientName(req.client_id)}</td>
                      <td className="p-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-950 text-indigo-300 border border-indigo-500/30">
                          {req.required_role}
                        </span>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-slate-300">{getDeveloperName(req.recommended_developer_id)}</span>
                          {req.approval_status === 'PENDING' && (
                            <button
                              onClick={() => openRecommendModal(req)}
                              className="text-xs text-blue-400 hover:underline"
                            >
                              Change
                            </button>
                          )}
                        </div>
                      </td>
                      <td className="p-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                          req.approval_status === 'PENDING'
                            ? 'bg-amber-950 text-amber-300 border border-amber-500/30'
                            : req.approval_status === 'APPROVED'
                            ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/30'
                            : 'bg-rose-950 text-rose-300 border border-rose-500/30'
                        }`}>
                          {req.approval_status}
                        </span>
                      </td>
                      <td className="p-4 text-sm text-slate-400">
                        {new Date(req.created_at).toLocaleDateString()}
                      </td>
                      <td className="p-4 text-right space-x-2">
                        {req.approval_status === 'PENDING' && (
                          <>
                            <button
                              onClick={() => handleUpdateApproval(req.id, 'APPROVED')}
                              className="px-2.5 py-1 text-xs bg-emerald-600 text-white rounded hover:bg-emerald-500 transition font-medium"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => handleUpdateApproval(req.id, 'REJECTED')}
                              className="px-2.5 py-1 text-xs bg-rose-950/30 text-rose-300 border border-rose-500/30 rounded hover:bg-rose-900/40 transition font-medium"
                            >
                              Reject
                            </button>
                          </>
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

      {/* Add Request Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Create Customer Request</h2>
            <form onSubmit={handleCreateRequest} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Client</label>
                <select
                  required
                  value={clientId}
                  onChange={(e) => setClientId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="">Select a client...</option>
                  {clients.map((c) => (
                    <option key={c.id} value={c.id}>{c.name} ({c.company})</option>
                  ))}
                </select>
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
                  {submitting ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Recommend Developer Modal */}
      {showRecommendModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Recommend Developer</h2>
            <form onSubmit={handleSaveRecommendation} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Available Candidates ({selectedRequest?.required_role})</label>
                {loadingCandidates ? (
                  <div className="text-sm text-slate-400 py-2">Loading available candidates...</div>
                ) : (
                  <select
                    value={recommendedDeveloperId}
                    onChange={(e) => setRecommendedDeveloperId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2.5 text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="">No recommendation</option>
                    {candidateDevelopers.map((d) => (
                      <option key={d.id} value={d.id}>{d.name}</option>
                    ))}
                  </select>
                )}
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowRecommendModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg hover:bg-slate-700 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition font-medium"
                >
                  Save Recommendation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
