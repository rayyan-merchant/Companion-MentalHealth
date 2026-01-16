export interface MessageMetadata {
    confidence?: number;
    state?: string;
    action?: 'explain' | 'explain_cautious' | 'ask_clarification' | 'crisis_intervention';
    evidence?: {
        emotions: string[];
        symptoms: string[];
        triggers: string[];
    };
    clarificationQuestions?: string[];
    disclaimer?: string;
}

export interface Message {
    id: string;
    sender: 'user' | 'bot' | 'system';
    text: string;
    timestamp: string;
    metadata?: MessageMetadata;
}

// Symbolic KRR Types
export interface SymbolicState {
    state: string; // e.g. "Academic Stress"
    // No numeric confidence
}

export interface Intervention {
    name: string;
    reason: string;
}

export interface KrrResult {
    session_id: string;
    response: string;
    state: string;
    confidence: string;
    action: 'explain' | 'explain_cautious' | 'ask_clarification' | 'crisis_intervention';
    evidence: {
        emotions: string[];
        symptoms: string[];
        triggers: string[];
        intensity: string;
        temporal?: string;
    };
    reasoning_trace?: string[];
    follow_up_questions: string[];
    disclaimer: string;
}
