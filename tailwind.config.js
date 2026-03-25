/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#271310",
        'primary-container': "#3E2723",
        surface: "#f9f9f9",
        'surface-container-lowest': "#ffffff",
        'surface-container-low': "#f3f3f3",
        'surface-container': "#eeeeee",
        'surface-container-high': "#e8e8e8",
        'surface-container-highest': "#e2e2e2",
        'on-surface': "#1a1c1c",
        'on-surface-variant': "#504442",
        outline: "#827472",
        'outline-variant': "#d3c3c0",
        error: "#ba1a1a",
        secondary: "#376a10",
        'secondary-container': "#b6f48a",
      },
      fontFamily: {
        sans: ['Manrope', 'sans-serif'],
        display: ['Space Grotesk', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
