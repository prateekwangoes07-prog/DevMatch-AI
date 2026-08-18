'use client';

import React, { useEffect, useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { api } from '@/utils/api';
import { 
  Users, 
  Briefcase, 
  Calendar, 
  ClipboardCheck, 
  Plus, 
  ArrowRight,
  Clock
} from 'lucide-react';
import Link from 'next/link';

interface Stats {
  developersCount: number;
  clientsCount: number;
  appointmentsCount: number;
  requestsCount: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats>({
    developersCount: 0,
    clientsCount: 0,
    appointmentsCount: 0,
    requestsCount: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const [devs, clients, appts, requests] = await Promise.all([
          api.get('/developers').catch(() => []),
          api.get('/clients').catch(() => []),
          api.get('/appointments').catch(() => []),
          api.get('/customer-requests').catch(() => []),
        ]);

        setStats({
          developersCount: devs.length,
          clientsCount: clients.length,
          appointmentsCount: appts.length,
          requestsCount: requests.length,
        });
      } catch (err: any) {
        setError(err.message || 'Failed to load system metrics');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const statCards = [
    {
      name: 'Total Developers',
      value: stats.developersCount,
      icon: Users,
      color: 'from-blue-600 to-cyan-500',
      shadow: 'shadow-blue-500/10',
      href: '/developers',
    },
    {
      name: 'Managed Clients',
      value: stats.clientsCount,
      icon: Briefcase,
      color: 'from-indigo-600 to-purple-500',
      shadow: 'shadow-indigo-500/10',
      href: '/clients',
    },
    {
      name: 'Customer Requests',
      value: stats.requestsCount,
      icon: ClipboardCheck,
      color: 'from-amber-600 to-orange-500',
      shadow: 'shadow-amber-500/10',
      href: '/customer-requests',
    },
    {
      name: 'Scheduled Appointments',
      value: stats.appointmentsCount,
      icon: Calendar,
      color: 'from-emerald-600 to-teal-500',
      shadow: 'shadow-emerald-500/10',
      href: '/appointments',
    },
  ];

  return (
    <DashboardLayout title="Overview Dashboard">
      <div className="flex flex-col gap-8">
        {/* Welcome section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white/5 border border-white/5 p-6 rounded-2xl">
          <div>
            <h2 className="text-2xl font-bold text-white mb-1">Welcome back, Admin</h2>
            <p className="text-sm text-slate-400">
              Manage developer allocation limits, clients, and Cal.com meeting requests.
            </p>
          </div>
          <div className="flex gap-3">
            <Link 
              href="/appointments" 
              className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2.5 rounded-xl text-sm font-semibold transition flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Book Appointment
            </Link>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-sm text-rose-400">
            {error}
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((card) => {
            const Icon = card.icon;
            return (
              <Link 
                key={card.name} 
                href={card.href}
                className="group relative glassmorphism p-6 rounded-2xl border border-white/5 hover:border-white/10 transition-all duration-300 flex flex-col gap-4 shadow-xl"
              >
                <div className="flex justify-between items-start">
                  <div className={`p-3 rounded-xl bg-gradient-to-tr ${card.color} text-white shadow-lg ${card.shadow}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-3xl font-extrabold text-white tracking-tight group-hover:scale-105 transition-transform duration-200">
                    {loading ? '...' : card.value}
                  </span>
                </div>
                <div className="flex justify-between items-end mt-2">
                  <span className="text-sm font-bold text-slate-400 uppercase tracking-wider">{card.name}</span>
                  <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-white transition-colors duration-200" />
                </div>
              </Link>
            );
          })}
        </div>

        {/* Activity & Quick Actions */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Operations Card */}
          <div className="lg:col-span-2 glassmorphism border border-white/5 p-6 rounded-2xl flex flex-col gap-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-400" />
              Quick Operations Guide
            </h3>
            <div className="border-t border-white/5 pt-4 space-y-4 text-slate-300 text-sm">
              <div className="flex gap-4">
                <span className="w-6 h-6 rounded-full bg-blue-500/10 text-blue-400 flex items-center justify-center font-bold shrink-0">1</span>
                <div>
                  <h4 className="font-semibold text-white mb-1">Verify Developer Allocation Limits</h4>
                  <p className="text-xs text-slate-400">Developers can have a maximum of 2 active clients. Use the Developers tab to monitor their availability status.</p>
                </div>
              </div>
              <div className="flex gap-4">
                <span className="w-6 h-6 rounded-full bg-blue-500/10 text-blue-400 flex items-center justify-center font-bold shrink-0">2</span>
                <div>
                  <h4 className="font-semibold text-white mb-1">Client Verification & Deactivation</h4>
                  <p className="text-xs text-slate-400">Inactive clients are restricted from booking new appointments, matching developers, or submitting requests. Manage client statuses via the Clients panel.</p>
                </div>
              </div>
              <div className="flex gap-4">
                <span className="w-6 h-6 rounded-full bg-blue-500/10 text-blue-400 flex items-center justify-center font-bold shrink-0">3</span>
                <div>
                  <h4 className="font-semibold text-white mb-1">Secure Appointment Scheduling</h4>
                  <p className="text-xs text-slate-400">Cal.com is fully integrated at `/appointments` to handle scheduling without exposing private credentials to the browser.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Stats Summary */}
          <div className="glassmorphism border border-white/5 p-6 rounded-2xl flex flex-col justify-between gap-6">
            <div>
              <h3 className="text-lg font-bold text-white mb-2">Integration Health</h3>
              <p className="text-xs text-slate-400 mb-4">Current integration configurations and status indicators.</p>
              <div className="space-y-3">
                <div className="flex justify-between items-center text-sm py-2 border-b border-white/5">
                  <span className="text-slate-400">Cal.com Adapter</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Active</span>
                </div>
                <div className="flex justify-between items-center text-sm py-2 border-b border-white/5">
                  <span className="text-slate-400">Database Engine</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">PostgreSQL</span>
                </div>
                <div className="flex justify-between items-center text-sm py-2">
                  <span className="text-slate-400">Token Access</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">JWT</span>
                </div>
              </div>
            </div>
            <div className="text-slate-500 text-[10px] uppercase font-bold tracking-wider text-center">
              DevMatch AI Platform
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
