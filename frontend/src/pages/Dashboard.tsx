import { motion } from 'framer-motion';
import { TrendingUp, AlertTriangle, Activity, MessageSquare, Sparkles, X } from 'lucide-react';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getSessionStats, getDashboardInsight, sessionKeys } from '../api/sessions';
import { useAuth } from '../context/AuthContext';

export function Dashboard() {
    const { user } = useAuth();
    const dismissalKey = `companion:daily-observation-dismissed:${user?.user_id || 'anonymous'}`;
    const [showInsight, setShowInsight] = useState(
        () => sessionStorage.getItem(dismissalKey) !== 'true'
    );
    const statsQuery = useQuery({
        queryKey: sessionKeys.stats,
        queryFn: getSessionStats,
        staleTime: 60 * 1000
    });
    const insightQuery = useQuery({
        queryKey: sessionKeys.insight,
        queryFn: getDashboardInsight,
        enabled: Boolean(statsQuery.data?.total_sessions),
        refetchInterval: (query) => query.state.data?.status === 'generating' ? 2000 : false
    });
    const stats = statsQuery.data;
    const insight = insightQuery.data?.insight || null;

    if (statsQuery.isLoading) {
        return (
            <div className="p-4 md:p-6 max-w-6xl mx-auto" aria-label="Loading dashboard">
                <div className="h-8 w-48 bg-slate-200 rounded animate-pulse mb-6" />
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {[0, 1, 2, 3].map((item) => (
                        <div key={item} className="card animate-pulse">
                            <div className="h-10 w-10 bg-slate-200 rounded mb-3" />
                            <div className="h-7 w-16 bg-slate-200 rounded mb-2" />
                            <div className="h-4 w-24 bg-slate-100 rounded" />
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    // Default empty state if no stats
    if (!stats || stats.total_sessions === 0) {
        return (
            <div className="h-full flex flex-col items-center justify-center p-6 text-center">
                <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mb-4">
                    <Activity className="text-primary" size={32} />
                </div>
                <h2 className="text-xl font-semibold mb-2">No insights available yet</h2>
                <p className="text-slate-text/60 max-w-md mb-6">
                    Start chatting with Companion to see analytics about your emotional well-being and session patterns.
                </p>
            </div>
        );
    }

    const statCards = [
        {
            label: 'Total Sessions',
            value: stats.total_sessions.toString(),
            icon: <MessageSquare size={20} />,
            color: 'primary'
        },
        {
            label: 'Total Messages',
            value: stats.total_messages.toString(),
            icon: <Activity size={20} />,
            color: 'secondary'
        },
        {
            label: 'Sessions With Urgent Flags',
            value: stats.risk_distribution.high.toString(),
            icon: <AlertTriangle size={20} />,
            color: 'warning'
        },
        {
            label: 'Sessions Without Elevated Flags',
            value: stats.risk_distribution.low.toString(),
            icon: <TrendingUp size={20} />,
            color: 'success'
        }
    ];

    return (
        <div className="pb-20 md:pb-8 p-4 md:p-6 max-w-6xl mx-auto">
            <h1 className="text-2xl font-semibold mb-6">Your Insights</h1>

            {insight && showInsight && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-gradient-to-r from-primary/5 to-indigo-500/5 border border-primary/10 rounded-2xl p-6 mb-8 relative"
                >
                    <button
                        onClick={() => {
                            sessionStorage.setItem(dismissalKey, 'true');
                            setShowInsight(false);
                        }}
                        className="absolute top-4 right-4 text-slate-text/40 hover:text-slate-text/70 transition-colors"
                        title="Dismiss"
                    >
                        <X size={18} />
                    </button>
                    <div className="flex gap-4">
                        <div className="p-3 bg-white rounded-xl shadow-sm text-primary h-fit">
                            <Sparkles size={24} />
                        </div>
                        <div>
                            <h3 className="font-semibold text-lg mb-1 text-primary-dark">Daily Observation</h3>
                            <p className="text-slate-text/80 leading-relaxed max-w-3xl">
                                {insight}
                            </p>
                        </div>
                    </div>
                </motion.div>
            )}

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                {statCards.map((stat, index) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="card"
                    >
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${stat.color === 'primary' ? 'bg-primary/10 text-primary' :
                            stat.color === 'secondary' ? 'bg-secondary/10 text-secondary' :
                                stat.color === 'warning' ? 'bg-warning/20 text-amber-600' :
                                    'bg-success/10 text-success'
                            }`}>
                            {stat.icon}
                        </div>
                        <p className="text-2xl font-semibold mb-1">{stat.value}</p>
                        <p className="text-sm text-slate-text/50">{stat.label}</p>
                    </motion.div>
                ))}
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="card"
                >
                    <h3 className="font-medium mb-4">Common Themes</h3>
                    {stats.top_symptoms.length > 0 ? (
                        <div className="space-y-4">
                            {stats.top_symptoms.map((item) => (
                                <div key={item.name} className="flex items-center gap-3">
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-sm font-medium capitalize">{item.name}</span>
                                            <span className="text-sm text-slate-text/50">{item.count}</span>
                                        </div>
                                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-gradient-to-r from-primary to-secondary rounded-full"
                                                style={{ width: `${(item.count / Math.max(...stats.top_symptoms.map(s => s.count))) * 100}%` }}
                                            />
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-sm text-slate-text/50">Not enough data to identify themes yet.</p>
                    )}
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="card"
                >
                    <h3 className="font-medium mb-4">Safety Flag Distribution</h3>
                    <div className="flex items-end justify-center gap-8 h-48 py-4">
                        {['Low', 'Medium', 'High'].map((level) => {
                            const key = level.toLowerCase() as keyof typeof stats.risk_distribution;
                            const count = stats.risk_distribution[key];
                            const total = stats.total_sessions || 1;
                            const height = Math.max(10, (count / total) * 100);

                            const colorClass = key === 'low' ? 'bg-success/50' : key === 'medium' ? 'bg-warning/50' : 'bg-error/50';

                            return (
                                <div key={level} className="flex flex-col items-center gap-2 group w-16">
                                    <div className="relative flex-1 w-full flex items-end">
                                        <div
                                            className={`w-full rounded-t-lg transition-all duration-500 ease-out ${colorClass} group-hover:opacity-80`}
                                            style={{ height: `${height}%` }}
                                        />
                                    </div>
                                    <span className="text-sm font-medium">{count}</span>
                                    <span className="text-xs text-slate-text/50">{level}</span>
                                </div>
                            );
                        })}
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
