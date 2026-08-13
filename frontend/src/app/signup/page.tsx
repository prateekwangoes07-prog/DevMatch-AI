'use client';

import React from 'react';
import Link from 'next/link';

export default function SignupPage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-[#0b0f19] px-4 relative overflow-hidden">
      {/* Background lights */}
      <div className="absolute top-[-20%] left-[-20%] w-[600px] h-[600px] rounded-full bg-blue-500/10 blur-[120px]" />
      <div className="absolute bottom-[-20%] right-[-20%] w-[600px] h-[600px] rounded-full bg-indigo-500/10 blur-[120px]" />

      <div className="w-full max-w-md p-8 rounded-2xl glassmorphism z-10 relative text-center">
        <h1 className="text-2xl font-extrabold tracking-tight text-white mb-4">
          Registration Restricted
        </h1>
        <p className="text-sm text-slate-400 mb-6 leading-relaxed">
          Admin account registration is restricted to backend system administrators. 
          To set up a new Admin user, please run the server-side onboarding script or contact support.
        </p>

        <div className="mt-8">
          <Link href="/login" className="px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium transition duration-200 text-sm">
            Return to Login
          </Link>
        </div>
      </div>
    </main>
  );
}
