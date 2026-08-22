/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        club: {
          blue: '#0ea5e9',         // Azul deportivo (sky-500)
          'blue-dark': '#0284c7',   // sky-600
          'blue-light': '#38bdf8',  // sky-400
          green: '#10b981',         // Verde salud (emerald-500)
          'green-dark': '#059669',  // emerald-600
          'green-light': '#34d399', // emerald-400
          red: '#ef4444',
          amber: '#f59e0b',
          purple: '#8b5cf6',
          gray: {
            50: '#f8fafc',
            100: '#f1f5f9',
            200: '#e2e8f0',
            300: '#cbd5e1',
            400: '#94a3b8',
            500: '#64748b',
            600: '#475569',
            700: '#334155',
            800: '#1e293b',
            900: '#0f172a',
          },
          tier: {
            bronce: '#cd7f32',
            plata: '#c0c0c0',
            oro: '#ffd700',
            diamante: '#b9f2ff',
          }
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        card: '0 4px 20px -6px rgba(15, 23, 42, 0.15)',
        nav: '0 -4px 16px -4px rgba(15, 23, 42, 0.18)',
      },
      borderRadius: {
        xl: '1rem',
        '2xl': '1.25rem',
      },
    },
  },
  plugins: [],
}
