import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import { LeftNav } from './components/layout/LeftNav';
import { TopNav } from './components/layout/TopNav';
import { FooterBar } from './components/layout/FooterBar';
import { Home } from './pages/Home';
import { Chat } from './pages/Chat';
import { Session } from './pages/Session';
import { Dashboard } from './pages/Dashboard';
import { Settings } from './pages/Settings';
import { About } from './pages/About';

export default function App() {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <BrowserRouter>
            <div className="flex h-screen bg-slate-50 relative overflow-hidden">
                {/* Background Decoration */}
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary/10 blur-[100px] pointer-events-none animate-float" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-secondary/10 blur-[100px] pointer-events-none animate-float" style={{ animationDelay: '2s' }} />
                <div className="absolute top-[20%] right-[10%] w-[20%] h-[20%] rounded-full bg-accent/5 blur-[80px] pointer-events-none animate-float" style={{ animationDelay: '4s' }} />

                <div className="relative z-10 flex h-full w-full">
                    <LeftNav />

                    <div className="flex-1 flex flex-col min-w-0">
                        <TopNav onMenuClick={() => setMobileMenuOpen(!mobileMenuOpen)} />

                        <main className="flex-1 overflow-hidden relative">
                            <Routes>
                                <Route path="/" element={<Home />} />
                                <Route path="/chat" element={<Chat />} />
                                <Route path="/sessions" element={<Session />} />
                                <Route path="/dashboard" element={<Dashboard />} />
                                <Route path="/settings" element={<Settings />} />
                                <Route path="/about" element={<About />} />
                            </Routes>
                        </main>

                        <FooterBar />
                    </div>
                </div>
            </div>
        </BrowserRouter>
    );
}
