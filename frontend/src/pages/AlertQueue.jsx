import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Search, 
  Filter, 
  ArrowUpDown, 
  ShieldAlert, 
  ArrowRight, 
  User, 
  Landmark,
  RefreshCw
} from 'lucide-react';
import { useRole } from '../context/RoleContext';

export default function AlertQueue() {
  const { maskValue } = useRole();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLevel, setSelectedLevel] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState('risk_score');
  const [sortOrder, setSortOrder] = useState('desc');

  const fetchAlerts = () => {
    setLoading(true);
    fetch('/api/alerts')
      .then(res => res.json())
      .then(data => {
        setAlerts(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching alerts:', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  // Filtering
  const filteredAlerts = alerts.filter(alt => {
    if (selectedLevel !== 'ALL' && alt.risk_level.toUpperCase() !== selectedLevel) {
      return false;
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchCust = alt.customer_id.toLowerCase().includes(q) || alt.customer_name.toLowerCase().includes(q);
      const matchEmp = alt.employee_id?.toLowerCase().includes(q) || alt.employee_name?.toLowerCase().includes(q);
      const matchType = alt.alert_type.toLowerCase().includes(q);
      const matchId = alt.id.toLowerCase().includes(q);
      return matchCust || matchEmp || matchType || matchId;
    }
    return true;
  });

  // Sorting
  filteredAlerts.sort((a, b) => {
    let aVal = a[sortField];
    let bVal = b[sortField];
    if (typeof aVal === 'string') aVal = aVal.toLowerCase();
    if (typeof bVal === 'string') bVal = bVal.toLowerCase();

    if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
    return 0;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center space-x-2">
            <span>Alert Triage & Investigation Queue</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Prioritized operational queue with multidimensional risk scoring and insider-correlation telemetry.
          </p>
        </div>

        <button
          onClick={fetchAlerts}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 text-slate-700 text-xs transition-colors self-start border border-slate-200 shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel p-4 rounded-xl border border-slate-200 bg-white shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3">
        
        {/* Search */}
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
          <input
            type="text"
            id="alert-search-input"
            placeholder="Search by ID, Employee, Customer..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 transition-colors font-sans"
          />
        </div>

        {/* Level Filter Tabs */}
        <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-lg border border-slate-200 w-full sm:w-auto justify-center">
          {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map((lvl) => (
            <button
              key={lvl}
              onClick={() => setSelectedLevel(lvl)}
              className={`px-3 py-1 rounded text-xs font-mono font-medium transition-colors ${
                selectedLevel === lvl 
                  ? 'bg-blue-600 text-white font-bold shadow-sm' 
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>

      </div>

      {/* Queue Table */}
      <div className="glass-panel rounded-xl border border-slate-200 bg-white overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-mono text-[11px] uppercase border-b border-slate-200">
              <tr>
                <th 
                  className="py-3 px-4 cursor-pointer hover:text-slate-900"
                  onClick={() => handleSort('id')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Alert ID</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th 
                  className="py-3 px-4 cursor-pointer hover:text-slate-900"
                  onClick={() => handleSort('risk_score')}
                >
                  <div className="flex items-center space-x-1">
                    <span>Risk Score</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-4">Employee Telemetry</th>
                <th className="py-3 px-4">Customer Account</th>
                <th className="py-3 px-4">Detection Typology</th>
                <th className="py-3 px-4">Prior Precedents</th>
                <th className="py-3 px-4 text-right">Dossier</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredAlerts.length === 0 ? (
                <tr>
                  <td colSpan="7" className="py-8 text-center text-slate-500 font-mono">
                    No matching alerts found in queue.
                  </td>
                </tr>
              ) : (
                filteredAlerts.map((alt) => (
                  <tr 
                    key={alt.id} 
                    className={`hover:bg-slate-50 transition-colors ${alt.id === 'ALT_1001' ? 'bg-red-50/40' : ''}`}
                  >
                    {/* ID */}
                    <td className="py-3 px-4 font-mono font-bold text-blue-600">
                      <div className="flex items-center space-x-1.5">
                        <span>{alt.id}</span>
                        {alt.id === 'ALT_1001' && (
                          <span className="px-1.5 py-0.2 rounded bg-red-50 text-red-700 border border-red-200 text-[9px] font-bold animate-pulse">
                            HERO CASE
                          </span>
                        )}
                      </div>
                      <div className="text-[10px] text-slate-400 font-sans font-normal mt-0.5">
                        {new Date(alt.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} UTC
                      </div>
                    </td>

                    {/* Risk Badge */}
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono font-bold ${
                        alt.risk_level === 'High' ? 'bg-red-50 text-red-700 border border-red-200' :
                        (alt.risk_level === 'Medium' ? 'bg-amber-50 text-amber-700 border border-amber-200' : 'bg-emerald-50 text-emerald-700 border border-emerald-200')
                      }`}>
                        {alt.risk_score.toFixed(0)} &bull; {alt.risk_level}
                      </span>
                    </td>

                    {/* Employee */}
                    <td className="py-3 px-4 text-slate-800">
                      {alt.employee_id ? (
                        <div className="flex items-center space-x-2">
                          <User className="w-3.5 h-3.5 text-purple-600" />
                          <div>
                            <div className="font-semibold text-slate-900">{alt.employee_name}</div>
                            <div className="text-[11px] text-slate-500">{alt.employee_role} ({alt.employee_branch})</div>
                          </div>
                        </div>
                      ) : (
                        <span className="text-slate-400 italic">No insider linked</span>
                      )}
                    </td>

                    {/* Customer */}
                    <td className="py-3 px-4 text-slate-800">
                      <div className="flex items-center space-x-2">
                        <Landmark className="w-3.5 h-3.5 text-blue-600" />
                        <div>
                          <div className="font-semibold text-slate-900">
                            {maskValue(alt.customer_name, 'name')}
                          </div>
                          <div className="text-[11px] text-slate-500 font-mono">
                            {alt.customer_id} &bull; {alt.customer_branch}
                          </div>
                        </div>
                      </div>
                    </td>

                    {/* Typology & Lead */}
                    <td className="py-3 px-4">
                      <span className="text-slate-900 font-medium">
                        {alt.alert_type.replace(/_/g, ' ')}
                      </span>
                      <div className="text-[11px] text-slate-500 line-clamp-1 max-w-xs">
                        {alt.lead_reason}
                      </div>
                    </td>

                    {/* Similar Precedents */}
                    <td className="py-3 px-4">
                      {alt.similar_cases_count > 0 ? (
                        <span className="px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200 text-[10px] font-mono font-bold">
                          {alt.similar_cases_count} Prior Cases
                        </span>
                      ) : (
                        <span className="text-slate-400 font-mono text-[11px]">First seen</span>
                      )}
                    </td>

                    {/* Action */}
                    <td className="py-3 px-4 text-right">
                      <Link
                        to={`/alerts/${alt.id}`}
                        id={`investigate-btn-${alt.id}`}
                        className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold transition-all shadow-sm"
                      >
                        <span>Investigate</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>

                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
