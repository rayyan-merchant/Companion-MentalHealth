import { motion } from 'framer-motion';

interface QuickPromptsProps {
    onSelect: (text: string) => void;
}

const prompts = [
    "I can't sleep",
    "Exams stress",
    "Feeling overwhelmed",
    "Need to talk",
    "Anxious today"
];

export function QuickPrompts({ onSelect }: QuickPromptsProps) {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="flex flex-wrap gap-2 px-4 py-3 border-t border-gray-50"
        >
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
        </motion.div>
    );
}
