import React from 'react';
import { Plus, MessageSquare, Trash2, X, Sparkles, BookOpen } from 'lucide-react';

export default function ConversationSidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  isOpen,
  onClose,
  onOpenDocuments,
  documentCount = 0,
}) {
  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-40 md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed md:static inset-y-0 left-0 w-72 glass flex flex-col z-50 transition-transform duration-300 ease-in-out border-r border-slate-800 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Header */}
        <div className="p-4 flex items-center justify-between border-b border-slate-800/80">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-purple-500/20">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h1 className="font-semibold text-sm text-slate-100 tracking-tight">SoulSync</h1>
              <p className="text-[10px] text-purple-400 font-medium">Emotional AI Assistant</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="md:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Action Buttons */}
        <div className="p-3 space-y-2">
          <button
            onClick={onNewChat}
            className="w-full py-2.5 px-3.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-medium text-xs flex items-center justify-center gap-2 shadow-lg shadow-purple-600/20 transition-all hover:shadow-purple-600/30"
          >
            <Plus className="w-4 h-4" />
            <span>New Conversation</span>
          </button>

          <button
            onClick={onOpenDocuments}
            className="w-full py-2 px-3 rounded-xl border border-slate-700/80 bg-slate-800/40 hover:bg-slate-800 text-slate-300 hover:text-white text-xs flex items-center justify-between transition-colors"
          >
            <div className="flex items-center gap-2">
              <BookOpen className="w-3.5 h-3.5 text-purple-400" />
              <span>Knowledge Base & Notes</span>
            </div>
            {documentCount > 0 && (
              <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-purple-500/20 text-purple-300 font-medium">
                {documentCount}
              </span>
            )}
          </button>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          <div className="px-2 py-1 text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
            Recent Sessions
          </div>

          {conversations.length === 0 ? (
            <div className="p-4 text-center text-xs text-slate-500 italic">
              No previous conversations yet. Start a new heart-to-heart!
            </div>
          ) : (
            conversations.map((conv) => {
              const isActive = conv.id === activeConversationId;
              return (
                <div
                  key={conv.id}
                  onClick={() => onSelectConversation(conv.id)}
                  className={`group relative flex items-center justify-between px-3 py-2.5 rounded-xl text-xs cursor-pointer transition-all ${
                    isActive
                      ? 'bg-purple-900/40 text-purple-100 border border-purple-500/30 shadow-sm'
                      : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0 pr-2">
                    <MessageSquare
                      className={`w-3.5 h-3.5 flex-shrink-0 ${
                        isActive ? 'text-purple-400' : 'text-slate-500 group-hover:text-slate-400'
                      }`}
                    />
                    <span className="truncate font-medium">{conv.title}</span>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (confirm('Delete this conversation session?')) {
                        onDeleteConversation(conv.id);
                      }
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-slate-500 hover:text-rose-400 hover:bg-slate-700/60 transition-opacity"
                    title="Delete session"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>

        {/* Footer info */}
        <div className="p-3 border-t border-slate-800/80 text-[11px] text-slate-500 flex items-center justify-between">
          <span>SoulSync AI v0.1.0</span>
          <span className="flex items-center gap-1 text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Online
          </span>
        </div>
      </aside>
    </>
  );
}

