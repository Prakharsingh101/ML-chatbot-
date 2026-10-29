import React, { useState } from 'react';
import { Heart, Sparkles, Smile, CloudRain, Sun, Compass } from 'lucide-react';

const MOODS = [
  { id: 'calm', label: 'Peaceful', icon: Sun, color: 'text-amber-400 border-amber-500/30 bg-amber-500/10' },
  { id: 'reflective', label: 'Reflective', icon: Compass, color: 'text-purple-400 border-purple-500/30 bg-purple-500/10' },
  { id: 'overwhelmed', label: 'Overwhelmed', icon: CloudRain, color: 'text-blue-400 border-blue-500/30 bg-blue-500/10' },
  { id: 'seeking-clarity', label: 'Seeking Clarity', icon: Sparkles, color: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10' },
];

export default function EmotionalStatus({ selectedMood, onSelectMood, isThinking }) {
  const [showMoodPicker, setShowMoodPicker] = useState(false);

  return (
    <div className="flex items-center gap-3 px-3 py-1.5 rounded-full glass border border-purple-500/20 shadow-sm text-xs">
      {/* SoulSync Glowing Companion Avatar */}
      <div className="relative flex items-center justify-center">
        <div
          className={`w-6 h-6 rounded-full bg-gradient-to-tr from-purple-600 via-indigo-500 to-pink-500 flex items-center justify-center text-white shadow-md transition-all duration-500 ${
            isThinking ? 'animate-spin scale-110 shadow-purple-500/50' : 'animate-float'
          }`}
        >
          <Heart className="w-3.5 h-3.5 fill-white/80" />
        </div>
        <span
          className={`absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full border border-slate-900 ${
            isThinking ? 'bg-amber-400 animate-ping' : 'bg-emerald-400'
          }`}
        />
      </div>

      <div className="hidden sm:flex flex-col">
        <span className="font-medium text-slate-200 leading-tight">SoulSync</span>
        <span className="text-[10px] text-purple-300/80 leading-none">
          {isThinking ? 'Reflecting with empathy...' : 'Here for you'}
        </span>
      </div>

      {/* Mood Badge / Selector */}
      <div className="relative">
        <button
          onClick={() => setShowMoodPicker(!showMoodPicker)}
          className={`px-2.5 py-0.5 rounded-full border transition-all flex items-center gap-1.5 ${
            selectedMood ? selectedMood.color : 'text-slate-400 border-slate-700 bg-slate-800/60 hover:text-slate-200'
          }`}
          title="Set your emotional state for more tailored companionship"
        >
          <Smile className="w-3 h-3" />
          <span className="font-normal">{selectedMood ? selectedMood.label : 'My Mood'}</span>
        </button>

        {showMoodPicker && (
          <div className="absolute right-0 mt-2 w-44 rounded-xl glass-card p-1.5 shadow-2xl z-50 border border-slate-700">
            <div className="px-2 py-1 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
              How are you feeling?
            </div>
            {MOODS.map((m) => {
              const Icon = m.icon;
              return (
                <button
                  key={m.id}
                  onClick={() => {
                    onSelectMood(m);
                    setShowMoodPicker(false);
                  }}
                  className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left text-xs transition-colors hover:bg-slate-800 ${
                    selectedMood?.id === m.id ? 'bg-purple-900/40 text-purple-200' : 'text-slate-300'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{m.label}</span>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

