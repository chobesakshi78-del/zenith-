/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        page: '#F8FAFC',
        card: '#FFFFFF',
        navy: {
          950: '#F8FAFC',
          900: '#FFFFFF',
          850: '#F1F5F9',
          800: '#E2E8F0',
          700: '#CBD5E1',
          600: '#94A3B8',
        },
        risk: {
          high: '#DC2626',
          medium: '#F59E0B',
          low: '#16A34A',
          insider: '#7C3AED'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      }
    },
  },
  plugins: [],
}
