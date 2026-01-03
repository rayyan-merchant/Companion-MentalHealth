import { useState, useCallback } from 'react';
import { Message, KrrResult } from '../types';
import { runKrrPipeline } from '../api/client';

function generateId(): string {
    return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function generateSessionId(): string {
    return `sess-${Date.now()}`;
}

export function useSession() {
    const [sessionId] = useState(() => generateSessionId());
    const [messages, setMessages] = useState<Message[]>([]);

    // Symbolic Result State
    const [krrResult, setKrrResult] = useState<KrrResult | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const sendUserMessage = useCallback(async (text: string) => {
        const userMessageId = generateId();
        const userMessage: Message = {
            id: userMessageId,
            sender: 'user',
            text,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);

        try {
            // Execute KRR Pipeline
            const response = await runKrrPipeline({
                session_id: sessionId,
                student_id: 'student_web_user', // Default ID for web interface
                text: text
            });

            // Update symbolic state
            setKrrResult(response);

            // Construct Bot Reply from Hybrid Output
            const replyText = response.response;

            const botMessage: Message = {
                id: generateId(),
                sender: 'bot',
                text: replyText,
                timestamp: new Date().toISOString(),
                metadata: {
                    confidence: response.confidence === 'high' ? 0.9 : response.confidence === 'medium' ? 0.6 : 0.3,
                    state: response.state,
                    action: response.action,
                    evidence: {
                        emotions: response.evidence.emotions,
                        symptoms: response.evidence.symptoms,
                        triggers: response.evidence.triggers
                    },
                    clarificationQuestions: response.follow_up_questions,
                    disclaimer: response.disclaimer
                }
            };

            setMessages(prev => [...prev, botMessage]);

        } catch (error) {
            const errorMessage: Message = {
                id: generateId(),
                sender: 'system',
                text: 'System Error: Unable to process request. ' + (error instanceof Error ? error.message : ''),
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    }, [sessionId]);

    const clearSession = useCallback(() => {
        setMessages([]);
        setKrrResult(null);
    }, []);

    return {
        sessionId,
        messages,
        krrResult, // Expose full symbolic result for side panel
        isLoading,
        sendUserMessage,
        clearSession
    };
}

