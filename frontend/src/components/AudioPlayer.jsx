import React, { useState, useEffect } from 'react';
import { Volume2, VolumeX, Pause, Play, Sparkles } from 'lucide-react';

export default function AudioPlayer({ text }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      setIsSupported(true);
    }
  }, []);

  const handleToggleSpeak = () => {
    if (!isSupported || !text) return;

    if (isPlaying) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
      return;
    }

    window.speechSynthesis.cancel(); // Stop any pending speech

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95; // Gentle, empathetic pacing
    utterance.pitch = 1.0;

    // Pick a gentle sounding voice if available
    const voices = window.speechSynthesis.getVoices();
    const gentleVoice = voices.find(
      (v) => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha') || v.name.includes('Karen'))
    );
    if (gentleVoice) {
      utterance.voice = gentleVoice;
    }

    utterance.onend = () => setIsPlaying(false);
    utterance.onerror = () => setIsPlaying(false);

    window.speechSynthesis.speak(utterance);
    setIsPlaying(true);
  };

  if (!isSupported) return null;

  return (
    <button
      onClick={handleToggleSpeak}
      className={`p-1.5 rounded-lg border transition-all text-xs flex items-center gap-1.5 ${
        isPlaying
          ? 'bg-purple-600/30 border-purple-500/50 text-purple-200'
          : 'bg-slate-800/60 border-slate-700/60 text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
      }`}
      title={isPlaying ? 'Pause spoken response' : 'Listen with soothing voice synthesis'}
    >
      {isPlaying ? (
        <>
          <Pause className="w-3.5 h-3.5 text-purple-400 animate-pulse" />
          <span className="text-[11px]">Speaking...</span>
        </>
      ) : (
        <>
          <Volume2 className="w-3.5 h-3.5" />
          <span className="text-[11px]">Listen</span>
        </>
      )}
    </button>
  );
}

