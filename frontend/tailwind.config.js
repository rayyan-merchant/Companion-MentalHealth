/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: '#8B5CF6', // Violet-500
                    light: '#A78BFA',    // Violet-400
                    dark: '#7C3AED',     // Violet-600
                },
                secondary: {
                    DEFAULT: '#EC4899',  // Pink-500
                    light: '#F472B6',    // Pink-400
                    dark: '#DB2777',     // Pink-600
                },
                accent: {
                    DEFAULT: '#F59E0B',  // Amber-500
                    light: '#FBBF24',
                    dark: '#D97706',
                },
                slate: {
                    text: '#334155',
                    header: '#1E293B'
                },
                background: '#F8FAFC',
                card: '#FFFFFF',
                warning: '#F59E0B',
                error: '#EF4444',
                success: '#10B981',
            },
            fontFamily: {
                sans: ['Inter', 'Roboto', 'system-ui', 'sans-serif']
            },
            boxShadow: {
                'soft': '0 4px 20px -2px rgba(139, 92, 246, 0.1)', // Violet shadow
                'card': '0 10px 30px -5px rgba(0, 0, 0, 0.05)',
                'glow': '0 0 15px rgba(139, 92, 246, 0.5)',
            },
            borderRadius: {
                'xl': '1rem',
                '2xl': '1.5rem',
                '3xl': '2rem',
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-out',
                'slide-up': 'slideUp 0.5s ease-out',
                'pulse-soft': 'pulseSoft 3s infinite',
                'float': 'float 6s ease-in-out infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' }
                },
                slideUp: {
                    '0%': { opacity: '0', transform: 'translateY(20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' }
                },
                pulseSoft: {
                    '0%, 100%': { opacity: '0.6' },
                    '50%': { opacity: '1' }
                },
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                }
            }
        },
    },
    plugins: [],
}
