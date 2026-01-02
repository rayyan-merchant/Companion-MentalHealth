import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, AlertCircle, ShieldCheck } from 'lucide-react';
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
                <h3 className="text-sm font-medium text-slate-text/50 mb-2">Symbolic Analysis</h3>
                <p className="text-sm text-slate-text/40">
                    Awaiting input to generate symbolic reasoning trace.
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
                    Symbolic Analysis
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
                        {/* Ranked Concerns */}
                        <div>
                            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-text/50 mb-3">
                                Ranked Concerns
                            </h4>
                            <div className="space-y-2">
                                {krrResult.ranked_concerns.map((concern, idx) => (
                                    <div key={idx} className="p-3 bg-red-50/50 border border-red-100 rounded-lg flex items-center gap-3">
                                        <div className="w-6 h-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center text-xs font-bold">
                                            {idx + 1}
                                        </div>
                                        <span className="font-medium text-slate-text">{concern}</span>
                                    </div>
                                ))}
                                {krrResult.ranked_concerns.length === 0 && (
                                    <p className="text-sm text-slate-text/60 italic">No specific concerns identified.</p>
                                )}
                            </div>
                        </div>

                        {/* Detected Evidence (New) */}
                        {(krrResult.detected_symptoms?.length || krrResult.detected_emotions?.length || krrResult.detected_triggers?.length) ? (
                            <div>
                                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-text/50 mb-3">
                                    Detected Evidence
                                </h4>
                                <div className="space-y-3">
                                    {/* Symptoms */}
                                    {krrResult.detected_symptoms && krrResult.detected_symptoms.length > 0 && (
                                        <div className="flex flex-col gap-1">
                                            <span className="text-[10px] font-medium text-slate-400">SYMPTOMS</span>
                                            <div className="flex flex-wrap gap-2">
                                                {krrResult.detected_symptoms.map(s => (
                                                    <span key={s} className="px-2 py-1 bg-orange-50 text-orange-700 text-xs rounded-md border border-orange-100">
                                                        {s}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                    {/* Emotions */}
                                    {krrResult.detected_emotions && krrResult.detected_emotions.length > 0 && (
                                        <div className="flex flex-col gap-1">
                                            <span className="text-[10px] font-medium text-slate-400">EMOTIONS</span>
                                            <div className="flex flex-wrap gap-2">
                                                {krrResult.detected_emotions.map(s => (
                                                    <span key={s} className="px-2 py-1 bg-purple-50 text-purple-700 text-xs rounded-md border border-purple-100">
                                                        {s}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                    {/* Triggers */}
                                    {krrResult.detected_triggers && krrResult.detected_triggers.length > 0 && (
                                        <div className="flex flex-col gap-1">
                                            <span className="text-[10px] font-medium text-slate-400">TRIGGERS</span>
                                            <div className="flex flex-wrap gap-2">
                                                {krrResult.detected_triggers.map(s => (
                                                    <span key={s} className="px-2 py-1 bg-slate-100 text-slate-600 text-xs rounded-md border border-slate-200">
                                                        {s}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ) : null}

                        {/* Interventions (New) */}
                        {krrResult.recommended_interventions && krrResult.recommended_interventions.length > 0 && (
                            <div>
                                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-text/50 mb-3">
                                    Suggested Actions
                                </h4>
                                <div className="space-y-2">
                                    {krrResult.recommended_interventions.map((int, idx) => (
                                        <div key={idx} className="p-3 bg-emerald-50/50 border border-emerald-100 rounded-lg">
                                            <div className="font-medium text-emerald-800 text-sm">{int.name}</div>
                                            <div className="text-xs text-emerald-600/70 mt-1">Target: {int.reason}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Explanations */}
                        <div>
                            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-text/50 mb-3">
                                Reasoning Trace
                            </h4>
                            <div className="bg-background rounded-xl p-4 border border-gray-100/50 shadow-sm text-sm space-y-3 leading-relaxed text-slate-text/80">
                                {krrResult.explanations.map((exp, idx) => (
                                    <p key={idx}>{exp}</p>
                                ))}
                            </div>
                        </div>

                        {/* Disclaimer */}
                        <div className="flex gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
                            <AlertCircle size={16} className="text-slate-400 flex-shrink-0 mt-0.5" />
                            <p className="text-xs text-slate-text/60 leading-relaxed">
                                {krrResult.disclaimer}
                            </p>
                        </div>

                        <div className="pt-2 text-[10px] text-slate-300 font-mono text-center">
                            Audit Ref: {krrResult.audit_ref}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}

