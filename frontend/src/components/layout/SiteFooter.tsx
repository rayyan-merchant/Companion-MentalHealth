import { Link } from 'react-router-dom';

interface SiteFooterProps {
    compact?: boolean;
}

export function SiteFooter({ compact = false }: SiteFooterProps) {
    return (
        <footer className={compact ? 'px-4 pb-4' : 'px-4 sm:px-6 pb-6 pt-2'}>
            <div className="mx-auto max-w-4xl rounded-2xl border border-white/60 bg-white/70 px-4 py-3 backdrop-blur-xl shadow-sm">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <p className="text-xs font-medium tracking-wide text-slate-text/60">
                        Companion · private reflection space
                    </p>
                    <div className="flex items-center gap-3 text-xs text-slate-text/50">
                        <Link to="/privacy" className="hover:text-primary transition-colors">Privacy</Link>
                        <span aria-hidden="true">·</span>
                        <Link to="/safety" className="hover:text-primary transition-colors">Safety</Link>
                        <span aria-hidden="true">·</span>
                        <Link to="/about" className="hover:text-primary transition-colors">About</Link>
                    </div>
                </div>
                <p className="mt-2 text-[11px] leading-5 text-slate-text/45">
                    Supportive only, not a replacement for professional help. If you are in crisis, contact local emergency services or a mental health professional.
                </p>
            </div>
        </footer>
    );
}