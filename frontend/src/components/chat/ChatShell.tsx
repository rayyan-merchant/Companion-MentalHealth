import { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Message } from '../../types';
import { MessageItem } from './MessageItem';

interface ChatShellProps {
    messages: Message[];
    isLoading?: boolean;
    onSelectMessage?: (id: string) => void;
}

function TypingIndicator() {
    return (
        <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="flex items-start gap-2"
        >
            <div className="message-bubble bot">
                <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </motion.div>
    );
}

export function ChatShell({ messages, isLoading, onSelectMessage }: ChatShellProps) {
    const scrollRef = useRef<HTMLDivElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (containerRef.current) {
            containerRef.current.scrollTo({
                top: containerRef.current.scrollHeight,
                behavior: 'smooth'
            });
        }
    }, [messages, isLoading]);

    const welcomeMessage: Message = {
        id: 'welcome',
        sender: 'bot',
        text: "Hi there! I'm here to listen and help you explore your feelings. How are you doing today?",
        timestamp: new Date().toISOString()
    };

    const displayMessages = messages.length > 0 ? messages : [welcomeMessage];

    return (
        <div
            ref={containerRef}
            className="flex-1 overflow-y-auto px-4 md:px-6 py-6 space-y-4"
        >
            <AnimatePresence mode="popLayout">
                {displayMessages.map((message) => (
                    <MessageItem
                        key={message.id}
                        message={message}
                        onSelect={onSelectMessage}
                    />
                ))}

                {isLoading && <TypingIndicator />}
            </AnimatePresence>

            <div ref={scrollRef} />
        </div>
    );
}
