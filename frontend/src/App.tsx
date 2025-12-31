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
            <div className="flex h-screen bg-background">
                <LeftNav />

                <div className="flex-1 flex flex-col min-w-0">
                    <TopNav onMenuClick={() => setMobileMenuOpen(!mobileMenuOpen)} />

                    <main className="flex-1 overflow-hidden">
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
        </BrowserRouter>
    );
}
