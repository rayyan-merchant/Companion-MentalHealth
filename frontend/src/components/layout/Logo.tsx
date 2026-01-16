import { motion } from 'framer-motion';

export function Logo({ className = "w-8 h-8", size = 32 }: { className?: string, size?: number }) {
    return (
        <div className={`relative flex items-center justify-center ${className}`}>
            <motion.svg
                width={size}
                height={size}
                viewBox="0 0 32 32"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                initial="initial"
                animate="animate"
                whileHover="hover"
            >
                <defs>
                    <linearGradient id="logoGradient" x1="0" y1="0" x2="32" y2="32">
                        <stop offset="0%" stopColor="#8B5CF6" /> {/* Violet */}
                        <stop offset="100%" stopColor="#EC4899" /> {/* Pink */}
                    </linearGradient>
                </defs>

                {/* Outer Circle Ring */}
                <motion.circle
                    cx="16"
                    cy="16"
                    r="12"
                    stroke="url(#logoGradient)"
                    strokeWidth="3"
                    strokeLinecap="round"
                    variants={{
                        initial: { pathLength: 0, opacity: 0, rotate: -90 },
                        animate: {
                            pathLength: 1,
                            opacity: 1,
                            rotate: 0,
                            transition: { duration: 1.5, ease: "easeOut" }
                        },
                        hover: {
                            scale: 1.1,
                            transition: { duration: 0.3 }
                        }
                    }}
                />

                {/* Inner Dot/Heart */}
                <motion.path
                    d="M16 22C16 22 21 17 21 14C21 11.5 19.5 10 17.5 10C16.5 10 16 11 16 11C16 11 15.5 10 14.5 10C12.5 10 11 11.5 11 14C11 17 16 22 16 22Z"
                    fill="url(#logoGradient)"
                    variants={{
                        initial: { scale: 0, opacity: 0 },
                        animate: {
                            scale: 1,
                            opacity: 1,
                            transition: { delay: 0.5, type: "spring", stiffness: 200 }
                        },
                        hover: {
                            scale: 1.2,
                            transition: { yoyo: Infinity, duration: 0.8 }
                        }
                    }}
                />
            </motion.svg>
        </div>
    );
}
