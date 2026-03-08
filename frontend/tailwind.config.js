/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#4f46e5",
        accent: "#10b981",
        slateBrand: "#334155",
      },
    },
  },
  plugins: [],
};
