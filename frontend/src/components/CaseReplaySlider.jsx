import React, { useEffect, useState } from 'react';
import { Play, Pause, RotateCcw, SkipBack, SkipForward, FastForward, Clock } from 'lucide-react';

export default function CaseReplaySlider({ 
  steps = [], 
  activeStep, 
  setActiveStep 
}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1); // 1x, 2x, 4x

  const totalSteps = steps.length;

  useEffect(() => {
    let timer;
    if (isPlaying && totalSteps > 0) {
      timer = setInterval(() => {
        setActiveStep((prev) => {
          if (prev === null || prev >= totalSteps - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1600 / speed);
    }
    return () => clearInterval(timer);
  }, [isPlaying, totalSteps, speed, setActiveStep]);

  if (!steps || steps.length === 0) return null;

  const currentEvent = activeStep !== null && steps[activeStep] ? steps[activeStep] : steps[0];

  const handlePlayToggle = () => {
    if (activeStep === null || activeStep >= totalSteps - 1) {
      setActiveStep(0);
      setIsPlaying(true);
    } else {
      setIsPlaying(!isPlaying);
    }
  };

  const handleReset = () => {
    setIsPlaying(false);
    setActiveStep(null);
  };

  const handleStepForward = () => {
    setActiveStep((prev) => (prev === null ? 0 : Math.min(totalSteps - 1, prev + 1)));
  };

  const handleStepBack = () => {
    setActiveStep((prev) => (prev === null ? 0 : Math.max(0, prev - 1)));
  };

  return (
    <div className="glass-panel p-4 rounded-xl border border-slate-200 bg-white shadow-sm space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Clock className="w-4 h-4 text-blue-600" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-900">
            Case Chronology Replay Studio
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-semibold">
            {activeStep === null ? 'All Events Shown' : `Step ${activeStep + 1} of ${totalSteps}`}
          </span>
        </div>

        {/* Speed Toggles */}
        <div className="flex items-center space-x-1 bg-slate-100 px-2 py-0.5 rounded-lg border border-slate-200 text-[10px] font-mono text-slate-700">
          <span>Speed:</span>
          {[1, 2, 4].map((s) => (
            <button
              key={s}
              onClick={() => setSpeed(s)}
              className={`px-1.5 py-0.5 rounded transition-colors ${speed === s ? 'bg-blue-600 text-white font-bold' : 'text-slate-600 hover:text-slate-900'}`}
            >
              {s}x
            </button>
          ))}
        </div>
      </div>

      {/* Current Step Description Card */}
      {currentEvent && (
        <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-3">
            <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
              currentEvent.event_type === 'ACCESS' ? 'bg-purple-50 text-purple-700 border border-purple-200' : 'bg-red-50 text-red-700 border border-red-200'
            }`}>
              {currentEvent.time_display} UTC
            </span>
            <span className="font-semibold text-slate-900">
              {currentEvent.action}
            </span>
            <span className="text-slate-600 hidden sm:inline">
              ({currentEvent.actor_name} &rarr; {currentEvent.target_name})
            </span>
          </div>

          {currentEvent.amount_display && (
            <span className="font-mono font-bold text-red-600">
              {currentEvent.amount_display}
            </span>
          )}
        </div>
      )}

      {/* Scrubbing Slider */}
      <div className="space-y-1">
        <input
          type="range"
          min="0"
          max={totalSteps - 1}
          value={activeStep === null ? totalSteps - 1 : activeStep}
          onChange={(e) => {
            setIsPlaying(false);
            setActiveStep(parseInt(e.target.value, 10));
          }}
          className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
        />
        <div className="flex justify-between text-[10px] font-mono text-slate-500">
          <span>{steps[0]?.time_display || 'Start'}</span>
          <span>Timeline Progression</span>
          <span>{steps[totalSteps - 1]?.time_display || 'End'}</span>
        </div>
      </div>

      {/* Controls Bar */}
      <div className="flex items-center justify-center space-x-2 pt-1">
        <button
          onClick={handleReset}
          className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 transition-colors text-xs flex items-center space-x-1"
          title="Show Full Graph (Reset)"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span className="text-[11px] hidden sm:inline font-medium">Show All</span>
        </button>

        <button
          onClick={handleStepBack}
          disabled={activeStep === 0}
          className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 disabled:opacity-40 transition-colors"
          title="Previous Event"
        >
          <SkipBack className="w-3.5 h-3.5" />
        </button>

        <button
          onClick={handlePlayToggle}
          className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs shadow-sm flex items-center space-x-1.5 transition-all"
        >
          {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
          <span>{isPlaying ? 'Pause Replay' : 'Play Incident'}</span>
        </button>

        <button
          onClick={handleStepForward}
          disabled={activeStep !== null && activeStep >= totalSteps - 1}
          className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 disabled:opacity-40 transition-colors"
          title="Next Event"
        >
          <SkipForward className="w-3.5 h-3.5" />
        </button>
      </div>

    </div>
  );
}
