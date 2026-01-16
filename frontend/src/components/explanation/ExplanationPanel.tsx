import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, AlertCircle, ShieldCheck, Activity, Target, BrainCircuit } from 'lucide-react';
import { useState } from 'react';
import { KrrResult } from '../../types';

interface ExplanationPanelProps {
    krrResult: KrrResult | null;
}

export function ExplanationPanel({ krrResult }: ExplanationPanelProps) {
    const [isExpanded, setIsExpanded] = useState(true);

    if (!krrResult) {
        return (
            <div className="card">
                <h3 className="text-sm font-medium text-slate-text/50 mb-2">Hybrid Analysis</h3>
                <p className="text-sm text-slate-text/40 italic">
                    Waiting for your message to analyze signals...
                </p>
            </div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="card space-y-4"
        >
            <div className="flex items-center justify-between">
                <h3 className="font-medium flex items-center gap-2">
                    <ShieldCheck size={18} className="text-primary" />
                    Hybrid Agentic Analysis
                </h3>
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="p-1 hover:bg-gray-100 rounded"
                >
                    {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </button>
            </div>

            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="space-y-6"
                    >
                        {/* Primary State & Confidence */}
                        <div className="p-3 bg-primary/5 border border-primary/10 rounded-xl space-y-2">
                            <div className="flex items-center justify-between">
                                <span className="text-[10px] font-bold text-primary tracking-tight uppercase">Inferred Pattern</span>
                                <span className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${krrResult.confidence === 'high' ? 'bg-emerald-100 text-emerald-700' :
                                    krrResult.confidence === 'medium' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'
                                    }`}>
                                    {krrResult.confidence} confidence
                                </span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Activity size={16} className="text-primary" />
                                <span className="font-semibold text-slate-text">{krrResult.state || 'Analyzing...'}</span>
                            </div>
                        </div>

                        {/* Evidence Summary */}
                        <div className="space-y-3">
                            <h4 className="text-[10px] font-bold text-slate-text/40 uppercase tracking-wider flex items-center gap-1.5">
                                <BrainCircuit size={12} />
                                Extracted Signals (ML)
                            </h4>

                            <div className="space-y-3 pl-1">
                                {krrResult.evidence.emotions.length > 0 && (
                                    <div className="space-y-1">
                                        <span className="text-[9px] font-medium text-slate-400">EMOTIONS</span>
                                        <div className="flex flex-wrap gap-1.5">
                                            {krrResult.evidence.emotions.map(e => (
                                                <span key={e} className="px-2 py-0.5 bg-purple-50 text-purple-700 text-[11px] rounded border border-purple-100 font-medium">
                                                    {e}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {krrResult.evidence.symptoms.length > 0 && (
                                    <div className="space-y-1">
                                        <span className="text-[9px] font-medium text-slate-400">SYMPTOMS</span>
                                        <div className="flex flex-wrap gap-1.5">
                                            {krrResult.evidence.symptoms.map(s => (
                                                <span key={s} className="px-2 py-0.5 bg-orange-50 text-orange-700 text-[11px] rounded border border-orange-100 font-medium">
                                                    {s}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {krrResult.evidence.triggers.length > 0 && (
                                    <div className="space-y-1">
                                        <span className="text-[9px] font-medium text-slate-400">CONTEXT/TRIGGERS</span>
                                        <div className="flex flex-wrap gap-1.5">
                                            {krrResult.evidence.triggers.map(t => (
                                                <span key={t} className="px-2 py-0.5 bg-slate-100 text-slate-600 text-[11px] rounded border border-slate-200 font-medium">
                                                    {t}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Action Taken */}
                        <div className="space-y-3">
                            <h4 className="text-[10px] font-bold text-slate-text/40 uppercase tracking-wider flex items-center gap-1.5">
                                <Target size={12} />
                                Reasoning Action
                            </h4>
                            <div className="p-3 bg-background border border-slate-100 rounded-xl flex items-center gap-3">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${krrResult.action === 'explain' ? 'bg-emerald-100 text-emerald-600' :
                                    krrResult.action === 'explain_cautious' ? 'bg-amber-100 text-amber-600' : 'bg-blue-100 text-blue-600'
                                    }`}>
                                    <Activity size={16} />
                                </div>
                                <div className="flex flex-col">
                                    <span className="text-xs font-bold text-slate-text capitalize">
                                        {krrResult.action.replace('_', ' ')}
                                    </span>
                                    <span className="text-[10px] text-slate-text/50">Symbolic Gate Resolution</span>
                                </div>
                            </div>

                            {/* Reasoning Trace */}
                            {krrResult.reasoning_trace && krrResult.reasoning_trace.length > 0 && (
                                <div className="pl-3 border-l-2 border-slate-100 space-y-2">
                                    {krrResult.reasoning_trace.map((trace, idx) => (
                                        <div key={idx} className="flex items-start gap-2">
                                            <div className="mt-1 w-1.5 h-1.5 rounded-full bg-slate-300 flex-shrink-0" />
                                            <p className="text-[10px] text-slate-text/70 leading-relaxed">
                                                {trace}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Disclaimer */}
                        {krrResult.disclaimer && (
                            <div className="flex gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                                <AlertCircle size={14} className="text-slate-400 flex-shrink-0 mt-0.5" />
                                <p className="text-[11px] text-slate-text/60 leading-relaxed italic">
                                    {krrResult.disclaimer}
                                </p>
                            </div>
                        )}

                        <div className="pt-2 text-[9px] text-slate-300 font-mono text-center opacity-50">
                            Hybrid Pipeline v2.0 • Deterministic Symbolic Trace
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}
