import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldAlert, 
  AlertTriangle, 
  FolderLock, 
  Clock, 
  TrendingUp, 
  ArrowUpRight, 
  UserCheck, 
  Activity,
  Layers
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  AreaChart, Area, CartesianGrid 
} from 'recharts';
import { useRole } from '../context/RoleContext';

export default function Dashboard() {
  const { maskValue } = useRole();
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/stats')
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error('Error fetching stats:', err));

    fetch('/api/alerts')
      .then(res => res.json())
      .then(data => {
        setAlerts(data);
        setLoading(false);
      })
      .catch(err => console.error('Error fetching alerts:', err));
  }, []);

  // Trend dummy points anchored on actual risk timeline
  const trendData = [
    { time: '09:00', high: 1, medium: 2, score: 65 },
    { time: '09:30', high: 2, medium: 2, score: 72 },
    { time: '10:00', high: 4, medium: 3, score: 88 },
    { time: '10:15', high: 5, medium: 2, score: 99 },
    { time: '10:30', high: 5, medium: 3, score: 94 },
    { time: '11:00', high: 4, medium: 4, score: 85 },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      
      {/* Page Title & Mission Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center space-x-2">
            <span>Financial Crime & Insider Risk Command Center</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time correlation of internal banking telemetry with customer transaction graphs across Pune, Mumbai & Nagpur branches.
          </p>
        </div>

        {/* Quick Link to Hero Case */}
        <Link
          to="/alerts/ALT_1001"
          id="hero-case-banner-btn"
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white font-medium text-xs shadow-sm transition-all"
        >
          <ShieldAlert className="w-4 h-4 animate-bounce" />
          <span>Inspect In-Progress Hero Case (ALT_1001)</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Total Alerts */}
        <div className="glass-panel p-4 rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Total Flagged Alerts</span>
            <div className="p-2 rounded-lg bg-blue-50 text-blue-600 border border-blue-200">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-black font-mono text-slate-900">
              {stats?.kpis?.total_alerts || 9}
            </span>
            <span className="text-[11px] text-emerald-600 font-medium">9 Evaluated Scenarios</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-400">
            Across 4,859 access events & 7,929 txns
          </div>
        </div>

        {/* High Risk */}
        <div className="glass-panel p-4 rounded-xl border border-slate-200 bg-white shadow-sm glow-red">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">High Risk Incidents</span>
            <div className="p-2 rounded-lg bg-red-50 text-red-600 border border-red-200">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-black font-mono text-red-600">
              {stats?.kpis?.high_risk_alerts || 5}
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-50 text-red-700 border border-red-200 font-mono font-bold animate-pulse">
              ACTION REQUIRED
            </span>
          </div>
          <div className="mt-2 text-[11px] text-slate-400">
            Critical threshold &ge; 70 score
          </div>
        </div>

        {/* Open Cases */}
        <div className="glass-panel p-4 rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Active Investigations</span>
            <div className="p-2 rounded-lg bg-blue-50 text-blue-600 border border-blue-200">
              <FolderLock className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-black font-mono text-slate-900">
              {stats?.kpis?.open_cases || 5}
            </span>
            <span className="text-[11px] text-blue-600 font-medium">Assigned to Lead</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-400">
            Open, In Review & Escalated dossiers
          </div>
        </div>

        {/* Avg Time-to-Triage */}
        <div className="glass-panel p-4 rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Avg Time-to-Triage</span>
            <div className="p-2 rounded-lg bg-purple-50 text-purple-600 border border-purple-200">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline space-x-2">
            <span className="text-2xl font-black font-mono text-purple-700">
              14m
            </span>
            <span className="text-[11px] text-purple-600 font-medium">-68% vs baseline</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-400">
            Empowered by Explainability & Replay
          </div>
        </div>

      </div>

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Risk Trend Line */}
        <div className="glass-panel p-5 rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <TrendingUp className="w-4 h-4 text-blue-600" />
                <span>Incident Velocity & Peak Risk Score</span>
              </h2>
              <p className="text-[11px] text-slate-500">Temporal risk evolution leading up to Hero event (10:15 UTC)</p>
            </div>
          </div>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#DC2626" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#DC2626" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis dataKey="time" stroke="#64748B" fontSize={10} fontFamilly="monospace" />
                <YAxis stroke="#64748B" fontSize={10} domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', borderRadius: '8px', fontSize: '11px', color: '#0F172A', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                />
                <Area type="monotone" dataKey="score" stroke="#DC2626" strokeWidth={2} fillOpacity={1} fill="url(#scoreGrad)" name="Peak Risk Score" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Alerts by Type Breakdown */}
        <div className="glass-panel p-5 rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <Activity className="w-4 h-4 text-blue-600" />
                <span>Detection Typologies Breakdown</span>
              </h2>
              <p className="text-[11px] text-slate-500">Alert distribution across the 9 modular detectors</p>
            </div>
          </div>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats?.alerts_by_type || []} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" horizontal={false} />
                <XAxis type="number" stroke="#64748B" fontSize={10} />
                <YAxis dataKey="type" type="category" stroke="#64748B" fontSize={9} width={130} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#E2E8F0', borderRadius: '8px', fontSize: '11px', color: '#0F172A', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                />
                <Bar dataKey="count" fill="#2563EB" radius={[0, 4, 4, 0]} name="Detected Alerts" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Bottom Row: Risky Employees & Live Alert Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Top Risky Employees */}
        <div className="glass-panel p-5 rounded-xl border border-slate-200 bg-white shadow-sm lg:col-span-1">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <UserCheck className="w-4 h-4 text-purple-600" />
              <span>Top Risky Employees</span>
            </h2>
            <Link to="/employees" className="text-[11px] text-blue-600 hover:underline font-medium">
              View All
            </Link>
          </div>

          <div className="space-y-3">
            {stats?.top_risky_employees?.map((emp) => (
              <div key={emp.id} className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
                <div>
                  <div className="font-semibold text-slate-900 flex items-center space-x-1.5">
                    <span>{emp.name}</span>
                    <span className="text-[10px] font-mono text-purple-600 font-bold">({emp.id})</span>
                  </div>
                  <div className="text-[11px] text-slate-500">
                    {emp.role} &bull; {emp.branch_id.replace('BR_', '')}
                  </div>
                </div>

                <div className="text-right">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                    emp.max_risk_score >= 70 ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-amber-50 text-amber-700 border border-amber-200'
                  }`}>
                    {emp.max_risk_score.toFixed(0)} Risk
                  </span>
                  <div className="text-[10px] text-slate-400 mt-1">
                    {emp.alert_count} alert{emp.alert_count > 1 ? 's' : ''}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Live Alert Feed Stream */}
        <div className="glass-panel p-5 rounded-xl border border-slate-200 bg-white shadow-sm lg:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" />
              <h2 className="text-sm font-bold text-slate-900">Live Alert Triage Stream</h2>
            </div>
            <Link to="/alerts" className="text-[11px] text-blue-600 hover:underline font-medium">
              View Queue ({alerts.length})
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-mono text-[10px] uppercase border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Alert ID</th>
                  <th className="py-2.5 px-3">Risk Level</th>
                  <th className="py-2.5 px-3">Employee</th>
                  <th className="py-2.5 px-3">Customer Target</th>
                  <th className="py-2.5 px-3">Typology</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {alerts.slice(0, 6).map((alt) => (
                  <tr key={alt.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-2.5 px-3 font-mono font-semibold text-blue-600">
                      {alt.id}
                      {alt.id === 'ALT_1001' && (
                        <span className="ml-1.5 px-1 py-0.2 rounded bg-red-50 text-red-700 border border-red-200 text-[9px] font-bold">
                          HERO
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                        alt.risk_level === 'High' ? 'bg-red-50 text-red-700 border border-red-200' :
                        (alt.risk_level === 'Medium' ? 'bg-amber-50 text-amber-700 border border-amber-200' : 'bg-emerald-50 text-emerald-700 border border-emerald-200')
                      }`}>
                        {alt.risk_score.toFixed(0)} &bull; {alt.risk_level}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-800">
                      {alt.employee_id ? (
                        <span>{alt.employee_name} <span className="text-purple-600 font-mono font-medium">({alt.employee_id})</span></span>
                      ) : (
                        <span className="text-slate-400 italic">None</span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-slate-800">
                      {maskValue(alt.customer_name, 'name')} <span className="text-blue-600 font-mono font-medium">({alt.customer_id})</span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-600">
                      {alt.alert_type.replace(/_/g, ' ')}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <Link
                        to={`/alerts/${alt.id}`}
                        className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 text-[11px] font-medium transition-colors"
                      >
                        Investigate
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>

    </div>
  );
}
