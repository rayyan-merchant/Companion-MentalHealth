import { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { AlertCircle, Brain, Plus, RotateCcw } from 'lucide-react';
import { ChatShell } from '../components/chat/ChatShell';
import { Composer } from '../components/chat/Composer';
import { QuickPrompts } from '../components/chat/QuickPrompts';
import { ExplanationPanel } from '../components/explanation/ExplanationPanel';
import { CrisisAlert } from '../components/chat/CrisisAlert';
import { useAuth } from '../context/AuthContext';
import { KrrResult, Message, MessageMetadata } from '../types';
import {
    createSession,
    deleteSession,
    getSession,
    sendMessage,
    sessionKeys,
    Session
} from '../api/sessions';

function clientMessageId(): string {
    if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
    return `message-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function toMessages(session: Session): Message[] {
    return session.messages.map((message) => ({
        id: message.id,
        sender: message.role === 'assistant' ? 'bot' : message.role,
        text: message.content,
        timestamp: message.timestamp,
        metadata: message.metadata ? {
            confidence: message.metadata.confidence === 'high' ? 0.9
                : message.metadata.confidence === 'medium' ? 0.6 : 0.3,
            state: message.metadata.state,
            action: message.metadata.action as MessageMetadata['action'],
            evidence: message.metadata.evidence,
            clarificationQuestions: message.metadata.follow_up_questions,
            disclaimer: message.metadata.disclaimer,
            crisisType: message.metadata.crisis_type
        } : undefined
    }));
}

function latestResult(session: Session): KrrResult | null {
    const message = [...session.messages].reverse().find((item) => item.role === 'assistant');
    if (!message?.metadata) return null;
    return {
        session_id: session.session_id,
        response: message.content,
        state: message.metadata.state || '',
        confidence: message.metadata.confidence || 'low',
        action: (message.metadata.action || 'ask_clarification') as KrrResult['action'],
        evidence: {
            emotions: message.metadata.evidence?.emotions || [],
            symptoms: message.metadata.evidence?.symptoms || [],
            triggers: message.metadata.evidence?.triggers || [],
            intensity: 'medium'
        },
        reasoning_trace: message.metadata.reasoning_trace || [],
        follow_up_questions: message.metadata.follow_up_questions || [],
        disclaimer: message.metadata.disclaimer || '',
        crisis_type: message.metadata.crisis_type
    };
}

export function Chat() {
    const { sessionId } = useParams<{ sessionId?: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const { user } = useAuth();
    const promptKey = `companion:suggestions-dismissed:${user?.user_id || 'anonymous'}`;

    const [currentSession, setCurrentSession] = useState<Session | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [krrResult, setKrrResult] = useState<KrrResult | null>(null);
    const [isInitializing, setIsInitializing] = useState(true);
    const [isSending, setIsSending] = useState(false);
    const [waitingLonger, setWaitingLonger] = useState(false);
    const [loadError, setLoadError] = useState<string | null>(null);
    const [sendError, setSendError] = useState<string | null>(null);
    const [retryPayload, setRetryPayload] = useState<{ text: string; id: string } | null>(null);
    const [explanationOpen, setExplanationOpen] = useState(false);
    const [showSuggestions, setShowSuggestions] = useState(
        () => localStorage.getItem(promptKey) !== 'true'
    );

    useEffect(() => {
        setShowSuggestions(localStorage.getItem(promptKey) !== 'true');
    }, [promptKey]);

    useEffect(() => {
        let active = true;
        async function initialize() {
            setIsInitializing(true);
            setLoadError(null);
            try {
                if (!sessionId) {
                    if (!active) return;
                    setCurrentSession(null);
                    setMessages([]);
                    setKrrResult(null);
                    return;
                }
                const session = await queryClient.fetchQuery({
                    queryKey: sessionKeys.detail(sessionId),
                    queryFn: () => getSession(sessionId),
                    staleTime: 5 * 60 * 1000
                });
                if (!active) return;
                setCurrentSession(session);
                setMessages(toMessages(session));
                setKrrResult(latestResult(session));
            } catch (reason) {
                if (active) {
                    setLoadError(reason instanceof Error ? reason.message : 'Failed to load conversation');
                }
            } finally {
                if (active) setIsInitializing(false);
            }
        }
        initialize();
        return () => { active = false; };
    }, [navigate, queryClient, sessionId]);

    useEffect(() => {
        if (!isSending) {
            setWaitingLonger(false);
            return;
        }
        const timer = window.setTimeout(() => setWaitingLonger(true), 4000);
        return () => window.clearTimeout(timer);
    }, [isSending]);

    const sendUserMessage = useCallback(async (
        text: string,
        id = clientMessageId(),
        optimistic = true
    ) => {
        if (isSending) return;
        setIsSending(true);
        setSendError(null);
        try {
            let session = currentSession;
            let createdSession = false;
            if (!session) {
                session = await createSession();
                createdSession = true;
                setCurrentSession(session);
                queryClient.invalidateQueries({ queryKey: sessionKeys.all });
            }
            if (optimistic) {
                setMessages((previous) => [...previous, {
                    id,
                    sender: 'user',
                    text,
                    timestamp: new Date().toISOString()
                }]);
            }
            setShowSuggestions(false);
            const response = await sendMessage(session.session_id, text, id);
            const result: KrrResult = {
                session_id: response.session_id,
                response: response.response,
                state: response.state || '',
                confidence: response.confidence || 'low',
                action: (response.action || 'ask_clarification') as KrrResult['action'],
                evidence: {
                    emotions: response.evidence?.emotions || [],
                    symptoms: response.evidence?.symptoms || [],
                    triggers: response.evidence?.triggers || [],
                    intensity: response.evidence?.intensity || 'medium',
                    temporal: response.evidence?.temporal
                },
                follow_up_questions: response.follow_up_questions || [],
                disclaimer: response.disclaimer || '',
                reasoning_trace: response.reasoning_trace || [],
                crisis_type: response.crisis_type
            };
            setKrrResult(result);
            setMessages((previous) => [...previous, {
                id: response.assistant_message_id,
                sender: 'bot',
                text: response.response,
                timestamp: new Date().toISOString(),
                metadata: {
                    confidence: response.confidence === 'high' ? 0.9
                        : response.confidence === 'medium' ? 0.6 : 0.3,
                    state: response.state,
                    action: response.action as MessageMetadata['action'],
                    evidence: {
                        emotions: response.evidence?.emotions || [],
                        symptoms: response.evidence?.symptoms || [],
                        triggers: response.evidence?.triggers || []
                    },
                    clarificationQuestions: response.follow_up_questions,
                    disclaimer: response.disclaimer,
                    crisisType: response.crisis_type
                }
            }]);
            setRetryPayload(null);
            queryClient.invalidateQueries({ queryKey: sessionKeys.all });
            queryClient.invalidateQueries({ queryKey: sessionKeys.detail(session.session_id) });
            queryClient.invalidateQueries({ queryKey: sessionKeys.stats });
            if (!sessionId) {
                navigate(`/chat/${session.session_id}`, { replace: true });
            }
        } catch (reason) {
            setSendError(reason instanceof Error ? reason.message : 'Unable to get a response');
            setRetryPayload({ text, id });
            if (createdSession) {
                try {
                    await deleteSession(session.session_id);
                    queryClient.invalidateQueries({ queryKey: sessionKeys.all });
                    queryClient.invalidateQueries({ queryKey: sessionKeys.stats });
                } catch {
                    // Ignore cleanup errors; empty sessions are filtered out server-side.
                }
            }
        } finally {
            setIsSending(false);
        }
    }, [currentSession, isSending, navigate, queryClient, sessionId]);

    async function newSession() {
        setCurrentSession(null);
        setMessages([]);
        setKrrResult(null);
        setSendError(null);
        setRetryPayload(null);
        navigate('/chat', { replace: true });
    }

    function dismissSuggestions() {
        localStorage.setItem(promptKey, 'true');
        setShowSuggestions(false);
    }

    function restoreSuggestions() {
        localStorage.removeItem(promptKey);
        setShowSuggestions(true);
    }

    if (isInitializing) {
        return (
            <div className="h-full p-4 md:p-6 space-y-5" aria-label="Loading conversation">
                <div className="h-8 w-48 rounded bg-slate-200 animate-pulse" />
                <div className="h-20 max-w-lg rounded-2xl bg-white animate-pulse" />
                <div className="h-16 max-w-md ml-auto rounded-2xl bg-primary/10 animate-pulse" />
                <div className="h-20 max-w-lg rounded-2xl bg-white animate-pulse" />
            </div>
        );
    }

    if (loadError) {
        return (
            <div className="h-full grid place-items-center p-6 text-center">
                <div>
                    <AlertCircle className="text-error mx-auto mb-3" size={40} />
                    <p className="text-error mb-4">{loadError || 'Conversation unavailable'}</p>
                    <button className="btn-primary" onClick={() => navigate('/chat')}>
                        Start a new conversation
                    </button>
                </div>
            </div>
        );
    }

    if (!currentSession) {
        return (
            <div className="flex h-full min-w-0 overflow-hidden">
                <section className="flex-1 flex flex-col min-w-0 max-w-full">
                    <div className="px-4 py-2 border-b border-gray-100 flex items-center justify-between bg-white/80">
                        <h2 className="font-medium truncate min-w-0">New conversation</h2>
                        <button onClick={newSession}
                            className="flex items-center gap-1 text-sm text-primary hover:bg-primary/10 px-3 py-1.5 rounded-lg">
                            <Plus size={16} /> Reset
                        </button>
                    </div>

                    <ChatShell
                        messages={messages}
                        isLoading={isSending}
                        loadingLabel={waitingLonger ? 'Still working...' : 'Companion is thinking...'}
                    />

                    {showSuggestions && messages.length === 0 ? (
                        <QuickPrompts onSelect={sendUserMessage} onClose={dismissSuggestions} />
                    ) : (
                        !showSuggestions && messages.length === 0 && (
                            <button onClick={restoreSuggestions}
                                className="mx-4 mb-2 self-start text-xs text-primary hover:underline">
                                Show suggested messages
                            </button>
                        )
                    )}

                    <Composer onSend={sendUserMessage} disabled={isSending} placeholder="Start a new conversation..." />
                </section>

                <aside className="hidden lg:block w-80 xl:w-96 min-w-0 border-l border-gray-100 bg-background overflow-y-auto p-4 space-y-4">
                    <ExplanationPanel krrResult={krrResult} />
                </aside>

                {explanationOpen && (
                    <div className="fixed inset-0 z-50 lg:hidden">
                        <button className="absolute inset-0 bg-black/30" aria-label="Close explanation"
                            onClick={() => setExplanationOpen(false)} />
                        <aside className="absolute inset-y-0 right-0 w-[min(92vw,24rem)] bg-background p-4 overflow-y-auto shadow-xl">
                            <button onClick={() => setExplanationOpen(false)}
                                className="mb-3 text-sm text-primary">Close explanation</button>
                            <ExplanationPanel krrResult={krrResult} />
                        </aside>
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className="flex h-full min-w-0 overflow-hidden">
            <section className="flex-1 flex flex-col min-w-0 max-w-full">
                <div className="px-4 py-2 border-b border-gray-100 flex items-center justify-between bg-white/80">
                    <h2 className="font-medium truncate min-w-0">{currentSession.title}</h2>
                    <div className="flex items-center gap-1">
                        <button onClick={() => setExplanationOpen(true)}
                            className="lg:hidden p-2 text-primary rounded-lg hover:bg-primary/10"
                            aria-label="Open response explanation">
                            <Brain size={18} />
                        </button>
                        <button onClick={newSession}
                            className="flex items-center gap-1 text-sm text-primary hover:bg-primary/10 px-3 py-1.5 rounded-lg">
                            <Plus size={16} /> New
                        </button>
                    </div>
                </div>

                <ChatShell
                    messages={messages}
                    isLoading={isSending}
                    loadingLabel={waitingLonger ? 'Still working...' : 'Companion is thinking...'}
                />

                {krrResult?.action === 'crisis_intervention' && (
                    <div className="px-4"><CrisisAlert type={krrResult.crisis_type} /></div>
                )}
                {sendError && retryPayload && (
                    <div role="alert" className="mx-4 mb-2 p-3 rounded-xl bg-error/10 text-error text-sm flex items-center gap-3">
                        <span className="flex-1">{sendError}</span>
                        <button className="font-medium flex items-center gap-1"
                            onClick={() => sendUserMessage(retryPayload.text, retryPayload.id, false)}>
                            <RotateCcw size={14} /> Retry
                        </button>
                    </div>
                )}
                {showSuggestions && messages.length === 0 ? (
                    <QuickPrompts onSelect={sendUserMessage} onClose={dismissSuggestions} />
                ) : (
                    !showSuggestions && messages.length === 0 && (
                        <button onClick={restoreSuggestions}
                            className="mx-4 mb-2 self-start text-xs text-primary hover:underline">
                            Show suggested messages
                        </button>
                    )
                )}
                <Composer onSend={sendUserMessage} disabled={isSending} />
            </section>

            <aside className="hidden lg:block w-80 xl:w-96 min-w-0 border-l border-gray-100 bg-background overflow-y-auto p-4 space-y-4">
                <ExplanationPanel krrResult={krrResult} />
            </aside>

            {explanationOpen && (
                <div className="fixed inset-0 z-50 lg:hidden">
                    <button className="absolute inset-0 bg-black/30" aria-label="Close explanation"
                        onClick={() => setExplanationOpen(false)} />
                    <aside className="absolute inset-y-0 right-0 w-[min(92vw,24rem)] bg-background p-4 overflow-y-auto shadow-xl">
                        <button onClick={() => setExplanationOpen(false)}
                            className="mb-3 text-sm text-primary">Close explanation</button>
                        <ExplanationPanel krrResult={krrResult} />
                    </aside>
                </div>
            )}
        </div>
    );
}
