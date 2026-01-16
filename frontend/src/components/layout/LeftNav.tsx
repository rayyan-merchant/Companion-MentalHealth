import { Link, useLocation } from 'react-router-dom';
import { Home, MessageCircle, BarChart3, History, Info, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { Logo } from './Logo';

interface NavItem {
    path: string;
    label: string;
    icon: React.ReactNode;
}

const navItems: NavItem[] = [
    { path: '/', label: 'Home', icon: <Home size={20} /> },
    { path: '/chat', label: 'Chat', icon: <MessageCircle size={20} /> },
    { path: '/dashboard', label: 'Dashboard', icon: <BarChart3 size={20} /> },
    { path: '/sessions', label: 'Sessions', icon: <History size={20} /> },
    { path: '/about', label: 'About', icon: <Info size={20} /> }
];

interface LeftNavProps {
    isOpen?: boolean;
    onClose?: () => void;
}

export function LeftNav({ isOpen = false, onClose }: LeftNavProps) {
    const location = useLocation();
    const [isCollapsed, setIsCollapsed] = useState(false);

    // Close mobile menu when route changes
    if (isOpen && onClose) {
        // We could use useEffect here but let's keep it simple for now or rely on parent
    }

    return (
        <>
            {/* Mobile Backdrop */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 md:hidden animate-fade-in"
                    onClick={onClose}
                />
            )}

            {/* Sidebar */}
            <nav className={`
                fixed md:static inset-y-0 left-0 z-50 
                flex flex-col h-full bg-card border-r border-gray-100/50 shadow-sm 
                transition-all duration-300 ease-in-out
                ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
                ${isCollapsed ? 'w-20' : 'w-64'}
            `}>
                <div className="flex items-center justify-between p-6 border-b border-gray-100/50">
                    {!isCollapsed && (
                        <div className="flex items-center gap-3">
                            <Logo size={32} />
                            <span className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">
                                Companion
                            </span>
                        </div>
                    )}

                    {/* Desktop Collapse Button */}
                    <button
                        onClick={() => setIsCollapsed(!isCollapsed)}
                        className={`hidden md:block p-2 hover:bg-primary/10 text-slate-text/70 hover:text-primary rounded-xl transition-all duration-200 ${isCollapsed ? 'mx-auto' : ''}`}
                        aria-label={isCollapsed ? 'Expand navigation' : 'Collapse navigation'}
                    >
                        {isCollapsed ? <Menu size={24} /> : <X size={20} />}
                    </button>

                    {/* Mobile Close Button */}
                    <button
                        onClick={onClose}
                        className="md:hidden p-2 hover:bg-gray-100 rounded-lg text-slate-text/70"
                        aria-label="Close menu"
                    >
                        <X size={24} />
                    </button>
                </div>

                <div className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
                    {navItems.map((item) => (
                        <Link
                            key={item.path}
                            to={item.path}
                            onClick={onClose}
                            className={`nav-link ${location.pathname === item.path ? 'active' : ''} ${isCollapsed ? 'justify-center' : ''}`}
                            title={isCollapsed ? item.label : undefined}
                        >
                            {item.icon}
                            {!isCollapsed && <span>{item.label}</span>}
                        </Link>
                    ))}
                </div>

                {!isCollapsed && (
                    <div className="px-4 pt-4 pb-2 border-t border-gray-100 mb-safe">
                        <div className="text-xs text-slate-text/50">
                            Session active
                        </div>
                    </div>
                )}
            </nav>
        </>
    );
}

