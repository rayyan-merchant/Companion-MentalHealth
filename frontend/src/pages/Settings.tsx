import { useState } from 'react';
import { motion } from 'framer-motion';
import { Moon, Sun, Type, Bell, Download, Trash2 } from 'lucide-react';

export function Settings() {
    const [darkMode, setDarkMode] = useState(false);
    const [fontSize, setFontSize] = useState<'small' | 'medium' | 'large'>('medium');
    const [notifications, setNotifications] = useState(true);

    return (
        <div className="h-full overflow-y-auto pb-20 md:pb-0 p-4 md:p-6 max-w-2xl mx-auto">
            <h1 className="text-2xl font-semibold mb-6">Settings</h1>

            <div className="space-y-6">
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="card"
                >
                    <h2 className="font-medium mb-4">Appearance</h2>

                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                {darkMode ? <Moon size={20} /> : <Sun size={20} />}
                                <div>
                                    <p className="font-medium">Dark Mode</p>
                                    <p className="text-sm text-slate-text/50">Switch to dark theme</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setDarkMode(!darkMode)}
                                className={`w-12 h-6 rounded-full transition-colors ${darkMode ? 'bg-primary' : 'bg-gray-200'
                                    }`}
                            >
                                <div
                                    className={`w-5 h-5 bg-white rounded-full shadow transition-transform ${darkMode ? 'translate-x-6' : 'translate-x-0.5'
                                        }`}
                                />
                            </button>
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <Type size={20} />
                                <div>
                                    <p className="font-medium">Text Size</p>
                                    <p className="text-sm text-slate-text/50">Adjust reading comfort</p>
                                </div>
                            </div>
                            <div className="flex gap-1">
                                {(['small', 'medium', 'large'] as const).map((size) => (
                                    <button
                                        key={size}
                                        onClick={() => setFontSize(size)}
                                        className={`px-3 py-1 rounded-lg text-sm capitalize ${fontSize === size
                                            ? 'bg-primary text-white'
                                            : 'bg-gray-100 hover:bg-gray-200'
                                            }`}
                                    >
                                        {size}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="card"
                >
                    <h2 className="font-medium mb-4">Notifications</h2>

                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <Bell size={20} />
                            <div>
                                <p className="font-medium">Session Reminders</p>
                                <p className="text-sm text-slate-text/50">Get gentle check-in prompts</p>
                            </div>
                        </div>
                        <button
                            onClick={() => setNotifications(!notifications)}
                            className={`w-12 h-6 rounded-full transition-colors ${notifications ? 'bg-primary' : 'bg-gray-200'
                                }`}
                        >
                            <div
                                className={`w-5 h-5 bg-white rounded-full shadow transition-transform ${notifications ? 'translate-x-6' : 'translate-x-0.5'
                                    }`}
                            />
                        </button>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="card"
                >
                    <h2 className="font-medium mb-4">Data</h2>

                    <div className="space-y-3">
                        <button className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors text-left">
                            <Download size={20} className="text-primary" />
                            <div>
                                <p className="font-medium">Export All Data</p>
                                <p className="text-sm text-slate-text/50">Download sessions as JSON</p>
                            </div>
                        </button>

                        <button className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-error/5 transition-colors text-left">
                            <Trash2 size={20} className="text-error" />
                            <div>
                                <p className="font-medium text-error">Clear All Data</p>
                                <p className="text-sm text-slate-text/50">Delete all local sessions</p>
                            </div>
                        </button>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
