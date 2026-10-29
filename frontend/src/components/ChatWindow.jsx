import React, { useRef, useEffect, useState } from 'react';
import { Bot, User, Copy, Check, Heart, Sparkles, MessageCircleHeart } from 'lucide-react';
import AudioPlayer from './AudioPlayer';

const STARTER_PROMPTS = [
  { icon: '🌿', title: 'Grounding Exercise', prompt: 'I feel a bit overwhelmed right now. Can you guide me through a calming 2-minute breathing exercise?' },
  { icon: '💭', title: 'Unpack My Thoughts', prompt: "I've had a lot going on today and would like a safe, compassionate space to talk through it." },
  { icon: '📄', title: 'Consult My Notes', prompt: 'Can you summarize the core points from my uploaded knowledge base documents?' },
  { icon: '✨', title: 'Positive Affirmation', prompt: 'Could you share an uplifting perspective or gentle affirmation for today?' },
];

export default function ChatWindow({
  messages,
  isThinking,
  onSelectPrompt,
}) {
  const scrollRef = useRef(null);
  const [copiedId, setCopiedId] = useState(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isThinking]);

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
      {/* Empty State */}
      {messages.length === 0 && (
        <div className="max-w-2xl mx-auto py-8 text-center space-y-6">
          <div className="w-16 h-16 mx-auto rounded-3xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-pink-500 p-0.5 shadow-xl shadow-purple-600/20">
            <div className="w-full h-full bg-slate-950 rounded-[22px] flex items-center justify-center">
              <Heart className="w-8 h-8 text-purple-400 fill-purple-400/30 animate-pulse-subtle" />
            </div>
          </div>

          <div className="space-y-2">
            <h2 className="text-xl sm:text-2xl font-bold text-slate-100 tracking-tight">
              Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-300 to-indigo-300">SoulSync</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 max-w-md mx-auto leading-relaxed">
              Your safe, non-judgmental AI companion. Talk through what's on your mind, explore grounding strategies, or reference your uploaded documents.
            </p>
          </div>

          {/* Quick Starters */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-4 text-left">
            {STARTER_PROMPTS.map((starter, i) => (
              <button
                key={i}
                onClick={() => onSelectPrompt(starter.prompt)}
                className="glass-card p-3.5 rounded-2xl hover:border-purple-500/50 hover:bg-slate-800/60 transition-all text-xs group"
              >
                <div className="flex items-center gap-2 font-medium text-slate-200 group-hover:text-purple-300 transition-colors">
                  <span className="text-base">{starter.icon}</span>
                  <span>{starter.title}</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                  {starter.prompt}
                </p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Message Stream */}
      {messages.map((msg, index) => {
        const isUser = msg.role === 'user';
        return (
          <div
            key={msg.id || index}
            className={`flex items-start gap-3 max-w-3xl ${
              isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'
            }`}
          >
            {/* Avatar */}
            <div
              className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 text-xs shadow-md ${
                isUser
                  ? 'bg-gradient-to-tr from-indigo-500 to-purple-600 text-white'
                  : 'bg-slate-800 border border-purple-500/30 text-purple-300'
              }`}
            >
              {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            {/* Message Bubble */}
            <div
              className={`relative group rounded-2xl px-4 py-3 text-sm leading-relaxed max-w-[85%] sm:max-w-[78%] transition-all ${
                isUser
                  ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-tr-sm shadow-lg shadow-purple-600/10'
                  : 'glass-card border border-slate-700/70 text-slate-200 rounded-tl-sm'
              }`}
            >
              {/* Message text with basic markdown/whitespace formatting */}
              <div className="whitespace-pre-wrap break-words text-[13px] sm:text-sm">
                {msg.content}
              </div>

              {/* Assistant Message Actions */}
              {!isUser && (
                <div className="mt-2.5 pt-2 border-t border-slate-700/50 flex items-center gap-2">
                  <AudioPlayer text={msg.content} />

                  <button
                    onClick={() => handleCopy(msg.id || index, msg.content)}
                    className="p-1.5 rounded-lg bg-slate-800/60 border border-slate-700/60 text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 transition-colors text-xs flex items-center gap-1"
                    title="Copy message"
                  >
                    {copiedId === (msg.id || index) ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-[11px] text-emerald-300">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span className="text-[11px]">Copy</span>
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          </div>
        );
      })}

      {/* Thinking Indicator */}
      {isThinking && (
        <div className="flex items-start gap-3 max-w-3xl mr-auto animate-pulse">
          <div className="w-8 h-8 rounded-xl bg-slate-800 border border-purple-500/30 text-purple-300 flex items-center justify-center flex-shrink-0">
            <Bot className="w-4 h-4" />
          </div>
          <div className="glass-card border border-purple-500/30 px-4 py-3 rounded-2xl rounded-tl-sm text-xs text-purple-300 flex items-center gap-2">
            <Sparkles className="w-4 h-4 animate-spin text-purple-400" />
            <span>SoulSync is listening and reflecting with empathy...</span>
          </div>
        </div>
      )}
    </div>
  );
}

