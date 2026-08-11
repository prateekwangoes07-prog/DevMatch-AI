"use client";

import React, { useState } from "react";
import { 
  Cpu, 
  Users, 
  Calendar, 
  CheckCircle, 
  Clock, 
  ShieldCheck, 
  ArrowRight,
  Database,
  Layers,
  ChevronRight,
  Smartphone,
  Check,
  AlertCircle
} from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState("matching");

  return (
    <div className="min-h-screen bg-[#070a13] text-slate-100 flex flex-col selection:bg-brand-500 selection:text-white">
      {/* Decorative Blur Background Elements */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-brand-500/10 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="absolute top-1/3 right-1/4 w-[400px] h-[400px] bg-blue-500/10 rounded-full blur-[100px] pointer-events-none -z-10" />

      {/* Header */}
      <header className="sticky top-0 z-50 glassmorphism border-b border-white/5 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-tr from-brand-600 to-blue-400 p-2.5 rounded-xl shadow-lg shadow-brand-500/20">
              <Cpu className="w-6 h-6 text-white animate-pulse" />
            </div>
            <div>
              <span className="font-extrabold text-2xl tracking-tight text-gradient">DevMatch AI</span>
              <p className="text-[10px] text-slate-400 font-semibold tracking-wider uppercase">Phase 1 Foundation</p>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
            <a href="#features" className="hover:text-white transition-colors duration-200">System Core</a>
            <a href="#flow" className="hover:text-white transition-colors duration-200">Allocation Flow</a>
            <a href="#rules" className="hover:text-white transition-colors duration-200">System Rules</a>
          </nav>
          <div className="flex items-center gap-4">
            <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              API Ready
            </span>
            <button className="bg-brand-600 hover:bg-brand-500 hover:shadow-lg hover:shadow-brand-500/30 text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 flex items-center gap-2">
              Launch Dashboard
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-12 md:py-24 flex flex-col gap-16">
        <section className="grid lg:grid-cols-12 gap-12 items-center">
          <div className="lg:col-span-7 flex flex-col gap-6 text-left">
            <div className="inline-flex items-center gap-2 bg-white/5 border border-white/10 px-3.5 py-1.5 rounded-full text-xs font-medium text-brand-300 w-fit">
              <Layers className="w-4 h-4" />
              <span>Project Scaffold Established</span>
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.1] text-white">
              Intelligent Developer <br />
              <span className="text-gradient">Allocation Platform</span>
            </h1>
            <p className="text-slate-400 text-lg sm:text-xl max-w-2xl leading-relaxed">
              Match clients automatically using custom AI agents, enforce developer allocation limits, and schedule initial kick-off sessions seamlessly. 
            </p>
            <div className="flex flex-wrap gap-4 pt-4">
              <a 
                href="#flow"
                className="bg-brand-600 hover:bg-brand-500 text-white font-semibold text-base px-6 py-3.5 rounded-xl transition-all duration-300 shadow-lg shadow-brand-600/20 hover:translate-y-[-2px] flex items-center gap-2"
              >
                Explore System Flow
                <ArrowRight className="w-5 h-5" />
              </a>
              <a 
                href="#rules"
                className="bg-white/5 hover:bg-white/10 border border-white/10 font-semibold text-base px-6 py-3.5 rounded-xl transition-all duration-300 hover:translate-y-[-2px]"
              >
                View Master Rules
              </a>
            </div>

            {/* Quick Metrics */}
            <div className="grid grid-cols-3 gap-6 pt-10 border-t border-white/5 mt-4">
              <div>
                <span className="block text-2xl font-bold text-white">2 Clients</span>
                <span className="text-xs text-slate-400">Max limit per dev</span>
              </div>
              <div>
                <span className="block text-2xl font-bold text-white">3 Specialisms</span>
                <span className="text-xs text-slate-400">AI/ML, DevOps, Auto</span>
              </div>
              <div>
                <span className="block text-2xl font-bold text-white">Cal.com</span>
                <span className="text-xs text-slate-400">Integrated schedule</span>
              </div>
            </div>
          </div>

          {/* Interactive UI Mockup Preview */}
          <div className="lg:col-span-5 relative">
            <div className="absolute -inset-1 rounded-2xl bg-gradient-to-tr from-brand-600 to-blue-500 opacity-20 blur-xl animate-pulse" />
            <div className="relative glassmorphism rounded-2xl p-6 shadow-2xl flex flex-col gap-6">
              <div className="flex items-center justify-between border-b border-white/5 pb-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-rose-500" />
                  <div className="w-3 h-3 rounded-full bg-amber-500" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500" />
                </div>
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Live Preview Simulation</span>
              </div>

              {/* Simulation Card */}
              <div className="flex flex-col gap-4">
                <div className="bg-slate-900/50 p-4 rounded-xl border border-white/5 flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-brand-300 font-bold uppercase tracking-wider">AI Analysis Intake</span>
                    <span className="text-[10px] text-slate-400 bg-white/5 px-2 py-0.5 rounded">Analysis OK</span>
                  </div>
                  <p className="text-xs italic text-slate-300">
                    "We need an automated DevOps engineer to configure our pipelines and set up Docker containers."
                  </p>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-[10px] bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded font-medium">DevOps</span>
                    <span className="text-[10px] bg-brand-500/10 text-brand-400 border border-brand-500/20 px-2 py-0.5 rounded font-medium">Automation</span>
                  </div>
                </div>

                <div className="flex items-center justify-center py-2">
                  <ChevronRight className="w-5 h-5 text-brand-500 rotate-90" />
                </div>

                {/* Match Allocation */}
                <div className="bg-slate-900/50 p-4 rounded-xl border border-white/5 flex flex-col gap-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-brand-300 font-bold uppercase tracking-wider">Recommended Match</span>
                    <span className="text-[10px] text-emerald-400 font-semibold flex items-center gap-1">
                      <Check className="w-3 h-3" /> Available (1/2 Active Clients)
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-sm text-white">
                      JD
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-white">John Doe</h4>
                      <p className="text-[10px] text-slate-400">DevOps & Cloud Engineer</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Confirm Actions */}
              <div className="flex gap-2">
                <button className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold py-2.5 rounded-lg transition-colors">
                  Approve Allocation
                </button>
                <button className="flex-1 bg-white/5 hover:bg-white/10 text-slate-300 text-xs font-bold py-2.5 rounded-lg transition-colors">
                  Reject Request
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Feature Overview Section */}
        <section id="features" className="py-12 border-t border-white/5 flex flex-col gap-12">
          <div className="text-center flex flex-col gap-3">
            <h2 className="text-3xl font-extrabold text-white tracking-tight">System Core Modules</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Our micro-architecture balances manual intervention with autonomous AI features to provide error-free management.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white/[0.02] border border-white/5 p-6 rounded-2xl hover:border-brand-500/30 transition-all duration-300 flex flex-col gap-4">
              <div className="p-3 bg-brand-500/10 rounded-xl w-fit">
                <Cpu className="w-6 h-6 text-brand-400" />
              </div>
              <h3 className="text-lg font-bold text-white">AI-Powered Extraction</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Ingests audio calls, WhatsApp texts, and emails to map the client's scope of work to standard developer profiles automatically.
              </p>
            </div>

            <div className="bg-white/[0.02] border border-white/5 p-6 rounded-2xl hover:border-brand-500/30 transition-all duration-300 flex flex-col gap-4">
              <div className="p-3 bg-brand-500/10 rounded-xl w-fit">
                <Users className="w-6 h-6 text-brand-400" />
              </div>
              <h3 className="text-lg font-bold text-white">Workload Enforcers</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Automatically checks that developers are assigned a maximum of 2 active clients. Instantly updates the synchronization sheet.
              </p>
            </div>

            <div className="bg-white/[0.02] border border-white/5 p-6 rounded-2xl hover:border-brand-500/30 transition-all duration-300 flex flex-col gap-4">
              <div className="p-3 bg-brand-500/10 rounded-xl w-fit">
                <Calendar className="w-6 h-6 text-brand-400" />
              </div>
              <h3 className="text-lg font-bold text-white">Cal.com Scheduler</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Enables approved client profiles to book onboarding meetings directly with their allocated developers without back-and-forth emails.
              </p>
            </div>
          </div>
        </section>

        {/* Master Rules Section */}
        <section id="rules" className="py-12 border-t border-white/5 flex flex-col gap-8">
          <div className="flex flex-col gap-3">
            <h2 className="text-3xl font-extrabold text-white tracking-tight">System Constraints (Master Rules)</h2>
            <p className="text-slate-400">
              The operational guidelines governing the software backend behavior.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="flex gap-4 p-4 rounded-xl bg-white/[0.01] border border-white/5 items-start">
              <ShieldCheck className="w-6 h-6 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="font-bold text-white text-base">Backend Rule Authority</h4>
                <p className="text-sm text-slate-400 mt-1 leading-relaxed">
                  The FastAPI backend is the sole authority for constraints. Frontend layouts provide visuals but do not replace authorization.
                </p>
              </div>
            </div>

            <div className="flex gap-4 p-4 rounded-xl bg-white/[0.01] border border-white/5 items-start">
              <AlertCircle className="w-6 h-6 text-brand-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="font-bold text-white text-base">Allocation Cap (Max 2)</h4>
                <p className="text-sm text-slate-400 mt-1 leading-relaxed">
                  Every developer portfolio strictly permits &le; 2 active client mappings. Database check constraints and transaction blocks enforce this limit.
                </p>
              </div>
            </div>

            <div className="flex gap-4 p-4 rounded-xl bg-white/[0.01] border border-white/5 items-start">
              <Database className="w-6 h-6 text-blue-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="font-bold text-white text-base">System Database of Record</h4>
                <p className="text-sm text-slate-400 mt-1 leading-relaxed">
                  PostgreSQL 16 serves as the main transactional database. Google Sheets serves as a secondary sync layer for roster visibility.
                </p>
              </div>
            </div>

            <div className="flex gap-4 p-4 rounded-xl bg-white/[0.01] border border-white/5 items-start">
              <Clock className="w-6 h-6 text-purple-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="font-bold text-white text-base">Separate Configurations</h4>
                <p className="text-sm text-slate-400 mt-1 leading-relaxed">
                  Development and production environments remain isolated. The production stack uses custom Docker settings without mounts or reloads.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 bg-slate-950 py-8">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <p>&copy; {new Date().getFullYear()} DevMatch AI. All rights reserved.</p>
          <div className="flex gap-6">
            <span>FastAPI Core v0.1.0</span>
            <span>Next.js Client v15.1.0</span>
            <span>PostgreSQL v16</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
