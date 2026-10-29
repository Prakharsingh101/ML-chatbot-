import React, { useState, useEffect } from 'react';
import { Menu, Sparkles, BookOpen, AlertCircle, Heart } from 'lucide-react';
import ConversationSidebar from './components/ConversationSidebar';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';
import DocumentPanel from './components/DocumentPanel';
import EmotionalStatus from './components/EmotionalStatus';
import {
  sendChatMessage,
  fetchConversations,
  fetchConversationDetails,
  deleteConversation,
  fetchDocuments,
  fetchHealth,
} from './services/api';

export default function App() {
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isThinking, setIsThinking] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Knowledge base / RAG state
  const [documents, setDocuments] = useState([]);
  const [isDocPanelOpen, setIsDocPanelOpen] = useState(false);
  const [useRag, setUseRag] = useState(true);
  const [useWebSearch, setUseWebSearch] = useState(false);

  // Emotional mood state
  const [selectedMood, setSelectedMood] = useState(null);

  // Mobile sidebar state
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Load initial data on mount
  useEffect(() => {
    loadConversations();
    loadDocuments();
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      await fetchHealth();
    } catch (err) {
      console.warn('Backend server not reachable yet:', err);
    }
  };

  const loadConversations = async () => {
    try {
      const data = await fetchConversations();
      setConversations(data);
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  const loadDocuments = async () => {
    try {
      const data = await fetchDocuments();
      setDocuments(data);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  const handleSelectConversation = async (conversationId) => {
    setIsSidebarOpen(false);
    setActiveConversationId(conversationId);
    setErrorMessage('');
    try {
      const details = await fetchConversationDetails(conversationId);
      setMessages(details.messages || []);
    } catch (err) {
      setErrorMessage(err.message || 'Could not load conversation history.');
    }
  };

  const handleNewChat = () => {
    setIsSidebarOpen(false);
    setActiveConversationId(null);
    setMessages([]);
    setErrorMessage('');
  };

  const handleDeleteConversation = async (conversationId) => {
    try {
      await deleteConversation(conversationId);
      if (activeConversationId === conversationId) {
        handleNewChat();
      }
      await loadConversations();
    } catch (err) {
      setErrorMessage(err.message || 'Failed to delete conversation.');
    }
  };

  const handleSendMessage = async ({ message, imageData }) => {
    setErrorMessage('');

    // Prepend user mood context if selected for emotional empathy
    let contextualMessage = message;
    if (selectedMood && !messages.length) {
      contextualMessage = `[Current Emotional State: Feeling ${selectedMood.label}]\n${message}`;
    }

    // Optimistically add user message to UI
    const tempUserMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: message,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMessage]);
    setIsThinking(true);

    try {
      const response = await sendChatMessage({
        message: contextualMessage,
        conversationId: activeConversationId,
        useRag,
        useWebSearch,
        imageData,
      });

      // Update active conversation ID if this was a new thread
      if (!activeConversationId && response.conversation_id) {
        setActiveConversationId(response.conversation_id);
        await loadConversations();
      }

      // Add assistant response to messages
      setMessages((prev) => [...prev, response.message]);
    } catch (err) {
      setErrorMessage(err.message || 'Failed to receive an AI response. Please try again.');
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100">
      {/* Sidebar */}
      <ConversationSidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        onDeleteConversation={handleDeleteConversation}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        onOpenDocuments={() => setIsDocPanelOpen(true)}
        documentCount={documents.length}
      />

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col min-w-0 h-full relative">
        {/* Top Navbar */}
        <header className="h-14 px-4 border-b border-slate-800/80 glass flex items-center justify-between z-10 flex-shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="md:hidden p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800"
              title="Open Navigation"
            >
              <Menu className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2">
              <span className="font-semibold text-sm text-slate-100">
                {activeConversationId
                  ? conversations.find((c) => c.id === activeConversationId)?.title || 'Companion Chat'
                  : 'New Conversation'}
              </span>
            </div>
          </div>

          {/* Emotional Status Indicator & Companion Mood */}
          <div className="flex items-center gap-2">
            <EmotionalStatus
              selectedMood={selectedMood}
              onSelectMood={setSelectedMood}
              isThinking={isThinking}
            />

            <button
              onClick={() => setIsDocPanelOpen(true)}
              className="p-2 rounded-full glass border border-slate-700/60 text-slate-400 hover:text-purple-300 transition-colors"
              title="Knowledge Base & Notes"
            >
              <BookOpen className="w-4 h-4" />
            </button>
          </div>
        </header>

        {/* Global Error Banner */}
        {errorMessage && (
          <div className="p-2.5 px-4 bg-rose-500/10 border-b border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage('')}
              className="text-xs hover:underline text-rose-400"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Chat message history stream */}
        <ChatWindow
          messages={messages}
          isThinking={isThinking}
          onSelectPrompt={(prompt) => handleSendMessage({ message: prompt })}
        />

        {/* Input bar */}
        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={isThinking}
          useRag={useRag}
          setUseRag={setUseRag}
          useWebSearch={useWebSearch}
          setUseWebSearch={setUseWebSearch}
          onOpenDocuments={() => setIsDocPanelOpen(true)}
        />
      </main>

      {/* RAG & Document Slide-Over */}
      <DocumentPanel
        isOpen={isDocPanelOpen}
        onClose={() => setIsDocPanelOpen(false)}
        documents={documents}
        onRefreshDocuments={loadDocuments}
      />
    </div>
  );
}

