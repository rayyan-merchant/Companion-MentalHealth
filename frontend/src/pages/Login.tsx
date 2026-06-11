import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { AlertCircle, Lock, LogIn, Mail } from 'lucide-react';
import { Logo } from '../components/layout/Logo';
import { useAuth } from '../context/AuthContext';

export function Login() {
    const navigate = useNavigate();
    const { login } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    async function handleSubmit(event: FormEvent) {
        event.preventDefault();
        setError('');
        if (!email.trim()) {
            setError('Enter your email address.');
            return;
        }
        if (!password) {
            setError('Enter your password.');
            return;
        }
        setIsLoading(true);
        try {
            const user = await login(email.trim(), password);
            navigate(user.must_change_password ? '/change-password' : '/');
        } catch (reason) {
            setError(reason instanceof Error ? reason.message : 'Login failed');
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <main className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-slate-50 via-primary/5 to-secondary/5">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                className="relative z-10 w-full max-w-md">
                <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-white/50 p-6 sm:p-8">
                    <header className="text-center mb-8">
                        <div className="flex justify-center mb-4"><Logo size={48} /></div>
                        <h1 className="text-2xl font-bold">Welcome back</h1>
                        <p className="text-slate-text/60 mt-2">Sign in to continue privately</p>
                    </header>
                    {error && (
                        <div role="alert" className="mb-6 p-4 bg-error/10 border border-error/20 rounded-xl flex gap-3">
                            <AlertCircle className="text-error shrink-0" size={20} />
                            <p className="text-error text-sm">{error}</p>
                        </div>
                    )}
                    <form onSubmit={handleSubmit} noValidate className="space-y-5">
                        <label className="block text-sm font-medium" htmlFor="email">
                            Email address
                            <div className="relative mt-2">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-text/40" size={20} />
                                <input id="email" type="email" autoComplete="email" value={email}
                                    onChange={(event) => setEmail(event.target.value)}
                                    maxLength={254} placeholder="you@example.com"
                                    className="input-field pl-12" />
                            </div>
                        </label>
                        <label className="block text-sm font-medium" htmlFor="password">
                            Password
                            <div className="relative mt-2">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-text/40" size={20} />
                                <input id="password" type="password" autoComplete="current-password"
                                    value={password} onChange={(event) => setPassword(event.target.value)}
                                    maxLength={128} placeholder="Your password"
                                    className="input-field pl-12" />
                            </div>
                        </label>
                        <div className="text-right">
                            <Link to="/recovery" className="text-sm text-primary hover:underline">
                                Forgot your password?
                            </Link>
                        </div>
                        <button type="submit" disabled={isLoading}
                            className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50">
                            {isLoading ? 'Signing in...' : <><LogIn size={20} /> Sign in</>}
                        </button>
                    </form>
                    <p className="mt-6 text-center text-sm text-slate-text/60">
                        New to Companion? <Link to="/signup" className="text-primary font-medium">Create an account</Link>
                    </p>
                </div>
                <p className="mt-5 text-center text-xs text-slate-text/50">
                    Supportive reflection only. Not emergency or clinical care.
                </p>
            </motion.div>
        </main>
    );
}
