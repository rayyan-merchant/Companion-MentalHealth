import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LeftNav } from './components/layout/LeftNav';
import { TopNav } from './components/layout/TopNav';
import { FooterBar } from './components/layout/FooterBar';
import { Home } from './pages/Home';
import { Chat } from './pages/Chat';
import { Session } from './pages/Session';
import { Dashboard } from './pages/Dashboard';
import { About } from './pages/About';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';

function AppLayout({ children }: { children: React.ReactNode }) {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <div className="fixed inset-0 flex bg-slate-50 overflow-hidden">
            {/* Background Decoration */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary/10 blur-[100px] pointer-events-none animate-float" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-secondary/10 blur-[100px] pointer-events-none animate-float" style={{ animationDelay: '2s' }} />
            <div className="absolute top-[20%] right-[10%] w-[20%] h-[20%] rounded-full bg-accent/5 blur-[80px] pointer-events-none animate-float" style={{ animationDelay: '4s' }} />

            <div className="relative z-10 flex h-full w-full">
                <LeftNav
                    isOpen={mobileMenuOpen}
                    onClose={() => setMobileMenuOpen(false)}
                />

                <div className="flex-1 flex flex-col min-w-0">
                    <TopNav onMenuClick={() => setMobileMenuOpen(!mobileMenuOpen)} />

                    <main className="flex-1 overflow-hidden relative">
                        {children}
                    </main>

                    <FooterBar />
                </div>
            </div>
        </div>
    );
}

export default function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Routes>
                    {/* Public routes - no layout */}
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<Signup />} />

                    {/* Protected routes - with layout */}
                    <Route path="/" element={
                        <ProtectedRoute>
                            <AppLayout><Home /></AppLayout>
                        </ProtectedRoute>
                    } />
                    <Route path="/chat" element={
                        <ProtectedRoute>
                            <AppLayout><Chat /></AppLayout>
                        </ProtectedRoute>
                    } />
                    <Route path="/chat/:sessionId" element={
                        <ProtectedRoute>
                            <AppLayout><Chat /></AppLayout>
                        </ProtectedRoute>
                    } />
                    <Route path="/sessions" element={
                        <ProtectedRoute>
                            <AppLayout><Session /></AppLayout>
                        </ProtectedRoute>
                    } />
                    <Route path="/dashboard" element={
                        <ProtectedRoute>
                            <AppLayout><Dashboard /></AppLayout>
                        </ProtectedRoute>
                    } />

                    <Route path="/about" element={
                        <ProtectedRoute>
                            <AppLayout><About /></AppLayout>
                        </ProtectedRoute>
                    } />
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}
