import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AlertCircle, Check, Lock, Mail, UserPlus } from 'lucide-react';
import { ApiError } from '../api/client';
import { Logo } from '../components/layout/Logo';
import { useAuth } from '../context/AuthContext';

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function Signup() {
    const navigate = useNavigate();
    const { signup } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [formError, setFormError] = useState('');
    const [emailError, setEmailError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const requirements = [
        { label: '12 to 128 characters', met: password.length >= 12 && password.length <= 128 },
        { label: 'Passwords match', met: password.length > 0 && password === confirmPassword }
    ];

    async function submit(event: FormEvent) {
        event.preventDefault();
        setFormError('');
        setEmailError('');
        const normalizedEmail = email.trim().toLowerCase();
        if (!emailPattern.test(normalizedEmail)) {
            setEmailError('Enter a valid email address.');
            return;
        }
        if (password.length < 12 || password.length > 128) {
            setFormError('Password must be between 12 and 128 characters.');
            return;
        }
        if (password !== confirmPassword) {
            setFormError('Passwords do not match.');
            return;
        }
        setIsLoading(true);
        try {
            await signup(normalizedEmail, password);
            navigate('/');
        } catch (reason) {
            if (reason instanceof ApiError && reason.status === 409) {
                setEmailError('An account with this email already exists.');
            } else {
                setFormError(reason instanceof Error ? reason.message : 'Signup failed');
            }
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <main className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-slate-50 via-primary/5 to-secondary/5">
            <div className="relative z-10 w-full max-w-md">
                <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-white/50 p-6 sm:p-8">
                    <header className="text-center mb-8">
                        <div className="flex justify-center mb-4"><Logo size={48} /></div>
                        <h1 className="text-2xl font-bold">Create account</h1>
                        <p className="text-slate-text/60 mt-2">Start a private reflection space</p>
                    </header>
                    {formError && (
                        <div role="alert" className="mb-6 p-4 bg-error/10 text-error rounded-xl flex gap-3">
                            <AlertCircle className="shrink-0" size={20} />
                            <p className="text-sm">{formError}</p>
                        </div>
                    )}
                    <form onSubmit={submit} noValidate className="space-y-5">
                        <label htmlFor="email" className="block text-sm font-medium">
                            Email address
                            <div className="relative mt-2">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-text/40" size={20} />
                                <input id="email" type="email" autoComplete="email" value={email}
                                    onChange={(event) => { setEmail(event.target.value); setEmailError(''); }}
                                    maxLength={254} aria-invalid={Boolean(emailError)}
                                    aria-describedby={emailError ? 'email-error' : undefined}
                                    placeholder="you@example.com" className="input-field pl-12" />
                            </div>
                            {emailError && <span id="email-error" className="block text-xs text-error mt-2">{emailError}</span>}
                        </label>
                        <PasswordField id="password" label="Password" value={password}
                            autoComplete="new-password" onChange={setPassword} />
                        <PasswordField id="confirm-password" label="Confirm password"
                            value={confirmPassword} autoComplete="new-password" onChange={setConfirmPassword} />
                        <div className="space-y-2" aria-live="polite">
                            {requirements.map((requirement) => (
                                <div key={requirement.label} className="flex items-center gap-2 text-sm">
                                    <span className={`w-4 h-4 rounded-full grid place-items-center ${requirement.met ? 'bg-secondary text-white' : 'bg-slate-200'}`}>
                                        {requirement.met && <Check size={12} />}
                                    </span>
                                    <span className={requirement.met ? 'text-secondary-dark' : 'text-slate-text/50'}>
                                        {requirement.label}
                                    </span>
                                </div>
                            ))}
                        </div>
                        <button type="submit" disabled={isLoading || !requirements.every((item) => item.met)}
                            className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50">
                            {isLoading ? 'Creating account...' : <><UserPlus size={20} /> Create account</>}
                        </button>
                    </form>
                    <p className="mt-6 text-center text-sm text-slate-text/60">
                        Already registered? <Link to="/login" className="text-primary font-medium">Sign in</Link>
                    </p>
                </div>
                <p className="mt-5 text-center text-xs text-slate-text/50">
                    By continuing, review our <Link className="underline" to="/privacy">Privacy notice</Link> and <Link className="underline" to="/safety">Safety guidance</Link>.
                </p>
            </div>
        </main>
    );
}

function PasswordField({
    id,
    label,
    value,
    autoComplete,
    onChange
}: {
    id: string;
    label: string;
    value: string;
    autoComplete: string;
    onChange: (value: string) => void;
}) {
    return (
        <label htmlFor={id} className="block text-sm font-medium">
            {label}
            <div className="relative mt-2">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-text/40" size={20} />
                <input id={id} type="password" autoComplete={autoComplete} value={value}
                    onChange={(event) => onChange(event.target.value)}
                    minLength={12} maxLength={128} placeholder="At least 12 characters"
                    className="input-field pl-12" />
            </div>
        </label>
    );
}
