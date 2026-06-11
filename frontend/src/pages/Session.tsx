import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
    AlertCircle,
    Calendar,
    Loader2,
    MessageCircle,
    Plus,
    Search,
    Trash2
} from 'lucide-react';
import {
    deleteSession,
    getSessions,
    sessionKeys
} from '../api/sessions';

const PAGE_LOADED_AT = Date.now();

export function Session() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [searchQuery, setSearchQuery] = useState('');
    const sessionsQuery = useQuery({
        queryKey: sessionKeys.all,
        queryFn: getSessions,
        staleTime: 60 * 1000
    });
    const deletion = useMutation({
        mutationFn: deleteSession,
        onSuccess: (_, sessionId) => {
            queryClient.setQueryData(sessionKeys.all, (current: unknown) =>
                Array.isArray(current)
                    ? current.filter((item) => item.session_id !== sessionId)
                    : current
            );
            queryClient.invalidateQueries({ queryKey: sessionKeys.stats });
        }
    });

    const sessions = sessionsQuery.data || [];
    const query = searchQuery.trim().toLowerCase();
    const filtered = sessions.filter((session) =>
        session.title.toLowerCase().includes(query)
        || (session.last_message_preview || '').toLowerCase().includes(query)
    );
    const riskColors = {
        low: 'bg-secondary/10 text-secondary-dark',
        medium: 'bg-warning/50 text-amber-700',
        high: 'bg-error/10 text-error'
    };

    async function remove(sessionId: string, event: React.MouseEvent) {
        event.stopPropagation();
        if (deletion.isPending) return;
        if (!window.confirm('Are you sure you want to delete this session?')) return;
        deletion.mutate(sessionId);
    }

    function formatDate(value: string) {
        const date = new Date(value);
        const days = Math.floor((PAGE_LOADED_AT - date.getTime()) / 86_400_000);
        if (days === 0) return 'Today';
        if (days === 1) return 'Yesterday';
        if (days < 7) return `${days} days ago`;
        return date.toLocaleDateString();
    }

    return (
        <div className="pb-20 md:pb-8 p-4 md:p-6 max-w-4xl mx-auto min-w-0">
            <div className="flex flex-wrap gap-3 items-center justify-between mb-6">
                <h1 className="text-2xl font-semibold">Session History</h1>
                <button onClick={() => navigate('/chat')} className="btn-primary flex items-center gap-2">
                    <Plus size={18} /> New Session
                </button>
            </div>
            <div className="relative mb-6">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-text/40" size={20} />
                <input value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)}
                    maxLength={100} placeholder="Search sessions..."
                    className="w-full pl-12 pr-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50" />
            </div>

            {(sessionsQuery.error || deletion.error) && (
                <div role="alert" className="mb-6 p-4 bg-error/10 text-error rounded-xl flex gap-3">
                    <AlertCircle size={20} />
                    <span className="flex-1">
                        {(sessionsQuery.error || deletion.error) instanceof Error
                            ? (sessionsQuery.error || deletion.error)?.message
                            : 'Could not update sessions'}
                    </span>
                    <button onClick={() => sessionsQuery.refetch()} className="font-medium">Retry</button>
                </div>
            )}

            {sessionsQuery.isLoading ? (
                <div className="space-y-4" aria-label="Loading session history">
                    {[0, 1, 2].map((item) => (
                        <div key={item} className="card animate-pulse">
                            <div className="h-5 bg-slate-200 rounded w-1/2 mb-3" />
                            <div className="h-4 bg-slate-100 rounded w-4/5 mb-3" />
                            <div className="h-3 bg-slate-100 rounded w-1/3" />
                        </div>
                    ))}
                </div>
            ) : (
                <div className="space-y-4 min-w-0">
                    {filtered.map((session, index) => (
                        <motion.article key={session.session_id}
                            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.04 }}
                            onClick={() => navigate(`/chat/${session.session_id}`)}
                            className="card flex items-center justify-between cursor-pointer hover:shadow-md min-w-0 max-w-full">
                            <div className="flex items-start gap-4 flex-1 min-w-0 max-w-full">
                                <div className="p-2 bg-primary/10 rounded-lg shrink-0">
                                    <MessageCircle className="text-primary" size={20} />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium mb-1 truncate">{session.title}</p>
                                    {session.last_message_preview && (
                                        <p className="text-sm text-slate-text/50 break-words [overflow-wrap:anywhere] line-clamp-2 mb-2">
                                            {session.last_message_preview}
                                        </p>
                                    )}
                                    <div className="flex items-center gap-3 flex-wrap">
                                        <span className="text-sm text-slate-text/50 flex items-center gap-1">
                                            <Calendar size={14} /> {formatDate(session.updated_at)}
                                        </span>
                                        <span className="text-sm text-slate-text/50">{session.message_count} messages</span>
                                        <span className={`text-xs px-2 py-0.5 rounded-full ${riskColors[session.risk_level]}`}>
                                            {session.risk_level} risk
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <button onClick={(event) => remove(session.session_id, event)}
                                disabled={deletion.isPending}
                                className="p-2 ml-2 hover:bg-error/10 rounded-lg disabled:opacity-50"
                                aria-label={`Delete ${session.title}`}>
                                {deletion.isPending && deletion.variables === session.session_id
                                    ? <Loader2 size={18} className="text-error animate-spin" />
                                    : <Trash2 size={18} className="text-error/60" />}
                            </button>
                        </motion.article>
                    ))}
                </div>
            )}

            {!sessionsQuery.isLoading && filtered.length === 0 && (
                <div className="text-center py-12">
                    <div className="w-16 h-16 bg-primary/10 rounded-full grid place-items-center mx-auto mb-4">
                        <MessageCircle className="text-primary" size={32} />
                    </div>
                    <p className="text-slate-text/70 mb-4">
                        {query ? 'No sessions match your search.' : 'No conversations yet. Start one to build your private session history.'}
                    </p>
                    {query
                        ? <button onClick={() => setSearchQuery('')} className="text-primary">Clear search</button>
                        : <button onClick={() => navigate('/chat')} className="btn-primary">Start a conversation</button>}
                </div>
            )}
        </div>
    );
}
