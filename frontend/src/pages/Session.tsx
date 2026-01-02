import { motion } from 'framer-motion';
import { Calendar, Download, Trash2 } from 'lucide-react';

interface SessionItem {
    id: string;
    date: string;
    summary: string;
    riskLevel: 'low' | 'medium' | 'high';
}

const mockSessions: SessionItem[] = [
    { id: '1', date: '2025-12-05', summary: 'Discussed exam stress and sleep issues', riskLevel: 'medium' },
    { id: '2', date: '2025-12-04', summary: 'Explored relaxation techniques', riskLevel: 'low' },
    { id: '3', date: '2025-12-03', summary: 'Talked about workload management', riskLevel: 'low' }
];

export function Session() {
    const riskColors = {
        low: 'bg-secondary/10 text-secondary-dark',
        medium: 'bg-warning/50 text-amber-700',
        high: 'bg-error/10 text-error'
    };

    return (
        <div className="h-full overflow-y-auto pb-20 md:pb-0 p-4 md:p-6 max-w-4xl mx-auto">
            <h1 className="text-2xl font-semibold mb-6">Session History</h1>

            <div className="space-y-4">
                {mockSessions.map((session, index) => (
                    <motion.div
                        key={session.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="card flex items-center justify-between"
                    >
                        <div className="flex items-start gap-4">
                            <div className="p-2 bg-primary/10 rounded-lg">
                                <Calendar className="text-primary" size={20} />
                            </div>
                            <div>
                                <p className="font-medium mb-1">{session.summary}</p>
                                <div className="flex items-center gap-3">
                                    <span className="text-sm text-slate-text/50">{session.date}</span>
                                    <span className={`text-xs px-2 py-0.5 rounded-full ${riskColors[session.riskLevel]}`}>
                                        {session.riskLevel} risk
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center gap-2">
                            <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="Export">
                                <Download size={18} className="text-slate-text/50" />
                            </button>
                            <button className="p-2 hover:bg-error/10 rounded-lg transition-colors" title="Delete">
                                <Trash2 size={18} className="text-error/50" />
                            </button>
                        </div>
                    </motion.div>
                ))}
            </div>

            {mockSessions.length === 0 && (
                <div className="text-center py-12 text-slate-text/50">
                    <p>No sessions yet. Start a conversation to create your first session.</p>
                </div>
            )}
        </div>
    );
}
