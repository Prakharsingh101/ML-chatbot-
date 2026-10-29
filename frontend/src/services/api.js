/**
 * SoulSync API Service Client
 */
const API_BASE = import.meta.env.VITE_API_URL || '';

/**
 * Send chat message and receive AI response
 */
export async function sendChatMessage({
  message,
  conversationId = null,
  useRag = true,
  useWebSearch = false,
  imageData = null,
}) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      use_rag: useRag,
      use_web_search: useWebSearch,
      image_data: imageData,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error (${res.status})`);
  }

  return res.json();
}

/**
 * List all past conversation sessions
 */
export async function fetchConversations(limit = 50, offset = 0) {
  const res = await fetch(`${API_BASE}/conversations?limit=${limit}&offset=${offset}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch conversations (${res.status})`);
  }
  return res.json();
}

/**
 * Get details & full history of a specific conversation
 */
export async function fetchConversationDetails(conversationId) {
  const res = await fetch(`${API_BASE}/conversations/${conversationId}`);
  if (!res.ok) {
    throw new Error(`Failed to load conversation (${res.status})`);
  }
  return res.json();
}

/**
 * Delete a conversation
 */
export async function deleteConversation(conversationId) {
  const res = await fetch(`${API_BASE}/conversations/${conversationId}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error(`Failed to delete conversation (${res.status})`);
  }
  return res.json();
}

/**
 * List uploaded documents
 */
export async function fetchDocuments() {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) {
    throw new Error(`Failed to load documents (${res.status})`);
  }
  return res.json();
}

/**
 * Upload a document (PDF, TXT, MD, DOCX) for RAG indexing
 */
export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to upload file (${res.status})`);
  }

  return res.json();
}

/**
 * Delete a document from the RAG knowledge base
 */
export async function deleteDocument(documentId) {
  const res = await fetch(`${API_BASE}/documents/${documentId}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error(`Failed to delete document (${res.status})`);
  }
  return res.json();
}

/**
 * Fetch backend health status
 */
export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) {
    throw new Error(`Health check failed (${res.status})`);
  }
  return res.json();
}

