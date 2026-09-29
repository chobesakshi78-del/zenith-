import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Sliders, 
  Play, 
  ShieldAlert, 
  ShieldCheck, 
  Sparkles, 
  Database, 
  Clock, 
  ArrowUpRight, 
  CheckCircle2, 
  AlertTriangle,
  History,
  FileCode,
  Layers,
  Activity
} from 'lucide-react';

export default function Simulator() {
  const [scenarioType, setScenarioType] = useState('SUSPICIOUS_INSIDER');
  const [employeeId, setEmployeeId] = useState('E102');
  const [customerId, setCustomerId] = useState('C417');
  const [amount, setAmount] = useState(49000);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loadingAudit, setLoadingAudit] = useState(true);

  const fetchAuditLogs = () => {
    fetch('/api/audit-logs')
      .then(res => res.json())
      .then(data => {
        setAuditLogs(data);
        setLoadingAudit(false);
      })
      .catch(err => {
        console.error('Audit fetch error:', err);
        setLoadingAudit(false);
      });
  };

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  const handleSimulate = (e) => {
    e.preventDefault();
    setSubmitting(true);
    setResult(null);

    fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scenario_type: scenarioType,
        employee_id: employeeId,
        customer_id: customerId,
        amount: parseFloat(amount)
      })
    })
      .then(res => res.json())
      .then(data => {
        setResult(data);
        setSubmitting(false);
        fetchAuditLogs();
      })
      .catch(err => {
        console.error('Simulation error:', err);
        setSubmitting(false);
      });
  };

  const scenarioPresets = {
    'SUSPICIOUS_INSIDER': {
      title: 'Rogue Employee Collusion & Circular Flow',
      desc: 'Simulates unauthorized cross-branch customer record modification by CSO E102 followed 3 minutes later by a circular cycle below INR 50k.',
      defaultEmp: 'E102',
      defaultCust: 'C417',
      defaultAmt: 49000
    },
    'STRUCTURING': {
      title: 'Sub-Threshold Structured Splitting (Smurfing)',
      desc: 'Simulates 3 rapid installments under INR 50,000 threshold within a 30-minute window to avoid regulatory CTR reporting.',
      defaultEmp: 'E115',
      defaultCust: 'C142',
      defaultAmt: 49200
    },
    'BENIGN_TICKET': {
      title: 'Benign Inquiry with Verified Support Ticket',
      desc: 'Simulates a cross-branch account inquiry by an employee with a legitimate attached IT Service Ticket (TKT-XXXX) to test False Positive Shield noise suppression.',
      defaultEmp: 'E105',
      defaultCust: 'C350',
      defaultAmt: 0
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center space-x-2">
              <Sliders className="w-6 h-6 text-blue-600" />
              <span>Interactive Scenario Simulation Studio</span>
            </h1>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-semibold">
              LIVE INJECTION
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Inject synthetic insider fraud vectors and legitimate benign transactions directly into the live engine to observe detection, risk scoring, and False Positive Shield activation.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Link
            to="/alerts"
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 text-slate-700 text-xs font-medium border border-slate-200 shadow-sm transition-colors"
          >
            <span>View All Active Alerts</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Simulation Form & Presets (7 cols) */}
        <div className="lg:col-span-7 glass-panel p-5 rounded-xl border border-slate-200 bg-white shadow-sm space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-900 flex items-center space-x-2">
              <Database className="w-4 h-4 text-blue-600" />
              <span>Scenario Injector Configuration</span>
            </span>
            <span className="text-[10px] font-mono text-slate-400">
              Live SQLite + Graph Pipeline
            </span>
          </div>

          {/* Scenario Type Selection */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-700">
              Select Attack Vector or Benign Scenario
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              {Object.entries(scenarioPresets).map(([key, val]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => {
                    setScenarioType(key);
                    setEmployeeId(val.defaultEmp);
                    setCustomerId(val.defaultCust);
                    setAmount(val.defaultAmt);
                  }}
                  className={`p-3 rounded-lg border text-left transition-all ${
                    scenarioType === key
                      ? 'bg-blue-50/80 border-blue-400 shadow-sm'
                      : 'bg-slate-50 border-slate-200 hover:bg-slate-100/70'
                  }`}
                >
                  <div className="font-semibold text-xs text-slate-900">
                    {val.title}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1 line-clamp-2">
                    {val.desc}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Preset Description Banner */}
          <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700 flex items-start space-x-2">
            <Sparkles className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-slate-900">Scenario Intent: </span>
              <span>{scenarioPresets[scenarioType]?.desc}</span>
            </div>
          </div>

          {/* Input Parameters */}
          <form onSubmit={handleSimulate} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-[11px] font-mono text-slate-500 mb-1">
                  Employee ID
                </label>
                <input
                  type="text"
                  value={employeeId}
                  onChange={e => setEmployeeId(e.target.value)}
                  className="w-full px-3 py-1.5 text-xs font-mono bg-slate-50 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:border-blue-500 shadow-sm"
                  required
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-500 mb-1">
                  Target Customer ID
                </label>
                <input
                  type="text"
                  value={customerId}
                  onChange={e => setCustomerId(e.target.value)}
                  className="w-full px-3 py-1.5 text-xs font-mono bg-slate-50 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:border-blue-500 shadow-sm"
                  required
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-500 mb-1">
                  Amount (INR)
                </label>
                <input
                  type="number"
                  value={amount}
                  onChange={e => setAmount(e.target.value)}
                  disabled={scenarioType === 'BENIGN_TICKET'}
                  className="w-full px-3 py-1.5 text-xs font-mono bg-slate-50 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:border-blue-500 disabled:opacity-40 shadow-sm"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-sm flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <Activity className="w-4 h-4 animate-spin" />
                  <span>Synthesizing Telemetry & Executing Graph Scan...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span>Inject Synthetic Scenario & Trigger Pipeline</span>
                </>
              )}
            </button>
          </form>

          {/* Results Alert Card */}
          {result && (
            <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-200 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-blue-700 flex items-center space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Simulation Successful & Pipeline Scan Complete</span>
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white text-blue-700 border border-blue-200 font-semibold">
                  {result.total_active_alerts} Alerts Active
                </span>
              </div>

              <p className="text-xs text-slate-700">
                {result.details}
              </p>

              <div className="pt-2 flex items-center space-x-3">
                <Link
                  to="/alerts"
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium transition-colors shadow-sm"
                >
                  <span>Open Alert Queue</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </Link>

                <Link
                  to="/alerts/ALT_1001"
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 text-slate-700 text-xs font-medium border border-slate-200 transition-colors shadow-sm"
                >
                  <span>View Hero Incident (ALT_1001)</span>
                </Link>
              </div>
            </div>
          )}

        </div>

        {/* Right Column: Live Audit Ledger (5 cols) */}
        <div className="lg:col-span-5 glass-panel p-5 rounded-xl border border-slate-200 bg-white shadow-sm flex flex-col h-[650px]">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-900 flex items-center space-x-2">
              <History className="w-4 h-4 text-blue-600" />
              <span>Immutable Audit Trail Ledger</span>
            </span>
            <button
              onClick={fetchAuditLogs}
              className="text-[10px] font-mono text-blue-600 hover:underline font-semibold"
            >
              Refresh
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2.5 mt-3 pr-1">
            {loadingAudit ? (
              <div className="py-12 text-center text-xs text-slate-400 font-mono">
                Loading audit trail...
              </div>
            ) : auditLogs.length === 0 ? (
              <div className="py-12 text-center text-xs text-slate-400 font-mono">
                No audit logs recorded yet.
              </div>
            ) : (
              auditLogs.map((log) => (
                <div
                  key={log.id}
                  className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs space-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-blue-600 text-[11px]">
                      {log.action}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      {new Date(log.timestamp).toLocaleTimeString()} UTC
                    </span>
                  </div>

                  <div className="text-[11px] text-slate-700">
                    {log.details}
                  </div>

                  <div className="text-[10px] text-slate-400 flex items-center justify-between pt-1 border-t border-slate-200">
                    <span>Actor: {log.actor}</span>
                    {log.case_id && <span className="font-mono text-slate-600 font-medium">{log.case_id}</span>}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

    </div>
  );
}
