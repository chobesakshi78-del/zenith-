import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ShieldAlert, 
  ArrowLeft, 
  Download, 
  User, 
  Landmark, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  Send, 
  FileText, 
  Sparkles, 
  HelpCircle,
  TrendingDown,
  Layers,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import RiskGauge from '../components/RiskGauge';
import MoneyFlowGraph from '../components/MoneyFlowGraph';
import CaseReplaySlider from '../components/CaseReplaySlider';
import { useRole } from '../context/RoleContext';

export default function AlertDetail() {
  const { alertId } = useParams();
  const { maskValue } = useRole();

  const [alert, setAlert] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [timelineData, setTimelineData] = useState(null);
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Case Replay active step state
  const [replayStep, setReplayStep] = useState(null);

  // Case management inputs
  const [statusVal, setStatusVal] = useState('Open');
  const [investigatorVal, setInvestigatorVal] = useState('Sarah Chen');
  const [noteInput, setNoteInput] = useState('');
  const [submittingNote, setSubmittingNote] = useState(false);
  const [exportingPdf, setExportingPdf] = useState(false);

  useEffect(() => {
    setLoading(true);
    const targetId = alertId || 'ALT_1001';

    Promise.all([
      fetch(`/api/alerts/${targetId}`).then(r => r.json()),
      fetch(`/api/graph/${targetId}`).then(r => r.json()),
      fetch(`/api/timeline/${targetId}`).then(r => r.json()),
    ])
      .then(([alertRes, graphRes, timelineRes]) => {
        setAlert(alertRes);
        setGraphData(graphRes);
        setTimelineData(timelineRes);

        // Fetch case details if case exists
        if (alertRes.case?.id) {
          fetch(`/api/cases/${alertRes.case.id}`)
            .then(r => r.json())
            .then(cData => {
              setCaseData(cData);
              setStatusVal(cData.status);
              setInvestigatorVal(cData.assigned_investigator);
            })
            .catch(console.error);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading alert detail:', err);
        setLoading(false);
      });
  }, [alertId]);

  const handleStatusChange = (newStatus) => {
    setStatusVal(newStatus);
    if (!caseData?.id) return;
    fetch(`/api/cases/${caseData.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    }).catch(console.error);
  };

  const handleInvestigatorChange = (newInv) => {
    setInvestigatorVal(newInv);
    if (!caseData?.id) return;
    fetch(`/api/cases/${caseData.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ assigned_investigator: newInv })
    }).catch(console.error);
  };

  const handleAddNote = (e) => {
    e.preventDefault();
    if (!noteInput.trim() || !caseData?.id) return;
    setSubmittingNote(true);

    fetch(`/api/cases/${caseData.id}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        author: investigatorVal || 'Investigator',
        note_text: noteInput.trim()
      })
    })
      .then(res => res.json())
      .then(() => {
        // Refresh case details
        return fetch(`/api/cases/${caseData.id}`).then(r => r.json());
      })
      .then(updatedCase => {
        setCaseData(updatedCase);
        setNoteInput('');
        setSubmittingNote(false);
      })
      .catch(err => {
        console.error('Error adding note:', err);
        setSubmittingNote(false);
      });
  };

  const handleExportPdf = () => {
    if (!caseData?.id) return;
    setExportingPdf(true);
    window.location.href = `/api/cases/${caseData.id}/export`;
    setTimeout(() => setExportingPdf(false), 2000);
  };

  if (loading || !alert) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-3">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <span className="text-xs text-slate-500 font-mono">Loading Forensic Intelligence Dossier...</span>
      </div>
    );
  }

  const isHeroCase = alert.id === 'ALT_1001';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Breadcrumb & Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="flex items-center space-x-2 text-xs">
          <Link to="/alerts" className="text-slate-500 hover:text-blue-600 flex items-center space-x-1 font-medium">
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Alert Queue</span>
          </Link>
          <span className="text-slate-400">/</span>
          <span className="text-slate-900 font-mono font-semibold">{alert.id}</span>
          {isHeroCase && (
            <span className="px-2 py-0.5 rounded bg-red-50 text-red-700 border border-red-200 text-[10px] font-mono font-bold animate-pulse">
              HERO CASE: E102 &rarr; C417
            </span>
          )}
        </div>

        {/* Export Button */}
        <button
          id="export-evidence-pdf-btn"
          onClick={handleExportPdf}
          disabled={exportingPdf || !caseData?.id}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition-all border border-blue-600 self-start sm:self-auto disabled:opacity-50"
        >
          <Download className="w-4 h-4" />
          <span>{exportingPdf ? 'Generating SHA-256 PDF...' : 'Export Evidence Report (PDF)'}</span>
        </button>
      </div>

      {/* Hero Summary Card: Risk Gauge + Narrative + Counterfactual */}
      <div className="glass-panel p-6 rounded-xl border border-slate-200 bg-white shadow-sm relative overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          
          {/* Col 1: Risk Gauge */}
          <div className="lg:col-span-4 flex flex-col items-center justify-center p-2 border-b lg:border-b-0 lg:border-r border-slate-200">
            <span className="text-[11px] font-mono uppercase tracking-wider text-slate-500 mb-2">
              Fused Multi-Signal Risk
            </span>
            <RiskGauge score={alert.risk_score} level={alert.risk_level} size={220} />
            
            {alert.similar_cases_count > 0 && (
              <div className="mt-3 px-3 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-200 text-[11px] font-mono flex items-center space-x-1.5 font-medium">
                <Sparkles className="w-3.5 h-3.5 text-purple-600" />
                <span>Pattern matches 2 earlier cases by E102</span>
              </div>
            )}
          </div>

          {/* Col 2: Plain-English Narrative & Counterfactual */}
          <div className="lg:col-span-8 space-y-4">
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-xl font-bold text-slate-900 tracking-tight">
                  {alert.alert_type.replace(/_/g, ' ')}
                </h1>
                <span className="text-xs font-mono text-blue-600 font-semibold">
                  [{alert.lead_reason}]
                </span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed mt-2 p-3.5 rounded-lg bg-slate-50 border border-slate-200">
                {alert.explanation?.narrative}
              </p>
            </div>

            {/* Counterfactual Simulation Line */}
            <div className="p-3.5 rounded-lg bg-blue-50/70 border border-blue-200 flex items-start space-x-3 text-xs">
              <TrendingDown className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-blue-700 uppercase tracking-wider text-[10px] font-mono block">
                  Counterfactual What-If Sensitivity Analysis
                </span>
                <p className="text-slate-700 mt-0.5">
                  {alert.explanation?.counterfactual}
                </p>
              </div>
            </div>

            {/* Involved Entities Badges */}
            <div className="flex flex-wrap gap-2 text-xs">
              <div className="flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-purple-50 border border-purple-200 text-purple-800 font-medium">
                <User className="w-3.5 h-3.5 text-purple-600" />
                <span><b>Employee:</b> {alert.employee?.name} ({alert.employee?.id}) &bull; {alert.employee?.role}</span>
              </div>
              <div className="flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-blue-50 border border-blue-200 text-blue-800 font-medium">
                <Landmark className="w-3.5 h-3.5 text-blue-600" />
                <span><b>Primary Target:</b> {maskValue(alert.customer?.name, 'name')} ({alert.customer?.id}) &bull; {alert.customer?.home_branch_id}</span>
              </div>
            </div>

          </div>

        </div>
      </div>

      {/* Main Grid: Graph + Why Flagged Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Interactive Graph & Replay Studio (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <Layers className="w-4 h-4 text-blue-600" />
              <span>Interactive Money-Flow & Access Topology</span>
            </h2>
            <span className="text-[11px] text-slate-500 font-mono">
              Hover nodes/edges for details
            </span>
          </div>

          {/* Topology Graph */}
          <MoneyFlowGraph 
            graphData={graphData} 
            activeStep={replayStep} 
            highlightCycle={true} 
          />

          {/* Case Replay Studio Slider */}
          <CaseReplaySlider
            steps={timelineData?.timeline || []}
            activeStep={replayStep}
            setActiveStep={setReplayStep}
          />

        </div>

        {/* Right Column: "Why Was This Flagged?" & Contribution Breakdown (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          
          <div className="glass-panel p-5 rounded-xl border border-slate-200 bg-white shadow-sm space-y-4">
            
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <ShieldAlert className="w-4 h-4 text-red-600" />
                <span>Why Was This Flagged? (5 Critical Reasons)</span>
              </h2>
            </div>

            {/* 5 Numbered Concrete Evidence Points */}
            <div className="space-y-2.5 text-xs">
              
              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 flex items-start space-x-2.5">
                <span className="w-5 h-5 rounded-full bg-red-100 text-red-700 flex items-center justify-center font-mono font-bold shrink-0 text-[11px]">1</span>
                <div>
                  <b className="text-slate-900">Outside Authorized Branch:</b>
                  <p className="text-slate-600 mt-0.5">
                    Employee {alert.employee?.name} (Pune Branch) accessed customer {maskValue(alert.customer?.name, 'name')} belonging to Mumbai branch without authorization.
                  </p>
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 flex items-start space-x-2.5">
                <span className="w-5 h-5 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center font-mono font-bold shrink-0 text-[11px]">2</span>
                <div>
                  <b className="text-slate-900">Insider-Touch Preceding Transfers (5 min lag):</b>
                  <p className="text-slate-600 mt-0.5">
                    Account details modified (MODIFY_DETAILS) at 10:01 AM, exactly 4 minutes before circular transfers began.
                  </p>
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 flex items-start space-x-2.5">
                <span className="w-5 h-5 rounded-full bg-red-100 text-red-700 flex items-center justify-center font-mono font-bold shrink-0 text-[11px]">3</span>
                <div>
                  <b className="text-slate-900">Closed Circular Flow (C417 &rarr; C208 &rarr; C731 &rarr; C417):</b>
                  <p className="text-slate-600 mt-0.5">
                    Money routed in 3-hop ring in 7 mins preserving 97.8% of funds (₹49k &rarr; ₹48.5k &rarr; ₹47.9k).
                  </p>
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 flex items-start space-x-2.5">
                <span className="w-5 h-5 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center font-mono font-bold shrink-0 text-[11px]">4</span>
                <div>
                  <b className="text-slate-900">Sub-Threshold Structuring:</b>
                  <p className="text-slate-600 mt-0.5">
                    All transactions clustered between ₹47,900 and ₹49,000, deliberately under the ₹50,000 regulatory reporting threshold.
                  </p>
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 flex items-start space-x-2.5">
                <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-mono font-bold shrink-0 text-[11px]">5</span>
                <div>
                  <b className="text-slate-900">Historical Prior Pattern Match:</b>
                  <p className="text-slate-600 mt-0.5">
                    Identical modus operandi identified in 2 prior historical cases involving employee E102.
                  </p>
                </div>
              </div>

            </div>

            {/* Contribution Bars */}
            <div className="pt-2 border-t border-slate-200 space-y-2">
              <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-slate-500">
                Signal Weights & Normalized Contributions
              </span>
              
              <div className="space-y-1.5">
                {alert.explanation?.contributions?.map((c) => (
                  <div key={c.signal} className="text-xs">
                    <div className="flex justify-between text-[11px] mb-0.5">
                      <span className="text-slate-700 font-medium">{c.signal}</span>
                      <span className="font-mono text-blue-600 font-bold">{(c.score * 100).toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          c.score >= 0.7 ? 'bg-red-500' : (c.score >= 0.4 ? 'bg-amber-500' : 'bg-emerald-500')
                        }`}
                        style={{ width: `${Math.max(5, Math.min(100, c.score * 100))}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>

        </div>

      </div>

      {/* Interleaved Activity Timeline */}
      <div className="glass-panel p-5 rounded-xl border border-slate-200 bg-white shadow-sm space-y-4">
        
        <div className="flex items-center justify-between border-b border-slate-200 pb-3">
          <div className="flex items-center space-x-3">
            <Clock className="w-4 h-4 text-blue-600" />
            <h2 className="text-sm font-bold text-slate-900">
              Forensic Activity Chronology (Access Telemetry & Transfers Interleaved)
            </h2>
          </div>

          {timelineData?.insider_touch && (
            <div className="px-3 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-200 text-xs font-mono font-bold flex items-center space-x-1.5 animate-pulse">
              <Sparkles className="w-3.5 h-3.5 text-purple-600" />
              <span>{timelineData.insider_touch.label}</span>
            </div>
          )}
        </div>

        {/* Timeline Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-mono text-[10px] uppercase border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-3">Time (UTC)</th>
                <th className="py-2.5 px-3">Stream Type</th>
                <th className="py-2.5 px-3">Event Action</th>
                <th className="py-2.5 px-3">Actor &rarr; Subject</th>
                <th className="py-2.5 px-3">Value / Detail</th>
                <th className="py-2.5 px-3">Forensic Signature</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-sans">
              {timelineData?.timeline?.map((item, idx) => {
                const isCurrentReplay = (replayStep === idx);
                const isAccess = item.event_type === 'ACCESS';

                return (
                  <tr 
                    key={item.id} 
                    className={`transition-colors ${
                      isCurrentReplay 
                        ? 'bg-blue-50 border-l-4 border-blue-600' 
                        : (item.is_cycle ? 'bg-red-50/40' : 'hover:bg-slate-50')
                    }`}
                  >
                    <td className="py-2.5 px-3 font-mono text-slate-600">
                      {item.time_display}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                        isAccess 
                          ? 'bg-purple-50 text-purple-700 border border-purple-200' 
                          : 'bg-red-50 text-red-700 border border-red-200'
                      }`}>
                        {item.event_type}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-semibold text-slate-900">
                      {item.action}
                    </td>
                    <td className="py-2.5 px-3 text-slate-700">
                      {item.actor_name} &rarr; {isAccess ? maskValue(item.target_name, 'name') : maskValue(item.target_name, 'name')}
                    </td>
                    <td className="py-2.5 px-3 font-mono">
                      {item.amount_display ? (
                        <span className="text-red-600 font-bold">{item.amount_display}</span>
                      ) : (
                        <span className="text-slate-500 text-[11px]">{item.details}</span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-[11px]">
                      {item.is_unauthorized && (
                        <span className="text-red-600 font-semibold">Unauthorized Cross-Branch</span>
                      )}
                      {item.is_cycle && (
                        <span className="text-red-600 font-semibold">Circular Leg</span>
                      )}
                      {item.is_structured && (
                        <span className="text-amber-600 ml-1 font-medium">Structured (&lt;50k)</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

      </div>

      {/* Case Management & Evidence Box */}
      {caseData && (
        <div className="glass-panel p-5 rounded-xl border border-slate-200 bg-white shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-200 pb-3">
            <div>
              <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <FileText className="w-4 h-4 text-blue-600" />
                <span>Case Management & Investigator Chain of Custody</span>
              </h2>
              <p className="text-[11px] text-slate-500">Formal investigation file: {caseData.id}</p>
            </div>

            {/* Status & Investigator Controls */}
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center space-x-1.5 text-xs">
                <span className="text-slate-600 font-medium">Status:</span>
                <select
                  id="case-status-select"
                  value={statusVal}
                  onChange={(e) => handleStatusChange(e.target.value)}
                  className="bg-white border border-slate-200 text-slate-900 rounded px-2.5 py-1 text-xs focus:outline-none focus:border-blue-500 shadow-sm"
                >
                  <option value="Open">Open</option>
                  <option value="In Review">In Review</option>
                  <option value="Escalated">Escalated</option>
                  <option value="Closed">Closed</option>
                </select>
              </div>

              <div className="flex items-center space-x-1.5 text-xs">
                <span className="text-slate-600 font-medium">Investigator:</span>
                <select
                  id="case-investigator-select"
                  value={investigatorVal}
                  onChange={(e) => handleInvestigatorChange(e.target.value)}
                  className="bg-white border border-slate-200 text-slate-900 rounded px-2.5 py-1 text-xs focus:outline-none focus:border-blue-500 shadow-sm"
                >
                  <option value="Sarah Chen">Sarah Chen (Senior Investigator)</option>
                  <option value="Vikram Patel">Vikram Patel (Fraud Specialist)</option>
                  <option value="Elena Rostova">Elena Rostova (AML Lead)</option>
                  <option value="Unassigned">Unassigned</option>
                </select>
              </div>
            </div>
          </div>

          {/* Notes Thread */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            
            {/* Existing Notes List */}
            <div className="space-y-2">
              <span className="text-xs font-bold text-slate-900 block">
                Investigator Notes & Findings ({caseData.notes?.length || 0})
              </span>
              
              <div className="max-h-48 overflow-y-auto space-y-2 pr-1">
                {caseData.notes?.length === 0 ? (
                  <p className="text-xs text-slate-500 italic p-3 rounded bg-slate-50 border border-slate-200">
                    No notes recorded yet. Add findings below.
                  </p>
                ) : (
                  caseData.notes?.map((n) => (
                    <div key={n.id} className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs space-y-1">
                      <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                        <span className="font-bold text-blue-600">{n.author}</span>
                        <span>{new Date(n.timestamp).toLocaleTimeString()} UTC</span>
                      </div>
                      <p className="text-slate-800">{n.note_text}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Append Note Input */}
            <form onSubmit={handleAddNote} className="space-y-2">
              <span className="text-xs font-bold text-slate-900 block">
                Add Investigative Finding
              </span>
              <textarea
                id="case-note-textarea"
                rows={3}
                placeholder="Record supervisory observations, interview remarks, or SAR filing references..."
                value={noteInput}
                onChange={(e) => setNoteInput(e.target.value)}
                className="w-full p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 resize-none font-sans"
              />
              <button
                type="submit"
                id="submit-case-note-btn"
                disabled={submittingNote || !noteInput.trim()}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold disabled:opacity-50 transition-colors shadow-sm"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{submittingNote ? 'Saving...' : 'Append Note'}</span>
              </button>
            </form>

          </div>

        </div>
      )}

    </div>
  );
}
