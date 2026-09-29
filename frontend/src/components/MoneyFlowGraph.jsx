import React, { useState } from 'react';
import { User, Landmark, ArrowRight, Clock, ShieldAlert, Sparkles, RefreshCw } from 'lucide-react';
import { useRole } from '../context/RoleContext';

export default function MoneyFlowGraph({ 
  graphData, 
  activeStep = null, 
  highlightCycle = true 
}) {
  const { maskValue } = useRole();
  const [hoveredNode, setHoveredNode] = useState(null);
  const [hoveredEdge, setHoveredEdge] = useState(null);

  if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
    return (
      <div className="h-96 flex items-center justify-center text-slate-500 font-mono text-sm glass-panel rounded-xl">
        Loading topology graph...
      </div>
    );
  }

  // Pre-configured coordinates for clean circular & insider layout
  const nodePositions = {
    'E102': { x: 100, y: 140 },
    'C417': { x: 270, y: 140 },
    'C208': { x: 490, y: 140 },
    'C731': { x: 380, y: 310 },
  };

  // Helper to fallback positions for any additional nodes
  const getNodePos = (node, index) => {
    if (nodePositions[node.id]) return nodePositions[node.id];
    // Dynamic circle positioning
    const angle = (index / Math.max(1, graphData.nodes.length)) * 2 * Math.PI;
    return {
      x: 350 + 170 * Math.cos(angle),
      y: 220 + 110 * Math.sin(angle)
    };
  };

  // Step-based visibility for Case Replay
  const isEdgeVisibleInReplay = (edge, index) => {
    if (activeStep === null) return true;
    return index <= activeStep;
  };

  const isEdgeCurrentInReplay = (edge, index) => {
    return activeStep !== null && index === activeStep;
  };

  return (
    <div className="relative w-full h-[430px] bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
      
      {/* Graph Header Legend */}
      <div className="absolute top-3 left-4 z-10 flex items-center space-x-3 text-xs bg-white/95 px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm backdrop-blur-sm">
        <div className="flex items-center space-x-1.5 text-purple-700 font-medium">
          <span className="w-2.5 h-2.5 rounded-full bg-purple-600" />
          <span>Insider Touch</span>
        </div>
        <div className="flex items-center space-x-1.5 text-red-700 font-medium">
          <span className="w-2.5 h-2.5 rounded-full bg-red-600 animate-pulse" />
          <span>Circular Layering</span>
        </div>
        <div className="flex items-center space-x-1.5 text-blue-700 font-medium">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
          <span>Customer Account</span>
        </div>
      </div>

      {/* SVG Canvas */}
      <svg 
        className="w-full h-full"
        viewBox="0 0 620 400"
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          {/* Arrow markers */}
          <marker
            id="arrow-red"
            viewBox="0 0 10 10"
            refX="22"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#DC2626" />
          </marker>
          <marker
            id="arrow-purple"
            viewBox="0 0 10 10"
            refX="22"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#7C3AED" />
          </marker>
          <marker
            id="arrow-cyan"
            viewBox="0 0 10 10"
            refX="22"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563EB" />
          </marker>

          {/* Glow filter */}
          <filter id="glow-edge" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* 1. Render Edges */}
        {graphData.edges.map((edge, idx) => {
          const sNode = graphData.nodes.find(n => n.id === edge.source);
          const tNode = graphData.nodes.find(n => n.id === edge.target);
          if (!sNode || !tNode) return null;

          const sPos = getNodePos(sNode, graphData.nodes.indexOf(sNode));
          const tPos = getNodePos(tNode, graphData.nodes.indexOf(tNode));

          const isAccess = edge.type === 'ACCESS';
          const isCycle = edge.is_suspicious_cycle;
          const isVisible = isEdgeVisibleInReplay(edge, idx);
          const isCurrent = isEdgeCurrentInReplay(edge, idx);

          // Calculate midpoint for edge labels
          const midX = (sPos.x + tPos.x) / 2;
          const midY = (sPos.y + tPos.y) / 2;

          let strokeColor = isAccess ? '#7C3AED' : (isCycle ? '#DC2626' : '#2563EB');
          let markerId = isAccess ? 'url(#arrow-purple)' : (isCycle ? 'url(#arrow-red)' : 'url(#arrow-cyan)');

          if (!isVisible) {
            strokeColor = '#CBD5E1';
            markerId = '';
          }

          return (
            <g 
              key={edge.id || idx} 
              className={`transition-opacity duration-500 cursor-pointer ${isVisible ? 'opacity-100' : 'opacity-20'}`}
              onMouseEnter={() => setHoveredEdge(edge)}
              onMouseLeave={() => setHoveredEdge(null)}
            >
              {/* Main Line */}
              <line
                x1={sPos.x}
                y1={sPos.y}
                x2={tPos.x}
                y2={tPos.y}
                stroke={strokeColor}
                strokeWidth={isCurrent ? 4 : (isCycle ? 3 : 2)}
                strokeDasharray={isAccess ? "6,4" : (isCurrent ? "4,2" : "none")}
                markerEnd={markerId}
                filter={isCycle && isVisible ? "url(#glow-edge)" : undefined}
                className={isCurrent ? "animate-pulse" : ""}
              />

              {/* Edge Label Badge */}
              {isVisible && (
                <g transform={`translate(${midX}, ${midY})`}>
                  <rect
                    x="-40"
                    y="-12"
                    width="80"
                    height="20"
                    rx="10"
                    fill={isAccess ? "#F3E8FF" : (isCycle ? "#FEE2E2" : "#EFF6FF")}
                    stroke={strokeColor}
                    strokeWidth="1"
                    className="shadow-sm"
                  />
                  <text
                    x="0"
                    y="2"
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fill={isAccess ? "#6B21A8" : (isCycle ? "#991B1B" : "#1E40AF")}
                    fontSize="9"
                    fontFamily="monospace"
                    fontWeight="bold"
                  >
                    {isAccess ? edge.label.substring(0, 10) : `₹${(edge.amount / 1000).toFixed(1)}k`}
                  </text>
                </g>
              )}
            </g>
          );
        })}

        {/* 2. Render Nodes */}
        {graphData.nodes.map((node, idx) => {
          const pos = getNodePos(node, idx);
          const isEmployee = node.type === 'EMPLOYEE';
          const isTarget = node.is_target;
          const isHovered = hoveredNode?.id === node.id;

          let ringColor = isEmployee ? '#7C3AED' : (isTarget ? '#DC2626' : '#2563EB');
          let bgColor = isEmployee ? '#F3E8FF' : (isTarget ? '#FEE2E2' : '#EFF6FF');

          return (
            <g
              key={node.id}
              transform={`translate(${pos.x}, ${pos.y})`}
              className="cursor-pointer group"
              onMouseEnter={() => setHoveredNode(node)}
              onMouseLeave={() => setHoveredNode(null)}
            >
              {/* Outer pulsing ring for hero target */}
              {isTarget && (
                <circle
                  r="30"
                  fill="none"
                  stroke="#DC2626"
                  strokeWidth="1.5"
                  opacity="0.3"
                  className="animate-ping"
                />
              )}

              {/* Node Circle */}
              <circle
                r="22"
                fill={bgColor}
                stroke={ringColor}
                strokeWidth={isHovered ? 3 : 2}
                className="transition-transform duration-200 group-hover:scale-110 shadow-sm"
              />

              {/* Node Icon */}
              {isEmployee ? (
                <User x="-9" y="-9" width="18" height="18" className="text-purple-700 pointer-events-none" />
              ) : (
                <Landmark x="-9" y="-9" width="18" height="18" className={isTarget ? "text-red-700 pointer-events-none" : "text-blue-700 pointer-events-none"} />
              )}

              {/* Node Label Below */}
              <text
                x="0"
                y="36"
                textAnchor="middle"
                fill="#0F172A"
                fontSize="11"
                fontWeight="600"
                className="select-none"
              >
                {node.id}
              </text>
              <text
                x="0"
                y="48"
                textAnchor="middle"
                fill="#64748B"
                fontSize="9"
                className="select-none"
              >
                {isEmployee ? node.role : maskValue(node.label?.split(' ')[0], 'name')}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Hover Tooltip Overlay */}
      {hoveredNode && (
        <div className="absolute bottom-3 left-4 z-20 bg-white/95 border border-slate-200 p-3 rounded-lg shadow-xl max-w-xs text-xs pointer-events-none">
          <div className="flex items-center space-x-2 font-bold text-slate-900 mb-1">
            {hoveredNode.type === 'EMPLOYEE' ? <User className="w-4 h-4 text-purple-600" /> : <Landmark className="w-4 h-4 text-blue-600" />}
            <span>{hoveredNode.id}: {maskValue(hoveredNode.label, 'name')}</span>
          </div>
          <div className="text-slate-600 space-y-0.5">
            <div><b>Type:</b> {hoveredNode.type}</div>
            <div><b>Branch:</b> {hoveredNode.branch || 'Pune/Mumbai'}</div>
            {hoveredNode.role && <div><b>Role:</b> {hoveredNode.role}</div>}
            {hoveredNode.risk_rating && <div><b>Risk Rating:</b> {hoveredNode.risk_rating}</div>}
          </div>
        </div>
      )}

      {hoveredEdge && (
        <div className="absolute bottom-3 right-4 z-20 bg-white/95 border border-slate-200 p-3 rounded-lg shadow-xl max-w-xs text-xs pointer-events-none">
          <div className="flex items-center space-x-2 font-bold text-slate-900 mb-1">
            <ArrowRight className="w-4 h-4 text-red-600" />
            <span>{hoveredEdge.source} &rarr; {hoveredEdge.target}</span>
          </div>
          <div className="text-slate-600 space-y-0.5">
            <div><b>Type:</b> {hoveredEdge.type}</div>
            {hoveredEdge.amount && <div><b>Amount:</b> ₹{hoveredEdge.amount.toLocaleString()}</div>}
            {hoveredEdge.channel && <div><b>Channel:</b> {hoveredEdge.channel}</div>}
            <div><b>Timestamp:</b> {hoveredEdge.time_str || hoveredEdge.timestamp}</div>
            {hoveredEdge.description && <div><b>Note:</b> {hoveredEdge.description}</div>}
          </div>
        </div>
      )}

    </div>
  );
}
