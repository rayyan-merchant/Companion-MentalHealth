import { motion } from 'framer-motion';
import { Message } from '../../types';

interface MessageItemProps {
    message: Message;
    onSelect?: (id: string) => void;
}

// Evidence pill component
function EvidencePill({ label, items }: { label: string; items: string[] }) {
    if (!items || items.length === 0) return null;

    return (
        <div className="flex flex-wrap gap-1 items-center">
            <span className="text-xs text-slate-text/60">{label}:</span>
            {items.map((item, i) => (
                <span
                    key={i}
                    className="px-2 py-0.5 text-xs bg-primary/10 text-primary rounded-full"
                >
                    {item}
                </span>
            ))}
        </div>
    );
}

// Clarification section component
function ClarificationSection({ questions }: { questions: string[] }) {
    if (!questions || questions.length === 0) return null;

    return (
        <div className="mt-3 pt-3 border-t border-slate-border/30">
            <p className="text-xs text-slate-text/60 mb-1">To better understand:</p>
            {questions.map((q, i) => (
                <p key={i} className="text-sm text-primary/80 italic">"{q}"</p>
            ))}
        </div>
    );
}

// Confidence indicator (symbolic, not numeric)
function ConfidenceIndicator({ action }: { action?: string }) {
    if (!action) return null;

    const labels: Record<string, { text: string; className: string }> = {
        'explain': { text: 'I understand', className: 'bg-emerald-100 text-emerald-700' },
        'explain_cautious': { text: 'I think I understand', className: 'bg-amber-100 text-amber-700' },
        'ask_clarification': { text: 'Tell me more', className: 'bg-blue-100 text-blue-700' }
    };

    const label = labels[action] || labels['ask_clarification'];

    return (
        <span className={`px-2 py-0.5 text-xs rounded-full ${label.className}`}>
            {label.text}
        </span>
    );
}

export function MessageItem({ message, onSelect }: MessageItemProps) {
    const isUser = message.sender === 'user';
    const isSystem = message.sender === 'system';
    const metadata = message.metadata;

    const formatTime = (timestamp: string) => {
        return new Date(timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (isSystem) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-center my-4"
            >
                <div className="px-4 py-2 bg-warning/30 text-amber-700 text-sm rounded-full">
                    {message.text}
                </div>
            </motion.div>
        );
    }

    return (
        <motion.article
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
            className={`flex flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}
            onClick={() => onSelect?.(message.id)}
            aria-live={isUser ? undefined : 'polite'}
        >
            <div className={`message-bubble ${isUser ? 'user' : 'bot'} max-w-lg`}>
                {/* Main message text */}
                <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{message.text}</p>

                {/* Bot-only: Evidence section */}
                {!isUser && metadata?.evidence && (
                    <div className="mt-3 pt-3 border-t border-slate-border/30 space-y-1">
                        <p className="text-xs text-slate-text/60 font-medium mb-2">
                            What I understood:
                        </p>
                        <EvidencePill label="Feelings" items={metadata.evidence.emotions} />
                        <EvidencePill label="Experiences" items={metadata.evidence.symptoms} />
                        <EvidencePill label="Context" items={metadata.evidence.triggers} />
                    </div>
                )}

                {/* Bot-only: Clarification questions */}
                {!isUser && metadata?.clarificationQuestions && (
                    <ClarificationSection questions={metadata.clarificationQuestions} />
                )}

                {/* Bot-only: Action indicator */}
                {!isUser && metadata?.action && (
                    <div className="mt-3 flex items-center gap-2">
                        <ConfidenceIndicator action={metadata.action} />
                        {metadata.state && (
                            <span className="text-xs text-slate-text/50">
                                Pattern: {metadata.state}
                            </span>
                        )}
                    </div>
                )}

                {/* Disclaimer for cautious explanations */}
                {!isUser && metadata?.disclaimer && (
                    <p className="mt-3 text-xs text-slate-text/50 italic">
                        {metadata.disclaimer}
                    </p>
                )}
            </div>

            <span className="text-xs text-slate-text/40 px-2">
                {formatTime(message.timestamp)}
            </span>
        </motion.article>
    );
}
