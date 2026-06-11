import { Menu, HelpCircle, KeyRound, LogOut, Shield } from 'lucide-react';
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
    const menuButtonRef = useRef<HTMLButtonElement>(null);
    const firstMenuItemRef = useRef<HTMLAnchorElement>(null);

    // Close menu when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setShowUserMenu(false);
            }
        }
        function handleKeyDown(event: KeyboardEvent) {
            if (event.key === 'Escape') {
                setShowUserMenu(false);
                menuButtonRef.current?.focus();
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        document.addEventListener('keydown', handleKeyDown);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
            document.removeEventListener('keydown', handleKeyDown);
        };
    }, []);

    useEffect(() => {
        if (showUserMenu) firstMenuItemRef.current?.focus();
    }, [showUserMenu]);

    const handleLogout = async () => {
        await logout();
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
                            ref={menuButtonRef}
                            onClick={() => setShowUserMenu(!showUserMenu)}
                            className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center text-white font-medium text-sm hover:shadow-md transition-shadow"
                            aria-label="User menu"
                            aria-expanded={showUserMenu}
                            aria-controls="user-menu"
                        >
                            {getUserInitials()}
                        </button>

                        {/* Dropdown Menu */}
                        {showUserMenu && (
                            <>
                            <button
                                className="fixed inset-0 z-40 bg-black/20 sm:bg-transparent"
                                onClick={() => setShowUserMenu(false)}
                                aria-label="Close user menu"
                                tabIndex={-1}
                            />
                            <div id="user-menu" role="menu"
                                className="fixed right-2 top-14 sm:absolute sm:right-0 sm:top-auto sm:mt-2 w-[min(14rem,calc(100vw-1rem))] max-h-[calc(100vh-4rem)] overflow-y-auto bg-white rounded-xl shadow-lg border border-gray-100 py-1 z-50 animate-fade-in">
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
                                <div className="py-1">
                                    <Link ref={firstMenuItemRef} to="/change-password" role="menuitem"
                                        onClick={() => setShowUserMenu(false)}
                                        className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-50">
                                        <KeyRound size={16} /> Change password
                                    </Link>
                                    <Link to="/privacy" role="menuitem"
                                        onClick={() => setShowUserMenu(false)}
                                        className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-50">
                                        <Shield size={16} /> Privacy
                                    </Link>
                                </div>
                                <div className="border-t border-gray-100 py-1">
                                    <button
                                        onClick={handleLogout}
                                        className="flex items-center gap-2 px-4 py-2 text-sm text-error hover:bg-error/5 transition-colors w-full text-left"
                                        role="menuitem"
                                    >
                                        <LogOut size={16} />
                                        Sign Out
                                    </button>
                                </div>
                            </div>
                            </>
                        )}
                    </div>
                )}
            </div>
        </header>
    );
}
