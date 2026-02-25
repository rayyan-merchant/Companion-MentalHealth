import { motion } from 'framer-motion';
import { Clock, Play, Check } from 'lucide-react';
import { Intervention } from '../../types';

interface InterventionCardProps {
    intervention: Intervention;
    onStart?: () => void;
    onMarkTried?: () => void;
}

export function InterventionCard({ intervention, onStart, onMarkTried }: InterventionCardProps) {
    const urgencyColors = {
        low: 'bg-secondary/10 text-secondary-dark',
        medium: 'bg-warning/50 text-amber-700',
        high: 'bg-error/10 text-error'
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="card"
        >
            <div className="flex items-start justify-between mb-3">
                <h4 className="font-medium">{intervention.title}</h4>
                <span className={`text-xs px-2 py-0.5 rounded-full ${urgencyColors[intervention.urgency]}`}>
                    {intervention.urgency}
                </span>
            </div>

            {intervention.description && (
                <p className="text-sm text-slate-text/60 mb-3">{intervention.description}</p>
            )}

            <div className="flex items-center gap-2 text-sm text-slate-text/50 mb-4">
                <Clock size={14} />
                <span>{intervention.duration}</span>
            </div>

            {intervention.steps && (
                <ul className="space-y-1.5 mb-4">
                    {intervention.steps.slice(0, 3).map((step, index) => (
                        <li key={index} className="text-sm text-slate-text/70 flex items-start gap-2">
                            <span className="text-primary">•</span>
                            {step}
                        </li>
                    ))}
                </ul>
            )}

            <div className="flex gap-2">
                <button
                    onClick={onStart}
                    className="btn-primary text-sm py-2 px-4 flex items-center gap-2"
                >
                    <Play size={14} />
                    Start now
                </button>
                <button
                    onClick={onMarkTried}
                    className="btn-secondary text-sm py-2 px-4 flex items-center gap-2"
                >
                    <Check size={14} />
                    Mark as tried
                </button>
            </div>
        </motion.div>
    );
}
