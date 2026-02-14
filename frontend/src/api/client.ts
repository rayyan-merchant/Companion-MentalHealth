const API_BASE = '/api';

export interface KrrRequest {
    session_id: string;
    student_id: string;
    text: string;
}

export interface KrrResponse {
    session_id: string;
    response: string;
    state: string;
    confidence: string;
    action: 'explain' | 'explain_cautious' | 'ask_clarification';
    evidence: {
        emotions: string[];
        symptoms: string[];
        triggers: string[];
        intensity: string;
        temporal?: string;
    };
    follow_up_questions: string[];
    disclaimer: string;
}

export interface ErrorResponse {
    error: string;
}

export async function runKrrPipeline(request: KrrRequest): Promise<KrrResponse> {
    const response = await fetch(`${API_BASE}/krr/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
    });

    if (!response.ok) {
        // Try to parse error message from backend
        try {
            const errData = await response.json();
            throw new Error(errData.detail || errData.error || 'Failed to process request');
        } catch (e) {
            // If parsing fails or generic error
            throw new Error(e instanceof Error ? e.message : 'Unknown error occurred');
        }
    }

    return response.json();
}

