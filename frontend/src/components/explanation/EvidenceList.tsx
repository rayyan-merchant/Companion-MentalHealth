import { motion } from 'framer-motion';
import { MessageSquare } from 'lucide-react';

interface EvidenceItem {
    messageId: string;
    snippet: string;
    timestamp: string;
}

interface EvidenceListProps {
    items: EvidenceItem[];
    onItemClick?: (messageId: string) => void;
}

export function EvidenceList({ items, onItemClick }: EvidenceListProps) {
    if (items.length === 0) {
        return null;
    }

    return (
        <div className="card mt-4">
            <h4 className="text-sm font-medium text-slate-text/70 mb-3">Evidence</h4>
            <ul className="space-y-2">
                {items.map((item, index) => (
                    <motion.li
                        key={item.messageId}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                    >
                        <button
                            onClick={() => onItemClick?.(item.messageId)}
                            className="w-full text-left p-3 bg-background rounded-lg hover:bg-primary/5 transition-colors group"
                        >
                            <div className="flex items-start gap-2">
                                <MessageSquare size={14} className="text-primary mt-0.5 flex-shrink-0" />
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm text-slate-text/80 line-clamp-2">{item.snippet}</p>
                                    <span className="text-xs text-slate-text/40">{item.timestamp}</span>
                                </div>
                            </div>
                        </button>
                    </motion.li>
                ))}
            </ul>
        </div>
    );
}
