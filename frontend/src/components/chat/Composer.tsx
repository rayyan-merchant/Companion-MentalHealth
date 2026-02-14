import { useState, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';
import { motion } from 'framer-motion';

interface ComposerProps {
    onSend: (text: string) => void;
    disabled?: boolean;
    placeholder?: string;
}

export function Composer({ onSend, disabled, placeholder = "Type your message..." }: ComposerProps) {
    const [text, setText] = useState('');

    const handleSend = () => {
        const trimmed = text.trim();
        if (trimmed && !disabled) {
            onSend(trimmed);
            setText('');
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="border-t border-gray-100 bg-card px-4 pt-4 pb-2"
        >
            <div className="flex items-end gap-3">
                <div className="flex-1 relative">
                    <textarea
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={placeholder}
                        disabled={disabled}
                        rows={1}
                        className="input-field resize-none min-h-[48px] max-h-[120px] pr-12"
                        style={{ height: 'auto' }}
                        aria-label="Message input"
                    />
                </div>

                <button
                    onClick={handleSend}
                    disabled={disabled || !text.trim()}
                    className="btn-primary p-3 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed"
                    aria-label="Send message"
                >
                    <Send size={20} />
                </button>
            </div>

            <p className="text-[10px] text-slate-text/30 mt-1 text-center font-medium">
                Press Enter to send, Shift+Enter for new line
            </p>
        </motion.div>
    );
}
