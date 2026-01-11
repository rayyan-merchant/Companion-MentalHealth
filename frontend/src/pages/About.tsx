import { motion } from 'framer-motion';
import { Heart, Shield, Phone, ExternalLink, Code2, Cpu } from 'lucide-react';

export function About() {
    return (
        <div className="h-full overflow-y-auto pb-20 md:pb-0 p-4 md:p-6 max-w-4xl mx-auto">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center mb-12"
            >
                <div className="w-16 h-16 bg-gradient-to-br from-primary to-secondary rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Heart className="text-white" size={32} />
                </div>
                <h1 className="text-3xl font-semibold mb-3">About Companion</h1>
                <p className="text-slate-text/60 max-w-lg mx-auto leading-relaxed">
                    A symbolic mental health support system designed to help you reflect on your emotional well-being through structured reasoning and safe guidance.
                </p>
            </motion.div>

            <div className="grid md:grid-cols-2 gap-6">
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="card space-y-4"
                >
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-primary/10 rounded-lg">
                            <Heart className="text-primary" size={24} />
                        </div>
                        <h2 className="font-semibold text-lg">Our Mission</h2>
                    </div>
                    <p className="text-slate-text/70 leading-relaxed text-sm">
                        Companion focuses on understanding patterns of stress, anxiety, and emotional distress using symbolic reasoning.
                        We aim to encourage self-awareness and support-seeking behavior through thoughtful conversation.
                    </p>
                    <div className="p-3 bg-secondary/10 rounded-lg text-sm text-secondary-dark">
                        ⚠️ <strong>Not a replacement for professional care.</strong> This is a supportive tool to help you understand your experiences.
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="card space-y-4"
                >
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-success/10 rounded-lg">
                            <Shield className="text-success" size={24} />
                        </div>
                        <h2 className="font-semibold text-lg">Health & Safety</h2>
                    </div>
                    <ul className="text-sm text-slate-text/70 space-y-2 list-disc pl-4">
                        <li>System does not diagnose medical conditions</li>
                        <li>Not for use in emergencies</li>
                        <li>Avoids harmful content</li>
                        <li>Encourages healthy coping strategies</li>
                    </ul>
                    <p className="text-xs text-slate-text/50 italic mt-2">
                        If you feel overwhelmed, please reach out to a professional.
                    </p>
                </motion.div>
            </div>

            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="card mt-6"
            >
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 bg-warning/10 rounded-lg">
                        <Phone className="text-amber-600" size={24} />
                    </div>
                    <h2 className="font-semibold text-lg">Mental Health Helplines (Pakistan)</h2>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                    <div className="p-4 bg-background rounded-xl">
                        <h3 className="font-medium mb-1">Rozan Counseling Helpline</h3>
                        <a href="tel:+924235761999" className="text-primary hover:underline text-sm flex items-center gap-1">
                            Use phone: +92 42 35761999
                        </a>
                    </div>
                    <div className="p-4 bg-background rounded-xl">
                        <h3 className="font-medium mb-1">Umang Pakistan</h3>
                        <a href="https://umang.com.pk" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline text-sm flex items-center gap-1">
                            Visit Website <ExternalLink size={12} />
                        </a>
                    </div>
                    <div className="p-4 bg-background rounded-xl">
                        <h3 className="font-medium mb-1">Taskeen Mental Health</h3>
                        <a href="https://taskeen.org" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline text-sm flex items-center gap-1">
                            Visit Website <ExternalLink size={12} />
                        </a>
                    </div>
                    <div className="p-4 bg-error/5 rounded-xl border border-error/10">
                        <h3 className="font-medium text-error mb-1">Emergency Services</h3>
                        <a href="tel:15" className="text-error font-bold hover:underline text-lg">
                            Dial 15
                        </a>
                    </div>
                </div>
            </motion.div>

            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="mt-8"
            >
                <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                    <Code2 className="text-slate-text/50" />
                    Developers
                </h2>
                <div className="grid md:grid-cols-3 gap-6">
                    {[
                        {
                            name: "Riya Bhart",
                            email: "riyabhart02@gmail.com",
                            github: "https://github.com/RiyaBhart",
                            linkedin: "http://www.linkedin.com/in/riya-bhart-339036287"
                        },
                        {
                            name: "Rayyan Merchant",
                            email: "merchantrayyan43@gmail.com",
                            github: "https://github.com/rayyan-merchant",
                            linkedin: "https://www.linkedin.com/in/rayyanmerchant2004/"
                        },
                        {
                            name: "Syeda Rija Ali",
                            email: "rija.ali@gmail.com",
                            github: "https://github.com/Srijaali",
                            linkedin: "https://www.linkedin.com/in/rija-ali-731095296/"
                        }
                    ].map((dev) => (
                        <div key={dev.name} className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all">
                            <div className="w-12 h-12 bg-gradient-to-br from-primary/20 to-secondary/20 rounded-full flex items-center justify-center text-primary font-bold mb-3">
                                {dev.name.charAt(0)}
                            </div>
                            <h3 className="font-medium">{dev.name}</h3>
                            <a href={`mailto:${dev.email}`} className="text-xs text-slate-text/50 hover:text-primary block mb-3 truncate">
                                {dev.email}
                            </a>
                            <div className="flex gap-3 mt-auto">
                                <a href={dev.github} target="_blank" rel="noopener noreferrer" className="text-sm text-slate-text hover:text-black">GitHub</a>
                                <div className="w-px h-4 bg-gray-200"></div>
                                <a href={dev.linkedin} target="_blank" rel="noopener noreferrer" className="text-sm text-slate-text hover:text-[#0077b5]">LinkedIn</a>
                            </div>
                        </div>
                    ))}
                </div>
            </motion.div>

            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="mt-8"
            >
                <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                    <Cpu className="text-slate-text/50" />
                    Technologies Used
                </h2>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="p-4 bg-white border border-gray-100 rounded-xl">
                        <h3 className="font-medium mb-2 text-sm text-primary">Frontend</h3>
                        <p className="text-xs text-slate-text/60">React, TailwindCSS, Framer Motion</p>
                    </div>
                    <div className="p-4 bg-white border border-gray-100 rounded-xl">
                        <h3 className="font-medium mb-2 text-sm text-secondary">Backend</h3>
                        <p className="text-xs text-slate-text/60">FastAPI, RESTful APIs</p>
                    </div>
                    <div className="p-4 bg-white border border-gray-100 rounded-xl">
                        <h3 className="font-medium mb-2 text-sm text-accent">AI & Reasoning</h3>
                        <p className="text-xs text-slate-text/60">KRR, Ontology Inference (OWL), SPARQL</p>
                    </div>
                    <div className="p-4 bg-white border border-gray-100 rounded-xl">
                        <h3 className="font-medium mb-2 text-sm text-slate-header">Data</h3>
                        <p className="text-xs text-slate-text/60">RDFLib, JSON Storage</p>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
