import { motion } from 'framer-motion';
import { TrendingUp, AlertTriangle, Activity, Users } from 'lucide-react';

export function Dashboard() {
    const stats = [
        { label: 'Total Sessions', value: '12', icon: <Users size={20} />, color: 'primary' },
        { label: 'Avg. Session Length', value: '8 min', icon: <Activity size={20} />, color: 'secondary' },
        { label: 'Improvement Trend', value: '+15%', icon: <TrendingUp size={20} />, color: 'secondary' },
        { label: 'High Risk Sessions', value: '2', icon: <AlertTriangle size={20} />, color: 'warning' }
    ];

    const topSymptoms = [
        { name: 'Sleep issues', count: 8 },
        { name: 'Exam stress', count: 6 },
        { name: 'Anxiety', count: 5 },
        { name: 'Fatigue', count: 4 },
        { name: 'Social worry', count: 3 }
    ];

    return (
        <div className="h-full overflow-y-auto pb-20 md:pb-0 p-4 md:p-6 max-w-6xl mx-auto">
            <h1 className="text-2xl font-semibold mb-6">Dashboard</h1>

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                {stats.map((stat, index) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="card"
                    >
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${stat.color === 'primary' ? 'bg-primary/10 text-primary' :
                            stat.color === 'secondary' ? 'bg-secondary/10 text-secondary' :
                                'bg-warning/30 text-amber-600'
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
                    <h3 className="font-medium mb-4">Top Symptoms</h3>
                    <div className="space-y-3">
                        {topSymptoms.map((symptom) => (
                            <div key={symptom.name} className="flex items-center gap-3">
                                <div className="flex-1">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-sm">{symptom.name}</span>
                                        <span className="text-sm text-slate-text/50">{symptom.count}</span>
                                    </div>
                                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-primary to-secondary rounded-full"
                                            style={{ width: `${(symptom.count / 8) * 100}%` }}
                                        />
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="card"
                >
                    <h3 className="font-medium mb-4">Weekly Trend</h3>
                    <div className="h-48 flex items-end justify-around gap-2">
                        {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => {
                            const height = [40, 60, 45, 70, 55, 30, 35][i];
                            return (
                                <div key={day} className="flex flex-col items-center gap-2 flex-1">
                                    <div
                                        className="w-full bg-gradient-to-t from-primary to-secondary/50 rounded-t-lg transition-all"
                                        style={{ height: `${height}%` }}
                                    />
                                    <span className="text-xs text-slate-text/50">{day}</span>
                                </div>
                            );
                        })}
                    </div>
                </motion.div>
            </div>

            <p className="text-center text-sm text-slate-text/40 mt-8">
                Dashboard shows placeholder data. Real analytics will be available after integration.
            </p>
        </div>
    );
}
