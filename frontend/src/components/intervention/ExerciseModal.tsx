import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Play, Pause, RotateCcw } from 'lucide-react';

interface ExerciseModalProps {
    isOpen: boolean;
    onClose: () => void;
    title?: string;
}

export function ExerciseModal({ isOpen, onClose, title = "Breathing Exercise" }: ExerciseModalProps) {
    const [phase, setPhase] = useState<'inhale' | 'hold' | 'exhale'>('inhale');
    const [isRunning, setIsRunning] = useState(false);
    const [cycles, setCycles] = useState(0);

    const phaseDuration = 4000;

    useEffect(() => {
        if (!isRunning) return;

        const interval = setInterval(() => {
            setPhase((p) => {
                if (p === 'inhale') return 'hold';
                if (p === 'hold') return 'exhale';
                setCycles((c) => c + 1);
                return 'inhale';
            });
        }, phaseDuration);

        return () => clearInterval(interval);
    }, [isRunning]);

    const handleReset = () => {
        setIsRunning(false);
        setPhase('inhale');
        setCycles(0);
    };

    const circleScale = phase === 'inhale' ? 1.3 : phase === 'hold' ? 1.3 : 1;

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
                    onClick={onClose}
                >
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        onClick={(e) => e.stopPropagation()}
                        className="bg-card rounded-2xl p-8 max-w-md w-full"
                    >
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-semibold">{title}</h2>
                            <button
                                onClick={onClose}
                                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                                aria-label="Close"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        <div className="flex flex-col items-center py-8">
                            <motion.div
                                animate={{ scale: circleScale }}
                                transition={{ duration: phaseDuration / 1000, ease: 'easeInOut' }}
                                className="w-32 h-32 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center mb-6"
                            >
                                <span className="text-white font-medium capitalize">{phase}</span>
                            </motion.div>

                            <p className="text-slate-text/60 mb-2">Cycles completed: {cycles}</p>

                            <div className="flex gap-3 mt-4">
                                <button
                                    onClick={() => setIsRunning(!isRunning)}
                                    className="btn-primary flex items-center gap-2"
                                >
                                    {isRunning ? <Pause size={18} /> : <Play size={18} />}
                                    {isRunning ? 'Pause' : 'Start'}
                                </button>
                                <button
                                    onClick={handleReset}
                                    className="btn-secondary flex items-center gap-2"
                                >
                                    <RotateCcw size={18} />
                                    Reset
                                </button>
                            </div>
                        </div>

                        <div className="mt-4 p-4 bg-background rounded-xl">
                            <h4 className="font-medium mb-2">Instructions</h4>
                            <ul className="text-sm text-slate-text/70 space-y-1">
                                <li>• Breathe in slowly for 4 seconds</li>
                                <li>• Hold your breath for 4 seconds</li>
                                <li>• Exhale slowly for 4 seconds</li>
                                <li>• Repeat 4-6 cycles</li>
                            </ul>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
