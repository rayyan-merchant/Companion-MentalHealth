import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getPublicConfig } from '../api/client';

export function Recovery() {
    const [email, setEmail] = useState('support@example.com');
    useEffect(() => {
        getPublicConfig().then((config) => setEmail(config.support_email)).catch(() => undefined);
    }, []);
    return (
        <main className="min-h-screen grid place-items-center p-4 bg-slate-50">
            <div className="card max-w-lg">
                <h1 className="text-2xl mb-3">Account recovery</h1>
                <p className="text-slate-text/70 mb-4">
                    For this beta, password resets are handled by the support team.
                    Contact <a className="text-primary underline break-all" href={`mailto:${email}`}>{email}</a> from your registered email address.
                </p>
                <p className="text-sm text-slate-text/60 mb-5">
                    Support will issue a one-time temporary password. All existing sessions
                    will be revoked and you will be required to choose a new password.
                </p>
                <Link className="text-primary font-medium" to="/login">Return to sign in</Link>
            </div>
        </main>
    );
}
