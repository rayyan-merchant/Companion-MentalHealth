/**
 * Session API client for the Mental Health Companion application.
 */

const API_BASE = '/api';

// Get token from localStorage
function getAuthToken(): string | null {
    return localStorage.getItem('companion_auth_token');
}

// Helper to make authenticated requests
async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const token = getAuthToken();

    const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('companion_auth_token');
        localStorage.removeItem('companion_user');
        window.location.href = '/login';
        throw new Error('Session expired. Please log in again.');
    }

    return response;
}

// ============================================================================
// Types
// ============================================================================

export interface SessionMessage {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: string;
    metadata?: {
        state?: string;
        confidence?: string;
        action?: string;
        evidence?: {
            emotions: string[];
            symptoms: string[];
            triggers: string[];
        };
        follow_up_questions?: string[];
        disclaimer?: string;
    };
}

export interface Session {
    session_id: string;
    user_id: string;
    title: string;
    created_at: string;
    updated_at: string;
    messages: SessionMessage[];
    inferred_states: string[];
    risk_level: 'low' | 'medium' | 'high';
}

export interface SessionSummary {
    session_id: string;
    user_id: string;
    title: string;
    created_at: string;
    updated_at: string;
    message_count: number;
    risk_level: 'low' | 'medium' | 'high';
    last_message_preview?: string;
}

export interface SendMessageResponse {
    user_message_id: string;
    assistant_message_id: string;
    session_id: string;
    response: string;
    state?: string;
    confidence?: string;
    action?: string;
    evidence?: {
        emotions: string[];
        symptoms: string[];
        triggers: string[];
        intensity?: string;
        temporal?: string;
    };
    follow_up_questions?: string[];
    disclaimer?: string;
}

export interface SessionStats {
    total_sessions: number;
    risk_distribution: {
        low: number;
        medium: number;
        high: number;
    };
    top_symptoms: Array<{
        name: string;
        count: number;
    }>;
    total_messages: number;
}


// ============================================================================
// API Functions
// ============================================================================

/**
 * Get session statistics for the dashboard
 */
export async function getSessionStats(): Promise<SessionStats> {
    const response = await authFetch(`${API_BASE}/sessions/stats`);

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Failed to fetch session stats');
    }

    return response.json();
}

/**
 * Get all sessions for the current user
 */
export async function getSessions(): Promise<SessionSummary[]> {
    const response = await authFetch(`${API_BASE}/sessions`);

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Failed to fetch sessions');
    }

    return response.json();
}

/**
 * Get a specific session with full messages
 */
export async function getSession(sessionId: string): Promise<Session> {
    const response = await authFetch(`${API_BASE}/sessions/${sessionId}`);

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Failed to fetch session');
    }

    return response.json();
}

/**
 * Create a new session
 */
export async function createSession(title?: string): Promise<Session> {
    const response = await authFetch(`${API_BASE}/sessions`, {
        method: 'POST',
        body: JSON.stringify({ title })
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Failed to create session');
    }

    return response.json();
}

/**
 * Send a message to a session and get AI response
 */
export async function sendMessage(sessionId: string, text: string): Promise<SendMessageResponse> {
    const response = await authFetch(`${API_BASE}/sessions/${sessionId}/message`, {
        method: 'POST',
        body: JSON.stringify({ text })
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Failed to send message');
    }

    return response.json();
}

/**
 * Delete a session (soft delete)
 */
export async function deleteSession(sessionId: string): Promise<void> {
    const response = await authFetch(`${API_BASE}/sessions/${sessionId}`, {
        method: 'DELETE'
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Failed to delete session');
    }
}
