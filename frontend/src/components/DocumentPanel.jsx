import React, { useState, useRef } from 'react';
import { X, UploadCloud, FileText, Trash2, CheckCircle2, AlertCircle, Loader2, Sparkles } from 'lucide-react';
import { uploadDocument, deleteDocument } from '../services/api';

export default function DocumentPanel({
  isOpen,
  onClose,
  documents,
  onRefreshDocuments,
}) {
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setErrorMessage('');

    try {
      await uploadDocument(file);
      await onRefreshDocuments();
    } catch (err) {
      setErrorMessage(err.message || 'Failed to upload document');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (docId) => {
    if (!confirm('Remove this document from the AI knowledge base?')) return;
    try {
      await deleteDocument(docId);
      await onRefreshDocuments();
    } catch (err) {
      alert(err.message || 'Failed to delete document');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/70 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-md h-full glass flex flex-col border-l border-slate-800 shadow-2xl">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-semibold text-sm text-slate-100">Knowledge Base & RAG</h2>
              <p className="text-[11px] text-slate-400">Contextual memory & documents</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Upload Zone */}
        <div className="p-4 border-b border-slate-800/80">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,.md,.markdown,.docx"
            onChange={handleFileUpload}
            className="hidden"
          />

          <div
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition-all ${
              isUploading
                ? 'border-purple-500 bg-purple-500/10'
                : 'border-slate-700 hover:border-purple-500 hover:bg-slate-800/40'
            }`}
          >
            {isUploading ? (
              <div className="flex flex-col items-center gap-2 text-purple-300">
                <Loader2 className="w-6 h-6 animate-spin text-purple-400" />
                <span className="text-xs font-medium">Extracting text & generating vector embeddings...</span>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2 text-slate-400">
                <UploadCloud className="w-7 h-7 text-purple-400" />
                <div>
                  <span className="text-xs font-medium text-slate-200">Click to upload document</span>
                  <p className="text-[10px] text-slate-400 mt-0.5">PDF, Markdown, TXT, DOCX (Max 10MB)</p>
                </div>
              </div>
            )}
          </div>

          {errorMessage && (
            <div className="mt-2.5 p-2 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          <div className="mt-3 flex items-start gap-2 text-[11px] text-slate-400 bg-slate-900/50 p-2.5 rounded-lg border border-slate-800">
            <Sparkles className="w-4 h-4 text-purple-400 flex-shrink-0 mt-0.5" />
            <span>
              Files uploaded here are chunked and converted into vector embeddings (`pgvector`). SoulSync retrieves these passages during conversations to ground its answers.
            </span>
          </div>
        </div>

        {/* Document List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Uploaded Files ({documents.length})
          </div>

          {documents.length === 0 ? (
            <div className="text-center py-10 text-slate-500 text-xs italic">
              No documents added yet. Upload files to provide custom knowledge to SoulSync.
            </div>
          ) : (
            documents.map((doc) => (
              <div
                key={doc.id}
                className="glass-card p-3 rounded-xl flex items-center justify-between text-xs transition-all hover:border-slate-600"
              >
                <div className="flex items-center gap-2.5 min-w-0 pr-2">
                  <div className="w-8 h-8 rounded-lg bg-purple-950/60 border border-purple-800/40 flex items-center justify-center text-purple-300 flex-shrink-0">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <p className="font-medium text-slate-200 truncate">{doc.filename}</p>
                    <div className="flex items-center gap-2 text-[10px] text-slate-400 mt-0.5">
                      <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                      <span>•</span>
                      <span className="flex items-center gap-1 text-emerald-400">
                        <CheckCircle2 className="w-3 h-3" />
                        {doc.chunk_count} Chunks
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(doc.id)}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-800 transition-colors"
                  title="Delete document"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

