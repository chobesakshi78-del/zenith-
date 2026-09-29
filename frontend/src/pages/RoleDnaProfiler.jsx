import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Users, 
  Search, 
  Filter, 
  ShieldAlert, 
  AlertTriangle, 
  CheckCircle2, 
  Activity, 
  Building2, 
  FileEdit, 
  Clock, 
  Layers, 
  ArrowUpRight,
  TrendingUp,
  Award,
  ChevronRight
} from 'lucide-react';
import { 
  Radar, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  ResponsiveContainer, 
  Tooltip
} from 'recharts';
import { useRole } from '../context/RoleContext';

export default function RoleDnaProfiler() {
  const { maskValue } = useRole();
  const [employees, setEmployees] = useState([]);
  const [selectedEmpId, setSelectedEmpId] = useState('E102');
  const [dnaData, setDnaData] = useState(null);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDna, setLoadingDna] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBranch, setSelectedBranch] = useState('ALL');

  // Load employee list
  useEffect(() => {
    fetch('/api/employees')
      .then(res => res.json())
      .then(data => {
        setEmployees(data);
        setLoadingList(false);
      })
      .catch(err => {
        console.error('Failed to load employees:', err);
        setLoadingList(false);
      });
  }, []);

  // Load DNA data for selected employee
  useEffect(() => {
    if (!selectedEmpId) return;
    setLoadingDna(true);
    fetch(`/api/employees/${selectedEmpId}/dna`)
      .then(res => res.json())
      .then(data => {
        setDnaData(data);
        setLoadingDna(false);
      })
      .catch(err => {
        console.error('Failed to load employee DNA:', err);
        setLoadingDna(false);
      });
  }, [selectedEmpId]);

  const filteredEmployees = employees.filter(emp => {
    const matchesSearch = 
      emp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      emp.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      emp.role.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesBranch = selectedBranch === 'ALL' || emp.branch_id === selectedBranch;
    return matchesSearch && matchesBranch;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center space-x-2">
              <Users className="w-6 h-6 text-blue-600" />
              <span>Role-DNA Anomaly Profiler</span>
            </h1>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200 font-semibold">
              COHORT BASELINE ENGINE
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Machine learning behavioral baselining using Isolation Forest & peer cohort deviation Z-scores. Identifies rogue access, after-hours snooping, and cross-branch boundary violations.
          </p>
        </div>

        {/* Quick highlight hero employee */}
        <button
          onClick={() => setSelectedEmpId('E102')}
          className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all border shadow-sm ${
            selectedEmpId === 'E102'
              ? 'bg-red-50 border-red-200 text-red-700'
              : 'bg-white border-slate-200 text-slate-700 hover:text-slate-900'
          }`}
        >
          <ShieldAlert className="w-4 h-4 text-red-600 animate-pulse" />
          <span>Inspect Hero Suspect: E102 (Anil Sharma)</span>
        </button>
      </div>

      {/* Main Grid: Sidebar + DNA Visualizer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Employee Roster (4 cols) */}
        <div className="lg:col-span-4 glass-panel p-4 rounded-xl border border-slate-200 bg-white shadow-sm flex flex-col h-[740px]">
          
          <div className="space-y-3 pb-3 border-b border-slate-200">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-900">
                Employee Cohort Roster ({filteredEmployees.length})
              </span>
              <span className="text-[10px] font-mono text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200 font-semibold">
                40 Monitored
              </span>
            </div>

            {/* Search */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search by ID, name, role..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 font-sans"
              />
            </div>

            {/* Branch Filter Tabs */}
            <div className="flex space-x-1 overflow-x-auto text-[10px] font-medium pb-1">
              {['ALL', 'BR_PUNE', 'BR_MUMBAI', 'BR_NAGPUR'].map(br => (
                <button
                  key={br}
                  onClick={() => setSelectedBranch(br)}
                  className={`px-2 py-1 rounded transition-colors whitespace-nowrap ${
                    selectedBranch === br
                      ? 'bg-blue-600 text-white font-semibold shadow-sm'
                      : 'bg-slate-100 text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {br === 'ALL' ? 'All Branches' : br.replace('BR_', '')}
                </button>
              ))}
            </div>
          </div>

          {/* Scrollable list */}
          <div className="flex-1 overflow-y-auto space-y-2 mt-3 pr-1">
            {loadingList ? (
              <div className="py-12 text-center text-xs text-slate-400 font-mono">
                Loading employee cohort...
              </div>
            ) : filteredEmployees.length === 0 ? (
              <div className="py-12 text-center text-xs text-slate-400 font-mono">
                No matching employees found
              </div>
            ) : (
              filteredEmployees.map(emp => {
                const isSelected = emp.id === selectedEmpId;
                const isHero = emp.id === 'E102';
                return (
                  <div
                    key={emp.id}
                    onClick={() => setSelectedEmpId(emp.id)}
                    className={`p-3 rounded-lg border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-blue-50/80 border-blue-400 shadow-sm'
                        : 'bg-slate-50/70 border-slate-200 hover:bg-slate-100/70'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-semibold text-slate-900">
                            {emp.name}
                          </span>
                          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-white text-blue-700 border border-slate-200 font-semibold">
                            {emp.id}
                          </span>
                          {isHero && (
                            <span className="text-[9px] px-1.5 py-0.2 rounded-full bg-red-50 text-red-700 font-mono font-bold animate-pulse border border-red-200">
                              HIGH ANOMALY
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-500 mt-0.5">
                          {emp.role}
                        </p>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white text-slate-600 border border-slate-200">
                        {emp.branch_id.replace('BR_', '')}
                      </span>
                    </div>

                    <div className="mt-2 text-[10px] text-slate-400 flex items-center justify-between">
                      <span>Auth Range: {emp.authorized_customer_range || 'General'}</span>
                      <ChevronRight className={`w-3.5 h-3.5 ${isSelected ? 'text-blue-600' : 'text-slate-400'}`} />
                    </div>
                  </div>
                );
              })
            )}
          </div>

        </div>

        {/* Right Column: Selected Employee DNA Visualizer (8 cols) */}
        <div className="lg:col-span-8 space-y-6">
          
          {loadingDna || !dnaData ? (
            <div className="glass-panel p-16 rounded-xl border border-slate-200 bg-white shadow-sm flex flex-col items-center justify-center text-slate-500 space-y-3">
              <Activity className="w-8 h-8 text-blue-600 animate-spin" />
              <span className="text-xs font-mono">Synthesizing behavioral peer vectors...</span>
            </div>
          ) : (
            <>
              {/* Profile Overview Card */}
              <div className="glass-panel p-5 rounded-xl border border-slate-200 bg-white shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-lg font-bold text-slate-900">{dnaData.name}</span>
                      <span className="text-xs font-mono px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-semibold">
                        {dnaData.employee_id}
                      </span>
                      <span className="text-xs text-slate-500">| {dnaData.role}</span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1 flex items-center space-x-2">
                      <Building2 className="w-3.5 h-3.5 text-slate-400" />
                      <span>Assigned to {dnaData.branch_id}</span>
                    </p>
                  </div>

                  {/* Anomaly Badge */}
                  <div className="flex items-center space-x-3">
                    <div className="text-right">
                      <div className="text-[10px] font-mono uppercase text-slate-500">
                        Peer Anomaly Score
                      </div>
                      <div className={`text-xl font-mono font-bold ${
                        dnaData.anomaly_score >= 0.7 
                          ? 'text-red-600' 
                          : dnaData.anomaly_score >= 0.4 
                            ? 'text-amber-600' 
                            : 'text-emerald-600'
                      }`}>
                        {(dnaData.anomaly_score * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div className={`p-2.5 rounded-xl border ${
                      dnaData.anomaly_score >= 0.7
                        ? 'bg-red-50 text-red-600 border-red-200'
                        : dnaData.anomaly_score >= 0.4
                          ? 'bg-amber-50 text-amber-600 border-amber-200'
                          : 'bg-emerald-50 text-emerald-600 border-emerald-200'
                    }`}>
                      {dnaData.anomaly_score >= 0.7 ? (
                        <AlertTriangle className="w-6 h-6 animate-pulse" />
                      ) : (
                        <CheckCircle2 className="w-6 h-6" />
                      )}
                    </div>
                  </div>
                </div>

                {/* Explanation narrative */}
                <div className="mt-4 p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700 flex items-start space-x-2.5">
                  <ShieldAlert className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-semibold text-slate-900">Cohort Evaluation Summary: </span>
                    <span className="text-slate-700">{dnaData.anomaly_reason}</span>
                  </div>
                </div>
              </div>

              {/* Behavioral Radar & Dimension Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Radar Chart */}
                <div className="glass-panel p-4 rounded-xl border border-slate-200 bg-white shadow-sm flex flex-col">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-900">
                      Behavioral DNA Radar vs Peer Cohort
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      Normalized 5D Vector
                    </span>
                  </div>

                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart cx="50%" cy="50%" outerRadius="75%" data={dnaData.radar_data}>
                        <PolarGrid stroke="#E2E8F0" />
                        <PolarAngleAxis dataKey="dimension" stroke="#64748B" tick={{ fill: '#334155', fontSize: 10 }} />
                        <PolarRadiusAxis stroke="#CBD5E1" tick={{ fill: '#64748B', fontSize: 9 }} />
                        <Radar
                          name={dnaData.name}
                          dataKey="employee_value"
                          stroke="#DC2626"
                          fill="#DC2626"
                          fillOpacity={0.35}
                        />
                        <Radar
                          name="Peer Cohort Baseline"
                          dataKey="peer_mean"
                          stroke="#2563EB"
                          fill="#2563EB"
                          fillOpacity={0.2}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#FFFFFF',
                            borderColor: '#E2E8F0',
                            borderRadius: '8px',
                            color: '#0F172A',
                            fontSize: '11px',
                            boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)'
                          }}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="flex items-center justify-center space-x-6 text-[11px] pt-2 border-t border-slate-200">
                    <div className="flex items-center space-x-1.5">
                      <span className="w-3 h-3 rounded bg-red-100 border border-red-500 inline-block" />
                      <span className="text-slate-800 font-medium">{dnaData.name}</span>
                    </div>
                    <div className="flex items-center space-x-1.5">
                      <span className="w-3 h-3 rounded bg-blue-100 border border-blue-500 inline-block" />
                      <span className="text-slate-600">Peer Cohort Mean</span>
                    </div>
                  </div>
                </div>

                {/* Dimension Metric Breakdown Cards */}
                <div className="glass-panel p-4 rounded-xl border border-slate-200 bg-white shadow-sm space-y-2.5">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-900">
                      Dimension Deviation Metrics (Z-Scores)
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">
                      Z &gt; 2.0 = Anomalous
                    </span>
                  </div>

                  <div className="space-y-2">
                    {dnaData.radar_data.map((dim, i) => {
                      const isHighZ = dim.z_score >= 2.0;
                      const isModZ = dim.z_score >= 1.0 && dim.z_score < 2.0;
                      return (
                        <div
                          key={i}
                          className={`p-2.5 rounded-lg border text-xs flex items-center justify-between ${
                            isHighZ
                              ? 'bg-red-50 border-red-200 text-slate-900'
                              : isModZ
                                ? 'bg-amber-50 border-amber-200 text-slate-900'
                                : 'bg-slate-50 border-slate-200 text-slate-700'
                          }`}
                        >
                          <div>
                            <div className="font-semibold text-slate-900 flex items-center space-x-2">
                              <span>{dim.dimension}</span>
                              {isHighZ && (
                                <span className="text-[9px] px-1.5 py-0.2 rounded bg-red-100 text-red-800 border border-red-200 font-mono font-bold">
                                  Z = +{dim.z_score}
                                </span>
                              )}
                            </div>
                            <div className="text-[11px] text-slate-500 mt-0.5">
                              Employee: <span className="font-mono text-slate-900 font-semibold">{dim.employee_value}</span> | Cohort Mean: <span className="font-mono text-blue-600 font-semibold">{dim.peer_mean}</span>
                            </div>
                          </div>

                          <div className="text-right">
                            <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                              isHighZ 
                                ? 'bg-red-100 text-red-800 border border-red-200' 
                                : isModZ
                                  ? 'bg-amber-100 text-amber-800 border border-amber-200'
                                  : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                            }`}>
                              {isHighZ ? 'HIGH DEV' : isModZ ? 'ELEVATED' : 'NORMAL'}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

              </div>

              {/* Alert History for Employee */}
              <div className="glass-panel p-4 rounded-xl border border-slate-200 bg-white shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-900 flex items-center space-x-2">
                    <ShieldAlert className="w-4 h-4 text-blue-600" />
                    <span>Associated Incidents & Alerts ({dnaData.alert_history.length})</span>
                  </span>
                </div>

                {dnaData.alert_history.length === 0 ? (
                  <div className="p-6 text-center text-xs text-slate-400 font-mono">
                    No flagged alert cases currently linked to this employee profile.
                  </div>
                ) : (
                  <div className="space-y-2">
                    {dnaData.alert_history.map(al => (
                      <div
                        key={al.id}
                        className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-between text-xs"
                      >
                        <div className="flex items-center space-x-3">
                          <span className="font-mono font-bold text-blue-600">{al.id}</span>
                          <span className="text-slate-900 font-medium">{al.alert_type}</span>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-red-50 text-red-700 border border-red-200 font-semibold">
                            Risk {al.risk_score.toFixed(0)} ({al.risk_level})
                          </span>
                        </div>

                        <Link
                          to={`/alerts/${al.id}`}
                          className="inline-flex items-center space-x-1 px-3 py-1 rounded bg-blue-50 text-blue-700 hover:bg-blue-100 text-[11px] font-mono font-medium border border-blue-200 transition-colors"
                        >
                          <span>Open Dossier</span>
                          <ArrowUpRight className="w-3 h-3" />
                        </Link>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}

        </div>

      </div>

    </div>
  );
}
