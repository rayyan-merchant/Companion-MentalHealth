import { apiFetch } from './client';

export interface InsightResponse {
    insight: string | null;
    status: 'ready' | 'generating';
}

export interface SessionMessage {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: string;
    metadata?: {
        state?: string;
        confidence?: string;
        action?: string;
        evidence?: { emotions: string[]; symptoms: string[]; triggers: string[] };
        reasoning_trace?: string[];
        follow_up_questions?: string[];
        disclaimer?: string;
        crisis_type?: 'suicidal_ideation' | 'self_harm' | 'harm_to_others' | 'medical_emergency';
        processing_ms?: number;
        used_fallback?: boolean;
        rules_fired?: string[];
        rule_version?: string;
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
    reasoning_trace?: string[];
    follow_up_questions?: string[];
    disclaimer?: string;
    crisis_type?: 'suicidal_ideation' | 'self_harm' | 'harm_to_others' | 'medical_emergency';
    processing_ms: number;
    used_fallback: boolean;
    rules_fired: string[];
    rule_version: string;
}

export interface SessionStats {
    total_sessions: number;
    risk_distribution: { low: number; medium: number; high: number };
    top_symptoms: Array<{ name: string; count: number }>;
    total_messages: number;
}

export const sessionKeys = {
    all: ['sessions'] as const,
    detail: (id: string) => ['sessions', id] as const,
    stats: ['session-stats'] as const,
    insight: ['dashboard-insight'] as const
};

export const getDashboardInsight = () =>
    apiFetch<InsightResponse>('/sessions/insight');
export const getSessionStats = () => apiFetch<SessionStats>('/sessions/stats');
export const getSessions = () => apiFetch<SessionSummary[]>('/sessions');
export const getSession = (sessionId: string) =>
    apiFetch<Session>(`/sessions/${encodeURIComponent(sessionId)}`);
export const createSession = (title?: string) =>
    apiFetch<Session>('/sessions', {
        method: 'POST',
        body: JSON.stringify({ title })
    });
export const sendMessage = (
    sessionId: string,
    text: string,
    clientMessageId: string
) => apiFetch<SendMessageResponse>(
    `/sessions/${encodeURIComponent(sessionId)}/message`,
    {
        method: 'POST',
        body: JSON.stringify({ text, client_message_id: clientMessageId })
    }
);
export const deleteSession = (sessionId: string) =>
    apiFetch<void>(`/sessions/${encodeURIComponent(sessionId)}`, {
        method: 'DELETE'
    });
