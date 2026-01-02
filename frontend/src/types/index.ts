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

export interface Intervention {
    name: string;
    reason: string;
}

export interface KrrResult {
    session_id: string;
    summary: string;
    explanations: string[];
    ranked_concerns: string[];
    escalation_guidance: string;
    disclaimer: string;
    audit_ref: string;
    detected_symptoms?: string[];
    detected_emotions?: string[];
    detected_triggers?: string[];
    recommended_interventions?: Intervention[];
}
