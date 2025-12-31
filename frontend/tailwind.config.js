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
                    DEFAULT: '#6AAFE6',
                    light: '#8FC4ED',
                    dark: '#4A9AD9'
                },
                secondary: {
                    DEFAULT: '#66C2B6',
                    light: '#8AD4CA',
                    dark: '#4AA89C'
                },
                slate: {
                    text: '#334155',
                    header: '#0F172A'
                },
                background: '#F8FAFC',
                card: '#FFFFFF',
                warning: '#F5D0A9',
                error: '#EF4444'
            },
            fontFamily: {
                sans: ['Inter', 'Roboto', 'system-ui', 'sans-serif']
            },
            boxShadow: {
                'soft': '0 2px 8px rgba(0, 0, 0, 0.06)',
                'card': '0 4px 12px rgba(0, 0, 0, 0.08)'
            },
            borderRadius: {
                'xl': '1rem',
                '2xl': '1.5rem'
            },
            animation: {
                'fade-in': 'fadeIn 0.3s ease-out',
                'slide-up': 'slideUp 0.3s ease-out',
                'pulse-soft': 'pulseSoft 2s infinite'
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' }
                },
                slideUp: {
                    '0%': { opacity: '0', transform: 'translateY(8px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' }
                },
                pulseSoft: {
                    '0%, 100%': { opacity: '0.6' },
                    '50%': { opacity: '1' }
                }
            }
        },
    },
    plugins: [],
}
