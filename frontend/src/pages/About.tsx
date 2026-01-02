import { motion } from 'framer-motion';
import { Heart, Shield, BookOpen, ExternalLink } from 'lucide-react';

export function About() {
    return (
        <div className="h-full overflow-y-auto pb-20 md:pb-0 p-4 md:p-6 max-w-3xl mx-auto">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center mb-12"
            >
                <div className="w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Heart className="text-white" size={32} />
                </div>
                <h1 className="text-3xl font-semibold mb-3">About Calm KG</h1>
                <p className="text-slate-text/60 max-w-lg mx-auto">
                    A Mental Health Knowledge Graph powered wellness assistant built with explainable AI.
                </p>
            </motion.div>

            <div className="space-y-6">
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="card"
                >
                    <div className="flex items-start gap-4">
                        <div className="p-2 bg-primary/10 rounded-lg">
                            <BookOpen className="text-primary" size={24} />
                        </div>
                        <div>
                            <h2 className="font-medium mb-2">Project Overview</h2>
                            <p className="text-sm text-slate-text/70 leading-relaxed">
                                This project uses OWL ontology and knowledge graph reasoning to provide
                                explainable emotional wellness support. The system extracts symptoms and
                                emotions from conversations, maps them to ontology concepts, and provides
                                clear explanations for its insights.
                            </p>
                        </div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="card"
                >
                    <div className="flex items-start gap-4">
                        <div className="p-2 bg-secondary/10 rounded-lg">
                            <Shield className="text-secondary" size={24} />
                        </div>
                        <div>
                            <h2 className="font-medium mb-2">Safety & Privacy</h2>
                            <p className="text-sm text-slate-text/70 leading-relaxed mb-3">
                                This is a supportive educational tool, not a replacement for professional
                                mental health care. All conversations are processed locally and not stored
                                on external servers.
                            </p>
                            <div className="p-3 bg-warning/20 rounded-lg">
                                <p className="text-sm text-amber-700">
                                    <strong>Important:</strong> If you're experiencing a mental health crisis,
                                    please reach out to a professional counselor or call your local emergency services.
                                </p>
                            </div>
                        </div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="card"
                >
                    <h2 className="font-medium mb-4">Technologies Used</h2>
                    <div className="flex flex-wrap gap-2">
                        {['React', 'TypeScript', 'TailwindCSS', 'Framer Motion', 'FastAPI', 'OWL', 'RDF', 'SPARQL'].map((tech) => (
                            <span key={tech} className="chip">
                                {tech}
                            </span>
                        ))}
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="card"
                >
                    <h2 className="font-medium mb-3">Resources</h2>
                    <ul className="space-y-2">
                        {[
                            { label: 'National Suicide Prevention Lifeline', url: 'https://988lifeline.org' },
                            { label: 'Crisis Text Line', url: 'https://www.crisistextline.org' },
                            { label: 'SAMHSA National Helpline', url: 'https://www.samhsa.gov/find-help/national-helpline' }
                        ].map((resource) => (
                            <li key={resource.label}>
                                <a
                                    href={resource.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-2 text-primary hover:underline"
                                >
                                    <ExternalLink size={14} />
                                    {resource.label}
                                </a>
                            </li>
                        ))}
                    </ul>
                </motion.div>
            </div>

            <footer className="mt-12 text-center text-sm text-slate-text/40">
                <p>Knowledge Representation & Reasoning Project</p>
                <p className="mt-1">© 2025</p>
            </footer>
        </div>
    );
}
