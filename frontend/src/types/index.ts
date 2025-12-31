export interface Message {
    id: string;
    sender: 'user' | 'bot' | 'system';
    text: string;
    timestamp: string;
}

// Symbolic KRR Types
export interface SymbolicState {
    state: string; // e.g. "Academic Stress"
    // No numeric confidence
}

export interface KrrResult {
    session_id: string;
    summary: string;
    explanations: string[];
    ranked_concerns: string[];
    escalation_guidance: string;
    disclaimer: string;
    audit_ref: string;
}

// Legacy adapters for UI components if needed, or strictly use new types
// We will try to rely on KrrResult

