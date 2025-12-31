import { motion } from 'framer-motion';
import { Message } from '../../types';

interface MessageItemProps {
    message: Message;
    onSelect?: (id: string) => void;
}

export function MessageItem({ message, onSelect }: MessageItemProps) {
    const isUser = message.sender === 'user';
    const isSystem = message.sender === 'system';

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
            <div className={`message-bubble ${isUser ? 'user' : 'bot'}`}>
                <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{message.text}</p>

                {message.metadata?.confidence && !isUser && (
                    <div className="mt-2 flex items-center gap-2">
                        <span className={`confidence-badge ${message.metadata.confidence >= 0.7 ? 'high' :
                                message.metadata.confidence >= 0.4 ? 'medium' : 'low'
                            }`}>
                            Confidence: {Math.round(message.metadata.confidence * 100)}%
                        </span>
                    </div>
                )}
            </div>

            <span className="text-xs text-slate-text/40 px-2">
                {formatTime(message.timestamp)}
            </span>
        </motion.article>
    );
}
