import { useState } from 'react';
import { motion } from 'framer-motion';
import {
    Check,
    Code2,
    Copy,
    Cpu,
    ExternalLink,
    Heart,
    Phone,
    Shield
} from 'lucide-react';

function CopyNumber({ value }: { value: string }) {
    const [copied, setCopied] = useState(false);
    async function copy() {
        await navigator.clipboard.writeText(value);
        setCopied(true);
        window.setTimeout(() => setCopied(false), 1500);
    }
    return (
        <div className="flex flex-wrap items-center gap-2">
            <span className="select-all text-sm font-medium break-all">{value}</span>
            <button onClick={copy} className="p-1.5 rounded-lg hover:bg-primary/10 text-primary"
                aria-label={`Copy ${value}`}>
                {copied ? <Check size={16} /> : <Copy size={16} />}
            </button>
        </div>
    );
}

const developers = [
    {
        name: 'Syeda Rija Ali',
        email: 'rijaali287@gmail.com',
        github: 'https://github.com/Srijaali',
        linkedin: 'https://www.linkedin.com/in/rija-ali-731095296/'
    },
    {
        name: 'Rayyan Merchant',
        email: 'merchantrayyan43@gmail.com',
        github: 'https://github.com/rayyan-merchant',
        linkedin: 'https://www.linkedin.com/in/rayyanmerchant2004/'
    },
    {
        name: 'Riya Bhart',
        email: 'riyabhart02@gmail.com',
        github: 'https://github.com/RiyaBhart',
        linkedin: 'https://www.linkedin.com/in/riya-bhart-339036287'
    }
];

export function About() {
    return (
        <div className="pb-20 md:pb-8 p-4 md:p-6 max-w-4xl mx-auto min-w-0">
            <motion.header initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                className="text-center mb-10">
                <div className="w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-2xl grid place-items-center mx-auto mb-4">
                    <Heart className="text-white" size={32} />
                </div>
                <h1 className="text-3xl font-semibold mb-3">About Companion</h1>
                <p className="text-slate-text/60 max-w-2xl mx-auto leading-relaxed">
                    A supportive reflection tool for Pakistani university students. It uses a
                    versioned rule catalog and deterministic guidance when optional AI phrasing
                    providers are unavailable.
                </p>
            </motion.header>

            <div className="grid md:grid-cols-2 gap-6">
                <section className="card space-y-4 min-w-0">
                    <div className="flex items-center gap-3">
                        <Heart className="text-primary" />
                        <h2>Our mission</h2>
                    </div>
                    <p className="text-sm text-slate-text/70">
                        Companion helps students reflect on stress, anxiety, sleep, and social
                        patterns while encouraging healthy coping and support-seeking.
                    </p>
                    <div className="p-3 bg-secondary/10 rounded-lg text-sm">
                        <strong>Not a replacement for professional care.</strong> The system can
                        miss context and does not provide a diagnosis.
                    </div>
                </section>
                <section className="card space-y-4 min-w-0">
                    <div className="flex items-center gap-3">
                        <Shield className="text-success" />
                        <h2>Health and safety</h2>
                    </div>
                    <ul className="text-sm text-slate-text/70 space-y-2 list-disc pl-5">
                        <li>Not for emergencies or clinical decisions</li>
                        <li>External AI processing is optional and disclosed</li>
                        <li>Safety rules take priority over conversational phrasing</li>
                        <li>Clinician review is required before unrestricted release</li>
                    </ul>
                </section>
            </div>

            <section className="card mt-6 min-w-0">
                <div className="flex items-center gap-3 mb-6">
                    <Phone className="text-amber-600" />
                    <h2>Mental health resources in Pakistan</h2>
                </div>
                <div className="grid sm:grid-cols-2 gap-4">
                    <div className="p-4 bg-background rounded-xl min-w-0">
                        <h3 className="font-medium mb-2">Rozan Counseling Helpline</h3>
                        <CopyNumber value="+92 42 35761999" />
                    </div>
                    <ResourceLink name="Umang Pakistan" href="https://umang.com.pk" />
                    <ResourceLink name="Taskeen Mental Health" href="https://taskeen.org" />
                    <div className="p-4 bg-error/5 rounded-xl border border-error/10">
                        <h3 className="font-medium text-error mb-1">Emergency services</h3>
                        <p className="text-sm text-error mb-2">Dial from your phone:</p>
                        <CopyNumber value="1122" />
                    </div>
                </div>
            </section>

            <section className="mt-8">
                <h2 className="mb-5 flex items-center gap-2"><Code2 /> Developers</h2>
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {developers.map((developer) => (
                        <article key={developer.name} className="bg-white p-5 rounded-xl border border-gray-100 min-w-0">
                            <div className="w-12 h-12 bg-primary/10 rounded-full grid place-items-center text-primary font-bold mb-3">
                                {developer.name.charAt(0)}
                            </div>
                            <h3 className="font-medium break-words">{developer.name}</h3>
                            <a href={`mailto:${developer.email}`} className="text-xs text-slate-text/50 break-all">
                                {developer.email}
                            </a>
                            <div className="flex gap-3 mt-3 text-sm">
                                <a href={developer.github} target="_blank" rel="noopener noreferrer">GitHub</a>
                                <a href={developer.linkedin} target="_blank" rel="noopener noreferrer">LinkedIn</a>
                            </div>
                        </article>
                    ))}
                </div>
            </section>

            <section className="mt-8">
                <h2 className="mb-5 flex items-center gap-2"><Cpu /> Technologies used</h2>
                <div className="grid sm:grid-cols-2 gap-4">
                    <Tech title="Frontend" text="React, TypeScript, TanStack Query, Tailwind CSS" />
                    <Tech title="Backend" text="FastAPI, async SQLAlchemy, PostgreSQL, Redis" />
                    <Tech title="Runtime reasoning" text="Versioned YAML rules and deterministic response templates" />
                    <Tech title="Research validation" text="OWL, RDFLib, and SPARQL artifacts outside the production request path" />
                </div>
            </section>
        </div>
    );
}

function ResourceLink({ name, href }: { name: string; href: string }) {
    return (
        <div className="p-4 bg-background rounded-xl">
            <h3 className="font-medium mb-2">{name}</h3>
            <a href={href} target="_blank" rel="noopener noreferrer"
                className="text-primary text-sm inline-flex items-center gap-1">
                Visit website <ExternalLink size={12} />
            </a>
        </div>
    );
}

function Tech({ title, text }: { title: string; text: string }) {
    return (
        <div className="p-4 bg-white border border-gray-100 rounded-xl min-w-0">
            <h3 className="font-medium mb-2 text-sm text-primary">{title}</h3>
            <p className="text-xs text-slate-text/60 break-words">{text}</p>
        </div>
    );
}
