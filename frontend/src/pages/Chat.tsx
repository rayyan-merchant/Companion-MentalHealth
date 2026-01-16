import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChatShell } from '../components/chat/ChatShell';
import { Composer } from '../components/chat/Composer';
import { QuickPrompts } from '../components/chat/QuickPrompts';
import { ExplanationPanel } from '../components/explanation/ExplanationPanel';
import { Message, KrrResult } from '../types';
import { getSession, sendMessage, createSession, Session } from '../api/sessions';
import { Loader2, Plus, AlertCircle } from 'lucide-react';
import { CrisisAlert } from '../components/chat/CrisisAlert';

function generateId(): string {
    return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export function Chat() {
    const { sessionId } = useParams<{ sessionId?: string }>();
    const navigate = useNavigate();

    // Session state
    const [currentSession, setCurrentSession] = useState<Session | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [krrResult, setKrrResult] = useState<KrrResult | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isInitializing, setIsInitializing] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Initialize session
    useEffect(() => {
        initializeSession();
    }, [sessionId]);

    const initializeSession = async () => {
        setIsInitializing(true);
        setError(null);

        try {
            if (sessionId) {
                // Load existing session
                const session = await getSession(sessionId);
                setCurrentSession(session);

                // Convert session messages to our format
                const loadedMessages: Message[] = session.messages.map(msg => ({
                    id: msg.id,
                    sender: msg.role === 'assistant' ? 'bot' : msg.role as 'user' | 'system',
                    text: msg.content,
                    timestamp: msg.timestamp,
                    metadata: msg.metadata ? {
                        confidence: msg.metadata.confidence === 'high' ? 0.9 :
                            msg.metadata.confidence === 'medium' ? 0.6 : 0.3,
                        state: msg.metadata.state,
                        action: msg.metadata.action as any,
                        evidence: msg.metadata.evidence,
                        clarificationQuestions: msg.metadata.follow_up_questions,
                        disclaimer: msg.metadata.disclaimer
                    } : undefined
                }));

                setMessages(loadedMessages);

                // Set latest KRR result from last assistant message
                const lastAssistant = session.messages.filter(m => m.role === 'assistant').pop();
                if (lastAssistant?.metadata) {
                    setKrrResult({
                        session_id: session.session_id,
                        response: lastAssistant.content,
                        state: lastAssistant.metadata.state || '',
                        confidence: lastAssistant.metadata.confidence || 'low',
                        action: (lastAssistant.metadata.action || 'ask_clarification') as any,
                        evidence: {
                            emotions: lastAssistant.metadata.evidence?.emotions || [],
                            symptoms: lastAssistant.metadata.evidence?.symptoms || [],
                            triggers: lastAssistant.metadata.evidence?.triggers || [],
                            intensity: 'medium'
                        },
                        follow_up_questions: lastAssistant.metadata.follow_up_questions || [],
                        disclaimer: lastAssistant.metadata.disclaimer || ''
                    });
                }
            } else {
                // Create new session
                const newSession = await createSession();
                setCurrentSession(newSession);
                setMessages([]);
                setKrrResult(null);
                // Update URL to include session ID
                navigate(`/chat/${newSession.session_id}`, { replace: true });
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to initialize session');
        } finally {
            setIsInitializing(false);
        }
    };

    const sendUserMessage = useCallback(async (text: string) => {
        if (!currentSession) return;

        const userMessageId = generateId();
        const userMessage: Message = {
            id: userMessageId,
            sender: 'user',
            text,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);
        setError(null);

        try {
            // Send message through API
            const response = await sendMessage(currentSession.session_id, text);

            // Update KRR result
            setKrrResult({
                session_id: response.session_id,
                response: response.response,
                state: response.state || '',
                confidence: response.confidence || 'low',
                action: (response.action || 'ask_clarification') as any,
                evidence: {
                    emotions: response.evidence?.emotions || [],
                    symptoms: response.evidence?.symptoms || [],
                    triggers: response.evidence?.triggers || [],
                    intensity: response.evidence?.intensity || 'medium',
                    temporal: response.evidence?.temporal
                },
                follow_up_questions: response.follow_up_questions || [],
                disclaimer: response.disclaimer || '',
                reasoning_trace: response.reasoning_trace || []
            });

            // Add bot response to messages
            const botMessage: Message = {
                id: response.assistant_message_id,
                sender: 'bot',
                text: response.response,
                timestamp: new Date().toISOString(),
                metadata: {
                    confidence: response.confidence === 'high' ? 0.9 :
                        response.confidence === 'medium' ? 0.6 : 0.3,
                    state: response.state,
                    action: response.action as any,
                    evidence: {
                        emotions: response.evidence?.emotions || [],
                        symptoms: response.evidence?.symptoms || [],
                        triggers: response.evidence?.triggers || []
                    },
                    clarificationQuestions: response.follow_up_questions,
                    disclaimer: response.disclaimer
                }
            };

            setMessages(prev => [...prev, botMessage]);

        } catch (err) {
            const errorMessage: Message = {
                id: generateId(),
                sender: 'system',
                text: 'System Error: ' + (err instanceof Error ? err.message : 'Unable to process request'),
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    }, [currentSession]);

    const handleQuickPrompt = (text: string) => {
        sendUserMessage(text);
    };

    const handleNewSession = async () => {
        try {
            const newSession = await createSession();
            setCurrentSession(newSession);
            setMessages([]);
            setKrrResult(null);
            navigate(`/chat/${newSession.session_id}`, { replace: true });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create session');
        }
    };

    // Loading state
    if (isInitializing) {
        return (
            <div className="flex h-full items-center justify-center">
                <div className="text-center">
                    <Loader2 className="w-8 h-8 text-primary animate-spin mx-auto mb-4" />
                    <p className="text-slate-text/50">Loading conversation...</p>
                </div>
            </div>
        );
    }

    // Error state
    if (error && !currentSession) {
        return (
            <div className="flex h-full items-center justify-center">
                <div className="text-center max-w-md mx-auto p-6">
                    <AlertCircle className="w-12 h-12 text-error mx-auto mb-4" />
                    <p className="text-error mb-4">{error}</p>
                    <button
                        onClick={() => navigate('/chat')}
                        className="btn-primary"
                    >
                        Start New Conversation
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="flex h-full">
            <div className="flex-1 flex flex-col min-w-0">
                {/* Session Header */}
                <div className="px-4 py-2 border-b border-gray-100 flex items-center justify-between bg-white/50">
                    <div className="flex-1 min-w-0">
                        <h2 className="font-medium truncate">
                            {currentSession?.title || 'New Conversation'}
                        </h2>
                    </div>
                    <button
                        onClick={handleNewSession}
                        className="flex items-center gap-1 text-sm text-primary hover:bg-primary/10 px-3 py-1.5 rounded-lg transition-colors"
                    >
                        <Plus size={16} />
                        New
                    </button>
                </div>

                <ChatShell
                    messages={messages}
                    isLoading={isLoading}
                />

                {krrResult?.action === 'crisis_intervention' && (
                    <div className="px-4">
                        <CrisisAlert />
                    </div>
                )}

                <QuickPrompts onSelect={handleQuickPrompt} />
                <Composer onSend={sendUserMessage} disabled={isLoading} />
            </div>

            <aside className="hidden lg:block w-80 xl:w-96 border-l border-gray-100 bg-background overflow-y-auto p-4 pb-2 space-y-4">
                <ExplanationPanel krrResult={krrResult} />
            </aside>
        </div>
    );
}
