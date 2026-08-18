'use client';

import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { api } from '@/utils/api';
import { 
  Calendar as CalendarIcon, 
  Plus, 
  X, 
  Clock, 
  AlertTriangle, 
  CheckCircle,
  HelpCircle,
  XCircle
} from 'lucide-react';

interface Client {
  id: string;
  name: string;
  company: string;
  email: string;
  status: string;
}

interface Appointment {
  id: string;
  client_id: string;
  appointment_time: string;
  status: string;
  external_booking_id: string | null;
  created_at: string;
  updated_at: string;
}

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Modal States
  const [showModal, setShowModal] = useState(false);
  const [selectedClientId, setSelectedClientId] = useState('');
  const [availableSlots, setAvailableSlots] = useState<string[]>([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState('');
  const [bookingInProgress, setBookingInProgress] = useState(false);
  
  // Steps in Booking Modal: 1 = Client Selection, 2 = Slot Selection
  const [bookingStep, setBookingStep] = useState(1);

  const selectedClient = clients.find(c => c.id === selectedClientId);
  const isClientInactive = selectedClient?.status === 'inactive';

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const [apptsData, clientsData] = await Promise.all([
        api.get('/appointments'),
        api.get('/clients'),
      ]);
      setAppointments(apptsData);
      setClients(clientsData);
    } catch (err: any) {
      setError(err.message || 'An error occurred while retrieving data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpenBookingModal = () => {
    setSelectedClientId('');
    setAvailableSlots([]);
    setSelectedSlot('');
    setBookingStep(1);
    setShowModal(true);
  };

  const handleClientSelectedNext = async () => {
    if (!selectedClientId || isClientInactive) return;
    
    setLoadingSlots(true);
    setBookingStep(2);
    try {
      // Query availability for the next 7 days
      const slots = await api.get('/appointments/availability');
      setAvailableSlots(slots);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch slot availability');
    } finally {
      setLoadingSlots(false);
    }
  };

  const handleBookAppointment = async () => {
    if (!selectedClientId || !selectedSlot) return;
    setBookingInProgress(true);
    setError('');
    setSuccess('');
    try {
      await api.post('/appointments/book', {
        client_id: selectedClientId,
        appointment_time: selectedSlot
      });
      setSuccess('Appointment successfully scheduled and synchronized with Cal.com!');
      setShowModal(false);
      fetchData();
    } catch (err: any) {
      setError(err.message || 'Booking process failed');
    } finally {
      setBookingInProgress(false);
    }
  };

  const handleCancelAppointment = async (apptId: string) => {
    if (!confirm('Are you sure you want to cancel this appointment?')) return;
    setError('');
    setSuccess('');
    try {
      await api.post(`/appointments/${apptId}/cancel`);
      setSuccess('Appointment cancelled successfully.');
      fetchData();
    } catch (err: any) {
      setError(err.message || 'Failed to cancel appointment');
    }
  };

  const getClientDisplay = (clientId: string) => {
    const client = clients.find(c => c.id === clientId);
    if (!client) return 'Unknown Client';
    return `${client.name} (${client.company})`;
  };

  const formatDateTime = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
    } catch {
      return isoString;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'scheduled':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle className="w-3 h-3" /> Scheduled
          </span>
        );
      case 'cancelled':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20">
            <XCircle className="w-3 h-3" /> Cancelled
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/20">
            <HelpCircle className="w-3 h-3" /> {status}
          </span>
        );
    }
  };

  return (
    <DashboardLayout title="Appointments">
      <div className="flex flex-col gap-6">
        {/* Header Action */}
        <div className="flex justify-between items-center">
          <p className="text-sm text-slate-400">
            Schedule kick-off calls, follow-ups, and review booking slots with active clients.
          </p>
          <button
            onClick={handleOpenBookingModal}
            className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Schedule Appointment
          </button>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-400">
            {error}
          </div>
        )}

        {success && (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-sm text-emerald-400">
            {success}
          </div>
        )}

        {/* List of Appointments */}
        <div className="glassmorphism rounded-2xl border border-white/5 overflow-hidden shadow-xl">
          {loading ? (
            <div className="py-12 flex justify-center text-slate-400 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                Loading Appointments...
              </div>
            </div>
          ) : appointments.length === 0 ? (
            <div className="py-16 text-center text-slate-400">
              <CalendarIcon className="w-12 h-12 mx-auto mb-3 opacity-20" />
              <p className="text-sm font-medium">No appointments scheduled yet</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-white/5 bg-white/[0.02] text-xs font-bold uppercase tracking-wider text-slate-400">
                    <th className="px-6 py-4">Client</th>
                    <th className="px-6 py-4">Appointment Time</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4">Cal.com Booking ID</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-sm text-slate-300">
                  {appointments.map((appt) => (
                    <tr key={appt.id} className="hover:bg-white/[0.01] transition-colors">
                      <td className="px-6 py-4 font-semibold text-white">
                        {getClientDisplay(appt.client_id)}
                      </td>
                      <td className="px-6 py-4 flex items-center gap-2">
                        <Clock className="w-4 h-4 text-slate-500" />
                        {formatDateTime(appt.appointment_time)}
                      </td>
                      <td className="px-6 py-4">
                        {getStatusBadge(appt.status)}
                      </td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-400">
                        {appt.external_booking_id || 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        {appt.status.toLowerCase() === 'scheduled' && (
                          <button
                            onClick={() => handleCancelAppointment(appt.id)}
                            className="text-xs font-bold text-red-400 hover:text-red-300 transition-colors"
                          >
                            Cancel
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

        {/* Booking Form Modal */}
        {showModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setShowModal(false)} />
            
            <div className="relative w-full max-w-md bg-[#0c101f] border border-white/10 rounded-2xl p-6 shadow-2xl z-10">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-bold text-white">
                  Schedule New Kick-Off Call
                </h3>
                <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white">
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* STEP 1: Select Client */}
              {bookingStep === 1 && (
                <div className="flex flex-col gap-5">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                      Select Client
                    </label>
                    <select
                      value={selectedClientId}
                      onChange={(e) => setSelectedClientId(e.target.value)}
                      className="w-full px-4 py-3 rounded-xl bg-slate-900/60 border border-slate-800 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition text-sm"
                    >
                      <option value="">-- Choose a Client --</option>
                      {clients.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.name} ({c.company}) {c.status === 'inactive' ? '[INACTIVE]' : ''}
                        </option>
                      ))}
                    </select>
                  </div>

                  {isClientInactive && (
                    <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-xs text-red-400 flex items-start gap-2.5">
                      <AlertTriangle className="w-4 h-4 shrink-0 text-red-400" />
                      <div>
                        <span className="font-bold">Booking Blocked: </span>
                        This client is inactive. Inactive clients cannot schedule new appointments.
                      </div>
                    </div>
                  )}

                  <div className="flex justify-end gap-3 mt-2">
                    <button
                      type="button"
                      onClick={() => setShowModal(false)}
                      className="px-4 py-2.5 rounded-xl border border-white/5 text-sm font-semibold text-slate-400 hover:bg-white/5 transition"
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      disabled={!selectedClientId || isClientInactive}
                      onClick={handleClientSelectedNext}
                      className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </div>
                </div>
              )}

              {/* STEP 2: Select Time Slot */}
              {bookingStep === 2 && (
                <div className="flex flex-col gap-5">
                  <div>
                    <span className="text-xs font-bold text-slate-400 block mb-1">CLIENT</span>
                    <span className="text-sm font-semibold text-white">{selectedClient?.name}</span>
                  </div>

                  <div>
                    <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                      Available Cal.com Slots
                    </label>

                    {loadingSlots ? (
                      <div className="py-8 flex justify-center text-slate-400 text-xs">
                        <div className="flex items-center gap-2">
                          <div className="w-3.5 h-3.5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                          Retrieving availability...
                        </div>
                      </div>
                    ) : availableSlots.length === 0 ? (
                      <p className="text-xs text-slate-400 italic py-2">No slots available for the upcoming week.</p>
                    ) : (
                      <div className="max-h-60 overflow-y-auto border border-white/5 rounded-xl divide-y divide-white/5">
                        {availableSlots.map((slot) => (
                          <button
                            key={slot}
                            type="button"
                            onClick={() => setSelectedSlot(slot)}
                            className={`w-full px-4 py-3 text-left text-xs font-medium transition ${
                              selectedSlot === slot 
                                ? 'bg-blue-600/20 text-blue-400 font-bold' 
                                : 'text-slate-300 hover:bg-white/5'
                            }`}
                          >
                            {formatDateTime(slot)}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="flex justify-between items-center mt-2">
                    <button
                      type="button"
                      onClick={() => setBookingStep(1)}
                      className="text-xs font-bold text-slate-400 hover:text-white transition"
                    >
                      Back
                    </button>
                    <div className="flex gap-3">
                      <button
                        type="button"
                        onClick={() => setShowModal(false)}
                        className="px-4 py-2.5 rounded-xl border border-white/5 text-sm font-semibold text-slate-400 hover:bg-white/5 transition"
                      >
                        Cancel
                      </button>
                      <button
                        type="button"
                        disabled={!selectedSlot || bookingInProgress}
                        onClick={handleBookAppointment}
                        className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                      >
                        {bookingInProgress ? 'Booking...' : 'Confirm Book'}
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
