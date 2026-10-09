/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        navy: '#08263D',
        deep: '#061B2C',
        cream: '#F7F8F5',
        ok: '#159447',
        warn: '#E59B28',
        bad: '#D92D3A',
        ai: '#7657D9',
        info: '#3478D4',
      },
      fontFamily: {
        display: ['Newsreader', 'Georgia', 'serif'],
        sans: ['"Public Sans"', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 2px rgba(8,38,61,.06), 0 8px 24px -12px rgba(8,38,61,.18)',
      },
    },
  },
  plugins: [],
};
