import { Menu, HelpCircle, LogOut } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Logo } from './Logo';
import { useAuth } from '../../context/AuthContext';

interface TopNavProps {
    onMenuClick?: () => void;
}

export function TopNav({ onMenuClick }: TopNavProps) {
    const navigate = useNavigate();
    const { user, logout, isAuthenticated } = useAuth();
    const [showUserMenu, setShowUserMenu] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    // Close menu when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setShowUserMenu(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleLogout = () => {
        logout();
        setShowUserMenu(false);
        navigate('/login');
    };

    // Get user initials for avatar
    const getUserInitials = () => {
        if (!user?.email) return 'U';
        return user.email.charAt(0).toUpperCase();
    };

    return (
        <header className="flex items-center justify-between px-4 py-2 bg-white border-b border-gray-100">
            <div className="flex items-center gap-4">
                <button
                    onClick={onMenuClick}
                    className="md:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    aria-label="Open menu"
                >
                    <Menu size={24} />
                </button>

                <Link to="/" className="flex items-center gap-2 group">
                    <div className="md:hidden">
                        <Logo size={32} />
                    </div>
                    <span className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary hidden sm:block">
                        Companion
                    </span>
                </Link>
            </div>

            <div className="flex items-center gap-2">
                <Link
                    to="/about"
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    aria-label="Help and information"
                >
                    <HelpCircle size={20} />
                </Link>

                {/* User Menu */}
                {isAuthenticated && (
                    <div className="relative" ref={menuRef}>
                        <button
                            onClick={() => setShowUserMenu(!showUserMenu)}
                            className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center text-white font-medium text-sm hover:shadow-md transition-shadow"
                            aria-label="User menu"
                        >
                            {getUserInitials()}
                        </button>

                        {/* Dropdown Menu */}
                        {showUserMenu && (
                            <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-100 py-1 z-50 animate-fade-in">
                                <div className="px-4 py-3 border-b border-gray-100">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center text-white font-medium">
                                            {getUserInitials()}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium text-slate-header truncate">
                                                {user?.email}
                                            </p>
                                            <p className="text-xs text-slate-text/50">
                                                Signed in
                                            </p>
                                        </div>
                                    </div>
                                </div>



                                <div className="border-t border-gray-100 py-1">
                                    <button
                                        onClick={handleLogout}
                                        className="flex items-center gap-2 px-4 py-2 text-sm text-error hover:bg-error/5 transition-colors w-full text-left"
                                    >
                                        <LogOut size={16} />
                                        Sign Out
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </header>
    );
}
