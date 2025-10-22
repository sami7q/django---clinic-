/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Cairo"', 'ui-sans-serif', 'system-ui'],
      },
      colors: {
        clinic: {
          light: '#E8F3FF',
          DEFAULT: '#3B82F6',
          dark: '#1E40AF',
        },
      },
      boxShadow: {
        card: '0 4px 20px rgba(0, 0, 0, 0.05)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
