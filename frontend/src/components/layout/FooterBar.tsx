import { Plus, Save, Download } from 'lucide-react';

interface FooterBarProps {
    onNewSession?: () => void;
    onSave?: () => void;
    onExport?: () => void;
}

export function FooterBar({ onNewSession, onSave, onExport }: FooterBarProps) {
    return (
        <footer className="md:hidden fixed bottom-0 left-0 right-0 bg-card border-t border-gray-100 px-4 py-2 safe-area-inset-bottom">
            <div className="flex items-center justify-around">
                <button
                    onClick={onNewSession}
                    className="flex flex-col items-center gap-1 p-2 text-slate-text/70 hover:text-primary transition-colors"
                >
                    <Plus size={20} />
                    <span className="text-xs">New</span>
                </button>

                <button
                    onClick={onSave}
                    className="flex flex-col items-center gap-1 p-2 text-slate-text/70 hover:text-primary transition-colors"
                >
                    <Save size={20} />
                    <span className="text-xs">Save</span>
                </button>

                <button
                    onClick={onExport}
                    className="flex flex-col items-center gap-1 p-2 text-slate-text/70 hover:text-primary transition-colors"
                >
                    <Download size={20} />
                    <span className="text-xs">Export</span>
                </button>
            </div>
        </footer>
    );
}
