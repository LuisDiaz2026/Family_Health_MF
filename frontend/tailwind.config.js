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
          forest: '#174C3C',
          'forest-dark': '#0F3829',
          'forest-light': '#256B54',
          wellness: '#3B8064',
          'wellness-dark': '#2E664F',
          'wellness-light': '#4FA07E',
          gold: '#D7AE58',
          'gold-dark': '#B8913F',
          'gold-light': '#E6C77D',
          coral: '#E9784A',
          'coral-dark': '#CC5F34',
          'coral-light': '#F19A74',
          ivory: '#F7F4EC',
          'ivory-dark': '#ECE7D8',
          'ivory-light': '#FBFAF6',
          graphite: '#232927',
          'graphite-dark': '#151918',
          'graphite-light': '#3A4340',
          red: '#ef4444',
          amber: '#f59e0b',
          purple: '#8b5cf6',
          gray: {
            50: '#FBFAF6',
            100: '#F7F4EC',
            200: '#ECE7D8',
            300: '#D6CFBA',
            400: '#9FA694',
            500: '#6E786A',
            600: '#4F574C',
            700: '#3A4340',
            800: '#232927',
            900: '#151918',
          },
          tier: {
            bronce: '#cd7f32',
            plata: '#c0c0c0',
            oro: '#D7AE58',
            diamante: '#b9f2ff',
          },
          area: {
            gym: '#174C3C',
            'gym-accent': '#232927',
            sports: '#3B8064',
            'sports-accent': '#E9784A',
            cultural: '#D7AE58',
            'cultural-accent': '#E9784A',
            family: '#3B8064',
            'family-accent': '#F7F4EC',
            vip: '#174C3C',
            'vip-accent': '#D7AE58',
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
