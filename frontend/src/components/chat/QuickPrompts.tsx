import { motion } from 'framer-motion';

import { X } from 'lucide-react';

interface QuickPromptsProps {
    onSelect: (text: string) => void;
    onClose?: () => void;
}

const prompts = [
    "I can't sleep",
    "Exams stress",
    "Feeling overwhelmed",
    "Need to talk",
    "Anxious today"
];

export function QuickPrompts({ onSelect, onClose }: QuickPromptsProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ delay: 0.3 }}
            className="flex items-center justify-between px-4 py-3 border-t border-gray-50"
        >
            <div className="flex flex-wrap gap-2 items-center flex-1">
                <span className="text-xs text-slate-text/50 mr-2 self-center">Quick:</span>
                {prompts.map((prompt, index) => (
                    <motion.button
                        key={prompt}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.1 * index }}
                        onClick={() => onSelect(prompt)}
                        className="chip"
                    >
                        {prompt}
                    </motion.button>
                ))}
            </div>

            {onClose && (
                <button
                    onClick={onClose}
                    className="ml-2 p-1 text-slate-text/40 hover:text-slate-text/70 hover:bg-black/5 rounded-full transition-colors"
                    title="Dismiss suggestions"
                >
                    <X size={14} />
                </button>
            )}
        </motion.div>
    );
}
