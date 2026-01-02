import { Menu, Moon, Sun, HelpCircle } from 'lucide-react';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Logo } from './Logo';

interface TopNavProps {
    onMenuClick?: () => void;
}

export function TopNav({ onMenuClick }: TopNavProps) {
    const [isDarkMode, setIsDarkMode] = useState(false);

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
                <button
                    onClick={() => setIsDarkMode(!isDarkMode)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
                >
                    {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
                </button>

                <Link
                    to="/about"
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    aria-label="Help and information"
                >
                    <HelpCircle size={20} />
                </Link>

                <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center text-primary font-medium text-sm">
                    U
                </div>
            </div>
        </header>
    );
}
