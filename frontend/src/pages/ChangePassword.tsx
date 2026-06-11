import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, Lock } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function ChangePassword() {
    const { changePassword, user } = useAuth();
    const navigate = useNavigate();
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [saving, setSaving] = useState(false);

    async function submit(event: FormEvent) {
        event.preventDefault();
        setError('');
        if (newPassword.length < 12) {
            setError('Your new password must be at least 12 characters.');
            return;
        }
        if (newPassword !== confirmPassword) {
            setError('New passwords do not match.');
            return;
        }
        setSaving(true);
        try {
            await changePassword(currentPassword, newPassword);
            navigate('/');
        } catch (reason) {
            setError(reason instanceof Error ? reason.message : 'Password change failed');
        } finally {
            setSaving(false);
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <form onSubmit={submit} className="card w-full max-w-md space-y-5">
                <div>
                    <Lock className="text-primary mb-3" />
                    <h1 className="text-2xl">Change your password</h1>
                    <p className="text-sm text-slate-text/60 mt-2">
                        {user?.must_change_password
                            ? 'An administrator reset your password. Choose a private password before continuing.'
                            : 'Update your account password.'}
                    </p>
                </div>
                {error && (
                    <div role="alert" className="p-3 bg-error/10 text-error rounded-xl flex gap-2 text-sm">
                        <AlertCircle size={18} /> {error}
                    </div>
                )}
                <label className="block text-sm font-medium">
                    Current password
                    <input className="input-field mt-2" type="password" value={currentPassword}
                        onChange={(event) => setCurrentPassword(event.target.value)} required maxLength={128} />
                </label>
                <label className="block text-sm font-medium">
                    New password
                    <input className="input-field mt-2" type="password" value={newPassword}
                        onChange={(event) => setNewPassword(event.target.value)} required minLength={12} maxLength={128} />
                </label>
                <label className="block text-sm font-medium">
                    Confirm new password
                    <input className="input-field mt-2" type="password" value={confirmPassword}
                        onChange={(event) => setConfirmPassword(event.target.value)} required maxLength={128} />
                </label>
                <button className="btn-primary w-full" disabled={saving}>
                    {saving ? 'Updating...' : 'Update password'}
                </button>
            </form>
        </div>
    );
}
