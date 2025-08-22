/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dracula color palette
        dracula: {
          background: '#282a36',
          'current-line': '#44475a',
          foreground: '#f8f8f2',
          comment: '#6272a4',
          cyan: '#8be9fd',
          green: '#50fa7b',
          orange: '#ffb86c',
          pink: '#ff79c6',
          purple: '#bd93f9',
          red: '#ff5555',
          yellow: '#f1fa8c',
        },
        // Override default colors with Dracula theme
        gray: {
          50: '#f8f8f2',
          100: '#f8f8f2',
          200: '#f8f8f2',
          300: '#f8f8f2',
          400: '#6272a4',
          500: '#6272a4',
          600: '#44475a',
          700: '#44475a',
          800: '#282a36',
          900: '#282a36',
        },
        purple: {
          400: '#bd93f9',
          500: '#bd93f9',
          600: '#a78bfa',
        },
        green: {
          400: '#50fa7b',
          500: '#50fa7b',
          600: '#4ade80',
        },
        red: {
          400: '#ff5555',
          500: '#ff5555',
          600: '#ef4444',
        },
        yellow: {
          400: '#f1fa8c',
          500: '#f1fa8c',
          600: '#eab308',
        },
        cyan: {
          400: '#8be9fd',
          500: '#8be9fd',
          600: '#06b6d4',
        },
        orange: {
          400: '#ffb86c',
          500: '#ffb86c',
          600: '#f97316',
        },
        pink: {
          400: '#ff79c6',
          500: '#ff79c6',
          600: '#ec4899',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'bounce-in': 'bounceIn 0.6s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceIn: {
          '0%': { transform: 'scale(0.3)', opacity: '0' },
          '50%': { transform: 'scale(1.05)' },
          '70%': { transform: 'scale(0.9)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
      },
    },
  },
  plugins: [],
}
