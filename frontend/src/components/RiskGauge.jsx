import React from 'react';

export default function RiskGauge({ score = 0, level = 'Low', size = 180 }) {
  // Semi-circle gauge (180 degrees)
  const radius = size * 0.4;
  const strokeWidth = size * 0.08;
  const center = size / 2;
  const circumference = Math.PI * radius; // half circle length

  // Clamp score
  const safeScore = Math.min(100, Math.max(0, score));
  const strokeDashoffset = circumference - (safeScore / 100) * circumference;

  let color = '#16A34A'; // green
  let glowClass = 'glow-emerald';
  let badgeBg = 'bg-emerald-50 text-emerald-700 border-emerald-200';

  if (safeScore >= 70) {
    color = '#DC2626'; // red
    glowClass = 'glow-red';
    badgeBg = 'bg-red-50 text-red-700 border-red-200';
  } else if (safeScore >= 40) {
    color = '#F59E0B'; // amber
    glowClass = 'glow-amber';
    badgeBg = 'bg-amber-50 text-amber-700 border-amber-200';
  }

  return (
    <div className="flex flex-col items-center justify-center relative">
      <svg width={size} height={size * 0.65} viewBox={`0 0 ${size} ${size * 0.65}`}>
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#16A34A" />
            <stop offset="50%" stopColor="#F59E0B" />
            <stop offset="100%" stopColor="#DC2626" />
          </linearGradient>
          <filter id="gaugeGlow">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Background Track */}
        <path
          d={`M ${center - radius} ${center} A ${radius} ${radius} 0 0 1 ${center + radius} ${center}`}
          fill="none"
          stroke="#E2E8F0"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Active Arc */}
        <path
          d={`M ${center - radius} ${center} A ${radius} ${radius} 0 0 1 ${center + radius} ${center}`}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          filter="url(#gaugeGlow)"
          className="transition-all duration-1000 ease-out"
        />
      </svg>

      {/* Numerical score & badge positioned in center */}
      <div className="absolute top-[35%] flex flex-col items-center">
        <div className="flex items-baseline space-x-1">
          <span className="text-3xl sm:text-4xl font-black tracking-tight text-slate-900 font-mono">
            {score.toFixed(0)}
          </span>
          <span className="text-xs text-slate-500 font-mono">/100</span>
        </div>

        <span className={`mt-1 px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold tracking-wider uppercase border shadow-sm ${badgeBg}`}>
          {level} Risk
        </span>
      </div>
    </div>
  );
}
