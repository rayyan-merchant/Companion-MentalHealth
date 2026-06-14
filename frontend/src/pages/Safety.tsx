import { Link } from 'react-router-dom';
import { SiteFooter } from '../components/layout/SiteFooter';

export function Safety() {
    return (
        <main className="min-h-dvh flex flex-col bg-slate-50 p-4 md:p-8">
            <div className="flex-1">
                <article className="card max-w-3xl mx-auto prose prose-slate">
                    <h1>Safety and emergency support</h1>
                    <p>Companion can miss context and does not diagnose, treat, or replace a qualified mental-health professional.</p>
                    <h2>Immediate danger</h2>
                    <p>If you or someone else may be in immediate danger in Pakistan, call Rescue 1122 from a phone or go to the nearest emergency department. Do not wait for a chat response.</p>
                    <h2>Support resources</h2>
                    <p>Rozan Counseling Helpline: <strong>+92 42 35761999</strong>. You can also visit Umang Pakistan or Taskeen for current support information.</p>
                    <h2>Clinical review status</h2>
                    <p>The beta rule set and coping content require clinician review before unrestricted public release. Responses are designed for supportive reflection, not clinical decision-making.</p>
                    <Link to="/" className="text-primary">Return to Companion</Link>
                </article>
            </div>
            <SiteFooter compact />
        </main>
    );
}
