import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import AlertQueue from './pages/AlertQueue';
import AlertDetail from './pages/AlertDetail';
import RoleDnaProfiler from './pages/RoleDnaProfiler';
import ShieldMetrics from './pages/ShieldMetrics';
import Simulator from './pages/Simulator';
import { ShieldCheck, ShieldAlert, Cpu, Terminal, Lock, ExternalLink } from 'lucide-react';

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      
      {/* Top Application Header */}
      <Header />

      {/* Main Content Area */}
      <main className="flex-1 pb-12">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/alerts" element={<AlertQueue />} />
          <Route path="/alerts/:alertId" element={<AlertDetail />} />
          <Route path="/employees" element={<RoleDnaProfiler />} />
          <Route path="/metrics" element={<ShieldMetrics />} />
          <Route path="/simulator" element={<Simulator />} />
          <Route path="*" element={<Dashboard />} />
        </Routes>
      </main>

      {/* High-Tech Terminal Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 rounded bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600">
              <ShieldCheck className="w-3.5 h-3.5" />
            </div>
            <div>
              <span className="font-semibold text-slate-900">
                ZenithGuard AML & Insider Intelligence Platform
              </span>
              <span className="text-[10px] font-mono text-blue-600 ml-2">
                v1.4-Core (FIN-04)
              </span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-[11px] font-mono text-slate-500">
            <span className="flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span className="text-slate-600">3 Branches Active</span>
            </span>
            <span>|</span>
            <span>40 Employees Monitored</span>
            <span>|</span>
            <span>401 Accounts</span>
            <span>|</span>
            <span>7,929 Transactions Indexed</span>
            <span>|</span>
            <span className="text-blue-600 flex items-center space-x-1">
              <Lock className="w-3 h-3" />
              <span>SHA-256 Forensics Enabled</span>
            </span>
          </div>

        </div>
      </footer>

    </div>
  );
}
