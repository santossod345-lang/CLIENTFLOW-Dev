/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#667eea',
        secondary: '#764ba2',
        dark: '#1a1a2e',
        light: '#f5f7fa'
      }
    },
  },
  plugins: [],
}
