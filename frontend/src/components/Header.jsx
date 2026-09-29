import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  ShieldAlert, 
  LayoutDashboard, 
  ListFilter, 
  Eye, 
  EyeOff, 
  Activity, 
  Users, 
  Sliders, 
  Radio
} from 'lucide-react';
import { useRole } from '../context/RoleContext';

export default function Header() {
  const { currentRole, setCurrentRole, isMasked } = useRole();

  const navLinks = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/alerts', label: 'Alert Queue', icon: ListFilter },
    { to: '/alerts/ALT_1001', label: 'Hero Case (E102)', icon: ShieldAlert, badge: 'HERO' },
    { to: '/employees', label: 'Role-DNA Profiler', icon: Users },
    { to: '/metrics', label: 'Shield & Accuracy', icon: Activity },
    { to: '/simulator', label: 'Simulator', icon: Sliders },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-md shadow-blue-500/20">
            <ShieldAlert className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight text-slate-900 font-sans">
                Zenith<span className="text-blue-600">Guard</span>
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-semibold">
                FIN-04
              </span>
            </div>
            <p className="text-[11px] text-slate-500 hidden sm:block">
              Financial Crime & Insider Risk Intelligence
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center space-x-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.to}
                to={link.to}
                id={`nav-${link.label.toLowerCase().replace(/[^a-z0-9]/g, '-')}`}
                className={({ isActive }) => `
                  flex items-center space-x-1.5 px-3 py-2 rounded-md text-xs font-medium transition-all
                  ${isActive 
                    ? 'bg-blue-50 text-blue-600 font-semibold border border-blue-200' 
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'}
                `}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{link.label}</span>
                {link.badge && (
                  <span className="text-[9px] px-1.5 py-0.2 rounded-full bg-red-100 text-red-700 font-mono font-semibold animate-pulse border border-red-200">
                    {link.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Right Action: Role Switcher & Engine Status */}
        <div className="flex items-center space-x-3">
          
          {/* Live Engine Indicator */}
          <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-mono font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Detection: Active</span>
          </div>

          {/* Role Masking Switcher */}
          <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-slate-200">
            <button
              id="role-analyst-btn"
              onClick={() => setCurrentRole('Analyst')}
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded text-xs transition-colors ${
                currentRole === 'Analyst'
                  ? 'bg-blue-600 text-white font-medium shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              title="Masks customer names and sensitive identifiers"
            >
              <EyeOff className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Analyst (Masked)</span>
            </button>

            <button
              id="role-investigator-btn"
              onClick={() => setCurrentRole('Investigator')}
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded text-xs transition-colors ${
                currentRole === 'Investigator'
                  ? 'bg-blue-600 text-white font-medium shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              title="Unmasked full view for authorized investigators"
            >
              <Eye className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Investigator</span>
            </button>
          </div>

        </div>

      </div>
    </header>
  );
}
