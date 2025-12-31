import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { MessageCircle, Brain, Heart, Shield } from 'lucide-react';

export function Home() {
    return (
        <div className="min-h-full flex flex-col">
            <section className="flex-1 flex flex-col items-center justify-center px-6 py-12">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center max-w-2xl"
                >
                    <div className="w-20 h-20 bg-gradient-to-br from-primary to-secondary rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-lg">
                        <Heart className="text-white" size={40} />
                    </div>

                    <h1 className="text-4xl md:text-5xl font-bold text-slate-header mb-6 leading-tight">
                        Hi, I'm your<br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">
                            Wellness Assistant
                        </span>
                    </h1>

                    <p className="text-lg text-slate-text/70 mb-8 leading-relaxed">
                        A calming, explainable companion to help you explore and understand your feelings.
                        Let's have a conversation about how you're doing.
                    </p>

                    <Link to="/chat" className="btn-primary inline-flex items-center gap-2 text-lg px-8 py-4">
                        <MessageCircle size={22} />
                        Start Conversation
                    </Link>
                </motion.div>
            </section>

            <section className="px-6 py-12 bg-card border-t border-gray-100">
                <div className="max-w-4xl mx-auto">
                    <h2 className="text-center text-2xl font-semibold mb-8">How it works</h2>

                    <div className="grid md:grid-cols-3 gap-6">
                        {[
                            {
                                icon: <MessageCircle className="text-primary" size={28} />,
                                title: "Share your thoughts",
                                desc: "Express how you're feeling in your own words"
                            },
                            {
                                icon: <Brain className="text-secondary" size={28} />,
                                title: "Understand the reasoning",
                                desc: "See clear explanations of patterns and insights"
                            },
                            {
                                icon: <Shield className="text-primary" size={28} />,
                                title: "Get gentle guidance",
                                desc: "Receive safe, supportive suggestions for well-being"
                            }
                        ].map((item, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.2 + index * 0.1 }}
                                className="p-6 bg-background rounded-2xl text-center"
                            >
                                <div className="w-14 h-14 bg-card rounded-xl flex items-center justify-center mx-auto mb-4 shadow-soft">
                                    {item.icon}
                                </div>
                                <h3 className="font-medium mb-2">{item.title}</h3>
                                <p className="text-sm text-slate-text/60">{item.desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            <footer className="px-6 py-8 text-center text-sm text-slate-text/50">
                <p>This is a supportive tool, not a replacement for professional help.</p>
                <p className="mt-1">If you're in crisis, please contact a mental health professional.</p>
            </footer>
        </div>
    );
}
