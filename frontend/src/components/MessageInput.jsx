import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Image as ImageIcon, Globe, Database, X, Paperclip } from 'lucide-react';

export default function MessageInput({
  onSendMessage,
  disabled,
  useRag,
  setUseRag,
  useWebSearch,
  setUseWebSearch,
  onOpenDocuments,
}) {
  const [text, setText] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);

  // Initialize Speech Recognition if supported
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map((result) => result[0].transcript)
          .join('');
        setText(transcript);
      };

      recognition.onerror = () => setIsListening(false);
      recognition.onend = () => setIsListening(false);

      recognitionRef.current = recognition;
    }
  }, []);

  const handleToggleMic = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err) {
        console.error(err);
      }
    }
  };

  const handleImageSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('Please select an image file (PNG, JPG, WEBP).');
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      setSelectedImage(reader.result);
    };
    reader.readAsDataURL(file);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSubmit = (e) => {
    e?.preventDefault();
    const trimmed = text.trim();
    if (!trimmed && !selectedImage) return;
    if (disabled) return;

    onSendMessage({
      message: trimmed || 'What do you see in this image?',
      imageData: selectedImage,
    });

    setText('');
    setSelectedImage(null);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleTextChange = (e) => {
    setText(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 140)}px`;
  };

  return (
    <div className="p-3 sm:p-4 border-t border-slate-800/80 glass">
      <div className="max-w-4xl mx-auto space-y-2.5">
        {/* Multimodal Image Preview */}
        {selectedImage && (
          <div className="relative inline-block">
            <img
              src={selectedImage}
              alt="Attached preview"
              className="w-20 h-20 object-cover rounded-xl border border-purple-500/40 shadow-lg"
            />
            <button
              onClick={() => setSelectedImage(null)}
              className="absolute -top-1.5 -right-1.5 p-1 rounded-full bg-slate-900 border border-slate-700 text-slate-300 hover:text-white hover:bg-rose-600 transition-colors"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        )}

        {/* Input box */}
        <div className="relative rounded-2xl glass-card border border-slate-700/80 focus-within:border-purple-500/70 focus-within:ring-2 focus-within:ring-purple-500/20 transition-all p-2 flex items-end gap-2">
          {/* Hidden image input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            className="hidden"
          />

          {/* Action buttons (Left) */}
          <div className="flex items-center gap-1 pb-1 text-slate-400">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="p-1.5 rounded-lg hover:text-purple-300 hover:bg-slate-800/80 transition-colors"
              title="Attach an image for vision analysis"
            >
              <ImageIcon className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={onOpenDocuments}
              className="p-1.5 rounded-lg hover:text-purple-300 hover:bg-slate-800/80 transition-colors"
              title="Attach / View Knowledge Base Documents"
            >
              <Paperclip className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={handleToggleMic}
              className={`p-1.5 rounded-lg transition-all ${
                isListening
                  ? 'bg-rose-500 text-white animate-pulse shadow-lg shadow-rose-500/30'
                  : 'hover:text-purple-300 hover:bg-slate-800/80'
              }`}
              title={isListening ? 'Stop listening' : 'Speak your message (Voice Input)'}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>
          </div>

          {/* Text Area */}
          <textarea
            ref={textareaRef}
            rows={1}
            value={text}
            onChange={handleTextChange}
            onKeyDown={handleKeyDown}
            placeholder={isListening ? 'Listening with empathy...' : 'Share what is on your mind... (Shift+Enter for new line)'}
            disabled={disabled}
            className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-sm focus:outline-none resize-none py-1.5 px-2 max-h-36"
          />

          {/* Send Button */}
          <button
            type="button"
            onClick={handleSubmit}
            disabled={disabled || (!text.trim() && !selectedImage)}
            className={`p-2 rounded-xl flex-shrink-0 transition-all ${
              !disabled && (text.trim() || selectedImage)
                ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg shadow-purple-600/30 hover:scale-105 active:scale-95'
                : 'bg-slate-800 text-slate-600 cursor-not-allowed'
            }`}
            title="Send Message"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

        {/* Intelligence Controls / Feature Toggles */}
        <div className="flex items-center justify-between px-1 text-[11px] text-slate-400">
          <div className="flex items-center gap-2">
            {/* RAG Memory Toggle */}
            <button
              type="button"
              onClick={() => setUseRag(!useRag)}
              className={`px-2.5 py-1 rounded-full border transition-all flex items-center gap-1.5 ${
                useRag
                  ? 'bg-purple-900/40 border-purple-500/40 text-purple-200'
                  : 'bg-slate-900/40 border-slate-800 text-slate-500 hover:text-slate-400'
              }`}
            >
              <Database className="w-3 h-3 text-purple-400" />
              <span>Knowledge Base (RAG): {useRag ? 'ON' : 'OFF'}</span>
            </button>

            {/* Live Web Search Toggle */}
            <button
              type="button"
              onClick={() => setUseWebSearch(!useWebSearch)}
              className={`px-2.5 py-1 rounded-full border transition-all flex items-center gap-1.5 ${
                useWebSearch
                  ? 'bg-cyan-950/50 border-cyan-500/40 text-cyan-200'
                  : 'bg-slate-900/40 border-slate-800 text-slate-500 hover:text-slate-400'
              }`}
            >
              <Globe className="w-3 h-3 text-cyan-400" />
              <span>Web Search: {useWebSearch ? 'ON' : 'OFF'}</span>
            </button>
          </div>

          <span className="hidden sm:inline text-slate-500 text-[10px]">
            SoulSync AI • Safe & Empathetic
          </span>
        </div>
      </div>
    </div>
  );
}

