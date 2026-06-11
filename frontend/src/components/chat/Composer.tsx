import { KeyboardEvent, useState } from 'react';
import { Send, X } from 'lucide-react';
import { motion } from 'framer-motion';

const MAX_LENGTH = 4000;

interface ComposerProps {
    onSend: (text: string) => void;
    disabled?: boolean;
    placeholder?: string;
}

export function Composer({ onSend, disabled, placeholder = 'Type your message...' }: ComposerProps) {
    const [text, setText] = useState('');
    const [error, setError] = useState('');

    function handleSend() {
        const trimmed = text.trim();
        if (!trimmed) {
            setError('Enter a message before sending.');
            return;
        }
        if (text.length > MAX_LENGTH) {
            setError(`Messages can be up to ${MAX_LENGTH.toLocaleString()} characters.`);
            return;
        }
        if (!disabled) {
            onSend(trimmed);
            setText('');
            setError('');
        }
    }

    function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSend();
        }
    }

    const nearLimit = text.length >= 3500;

    return (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="border-t border-gray-100 bg-card px-3 sm:px-4 pt-3 pb-2 min-w-0">
            <div className="flex items-end gap-2 sm:gap-3 min-w-0">
                <div className="flex-1 relative min-w-0">
                    <textarea value={text}
                        onChange={(event) => {
                            setText(event.target.value);
                            if (error) setError('');
                        }}
                        onKeyDown={handleKeyDown}
                        placeholder={placeholder}
                        disabled={disabled}
                        rows={1}
                        maxLength={MAX_LENGTH + 500}
                        aria-label="Message input"
                        aria-invalid={Boolean(error)}
                        aria-describedby="composer-status"
                        className="input-field resize-none min-h-[48px] max-h-[120px] pr-11" />
                    {text && (
                        <button type="button" onClick={() => { setText(''); setError(''); }}
                            className="absolute right-3 top-3 p-1 text-slate-text/40 hover:text-slate-text"
                            aria-label="Clear message">
                            <X size={18} />
                        </button>
                    )}
                </div>
                <button onClick={handleSend} disabled={disabled || text.length > MAX_LENGTH}
                    className="btn-primary p-3 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
                    aria-label="Send message">
                    <Send size={20} />
                </button>
            </div>
            <div id="composer-status" aria-live="polite"
                className={`min-h-5 mt-1 text-xs flex justify-between ${error ? 'text-error' : 'text-slate-text/40'}`}>
                <span>{error || 'Enter sends. Shift+Enter adds a new line.'}</span>
                {nearLimit && (
                    <span className={text.length > MAX_LENGTH ? 'text-error font-medium' : ''}>
                        {text.length.toLocaleString()} / {MAX_LENGTH.toLocaleString()}
                    </span>
                )}
            </div>
        </motion.div>
    );
}
