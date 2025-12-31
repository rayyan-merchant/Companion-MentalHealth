import { Link, useLocation } from 'react-router-dom';
import { Home, MessageCircle, BarChart3, History, Settings, Info, Menu, X } from 'lucide-react';
import { useState } from 'react';

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
    { path: '/settings', label: 'Settings', icon: <Settings size={20} /> },
    { path: '/about', label: 'About', icon: <Info size={20} /> }
];

export function LeftNav() {
    const location = useLocation();
    const [isCollapsed, setIsCollapsed] = useState(false);

    return (
        <nav className={`hidden md:flex flex-col h-full bg-card border-r border-gray-100 transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-56'}`}>
            <div className="flex items-center justify-between p-4 border-b border-gray-100">
                {!isCollapsed && (
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
                            <span className="text-white text-sm font-bold">CK</span>
                        </div>
                        <span className="font-semibold text-slate-header">Calm KG</span>
                    </div>
                )}
                <button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    aria-label={isCollapsed ? 'Expand navigation' : 'Collapse navigation'}
                >
                    {isCollapsed ? <Menu size={20} /> : <X size={18} />}
                </button>
            </div>

            <div className="flex-1 py-4 px-2 space-y-1">
                {navItems.map((item) => (
                    <Link
                        key={item.path}
                        to={item.path}
                        className={`nav-link ${location.pathname === item.path ? 'active' : ''} ${isCollapsed ? 'justify-center' : ''}`}
                        title={isCollapsed ? item.label : undefined}
                    >
                        {item.icon}
                        {!isCollapsed && <span>{item.label}</span>}
                    </Link>
                ))}
            </div>

            {!isCollapsed && (
                <div className="p-4 border-t border-gray-100">
                    <div className="text-xs text-slate-text/50">
                        Session active
                    </div>
                </div>
            )}
        </nav>
    );
}
