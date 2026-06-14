import { Link } from 'react-router-dom';
import { SiteFooter } from '../components/layout/SiteFooter';

export function Privacy() {
    return (
        <main className="min-h-dvh flex flex-col bg-slate-50 p-4 md:p-8">
            <div className="flex-1">
                <article className="card max-w-3xl mx-auto prose prose-slate">
                    <h1>Privacy notice</h1>
                    <p>Companion stores your account email, conversations, message assessments, safety flags, and security events so the service can provide session history and protect accounts.</p>
                    <h2>AI providers</h2>
                    <p>External phrasing providers are optional. When enabled by the operator, recent conversation text may be sent to the configured provider. Deterministic local responses remain available when providers are disabled or unavailable.</p>
                    <h2>Retention and deletion</h2>
                    <p>Deleted conversations are hidden immediately and permanently purged after 30 days. Redacted security and safety records are retained for 90 days. Application logs do not contain raw conversation text or passwords.</p>
                    <h2>Important limits</h2>
                    <p>Companion is a supportive reflection tool, not a medical service or emergency monitoring system. Review the <Link to="/safety">Safety page</Link> before use.</p>
                    <Link to="/" className="text-primary">Return to Companion</Link>
                </article>
            </div>
            <SiteFooter compact />
        </main>
    );
}
