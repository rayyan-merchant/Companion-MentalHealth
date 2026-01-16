import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Calendar, Download, Trash2, MessageCircle, Plus, Search, Loader2, AlertCircle } from 'lucide-react';
import { getSessions, deleteSession, SessionSummary } from '../api/sessions';

export function Session() {
    const navigate = useNavigate();
    const [sessions, setSessions] = useState<SessionSummary[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [deletingId, setDeletingId] = useState<string | null>(null);

    // Fetch sessions on mount
    useEffect(() => {
        loadSessions();
    }, []);

    const loadSessions = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const data = await getSessions();
            setSessions(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load sessions');
        } finally {
            setIsLoading(false);
        }
    };

    const handleOpenSession = (sessionId: string) => {
        navigate(`/chat/${sessionId}`);
    };

    const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
        e.stopPropagation();
        if (!confirm('Are you sure you want to delete this session?')) return;

        try {
            setDeletingId(sessionId);
            await deleteSession(sessionId);
            setSessions(prev => prev.filter(s => s.session_id !== sessionId));
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete session');
        } finally {
            setDeletingId(null);
        }
    };

    const handleNewSession = () => {
        navigate('/chat');
    };

    // Filter sessions by search query
    const filteredSessions = sessions.filter(session =>
        session.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        session.last_message_preview?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const riskColors = {
        low: 'bg-secondary/10 text-secondary-dark',
        medium: 'bg-warning/50 text-amber-700',
        high: 'bg-error/10 text-error'
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) {
            return 'Today';
        } else if (days === 1) {
            return 'Yesterday';
        } else if (days < 7) {
            return `${days} days ago`;
        } else {
            return date.toLocaleDateString();
        }
    };

    return (
        <div className="h-full overflow-y-auto pb-20 md:pb-0 p-4 md:p-6 max-w-4xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-semibold">Session History</h1>
                <button
                    onClick={handleNewSession}
                    className="btn-primary flex items-center gap-2"
                >
                    <Plus size={18} />
                    New Session
                </button>
            </div>

            {/* Search Bar */}
            <div className="relative mb-6">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-text/40" size={20} />
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search sessions..."
                    className="w-full pl-12 pr-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
                />
            </div>

            {/* Error State */}
            {error && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-6 p-4 bg-error/10 border border-error/20 rounded-xl flex items-center gap-3"
                >
                    <AlertCircle className="text-error flex-shrink-0" size={20} />
                    <p className="text-error text-sm">{error}</p>
                    <button
                        onClick={loadSessions}
                        className="ml-auto text-sm text-error hover:underline"
                    >
                        Retry
                    </button>
                </motion.div>
            )}

            {/* Loading State */}
            {isLoading && (
                <div className="flex flex-col items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 text-primary animate-spin mb-4" />
                    <p className="text-slate-text/50">Loading sessions...</p>
                </div>
            )}

            {/* Sessions List */}
            {!isLoading && (
                <div className="space-y-4">
                    {filteredSessions.map((session, index) => (
                        <motion.div
                            key={session.session_id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            onClick={() => handleOpenSession(session.session_id)}
                            className="card flex items-center justify-between cursor-pointer hover:shadow-md hover:border-primary/20 transition-all"
                        >
                            <div className="flex items-start gap-4 flex-1 min-w-0">
                                <div className="p-2 bg-primary/10 rounded-lg flex-shrink-0">
                                    <MessageCircle className="text-primary" size={20} />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="font-medium mb-1 truncate">{session.title}</p>
                                    {session.last_message_preview && (
                                        <p className="text-sm text-slate-text/50 truncate mb-2">
                                            {session.last_message_preview}
                                        </p>
                                    )}
                                    <div className="flex items-center gap-3 flex-wrap">
                                        <span className="text-sm text-slate-text/50 flex items-center gap-1">
                                            <Calendar size={14} />
                                            {formatDate(session.updated_at)}
                                        </span>
                                        <span className="text-sm text-slate-text/50">
                                            {session.message_count} messages
                                        </span>
                                        <span className={`text-xs px-2 py-0.5 rounded-full ${riskColors[session.risk_level]}`}>
                                            {session.risk_level} risk
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center gap-2 ml-4">
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        // TODO: Implement export
                                    }}
                                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                                    title="Export"
                                >
                                    <Download size={18} className="text-slate-text/50" />
                                </button>
                                <button
                                    onClick={(e) => handleDeleteSession(session.session_id, e)}
                                    disabled={deletingId === session.session_id}
                                    className="p-2 hover:bg-error/10 rounded-lg transition-colors disabled:opacity-50"
                                    title="Delete"
                                >
                                    {deletingId === session.session_id ? (
                                        <Loader2 size={18} className="text-error/50 animate-spin" />
                                    ) : (
                                        <Trash2 size={18} className="text-error/50" />
                                    )}
                                </button>
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}

            {/* Empty State */}
            {!isLoading && filteredSessions.length === 0 && (
                <div className="text-center py-12">
                    <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                        <MessageCircle className="text-primary" size={32} />
                    </div>
                    {searchQuery ? (
                        <>
                            <p className="text-slate-text/70 mb-2">No sessions match your search</p>
                            <button
                                onClick={() => setSearchQuery('')}
                                className="text-primary text-sm hover:underline"
                            >
                                Clear search
                            </button>
                        </>
                    ) : (
                        <>
                            <p className="text-slate-text/70 mb-4">No sessions yet. Start a conversation to create your first session.</p>
                            <button
                                onClick={handleNewSession}
                                className="btn-primary inline-flex items-center gap-2"
                            >
                                <Plus size={18} />
                                Start Your First Conversation
                            </button>
                        </>
                    )}
                </div>
            )}
        </div>
    );
}
