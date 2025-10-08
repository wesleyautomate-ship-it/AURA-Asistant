/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        aura: {
          primary: "#3B82F6",
          secondary: "#10B981",
          accent: "#F59E0B",
          background: "#F9FAFB",
          text: "#111827"
        }
      },
      spacing: {
        '128': '32rem',
        '144': '36rem'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    },
  },
  plugins: [],
}
