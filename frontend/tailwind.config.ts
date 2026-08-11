import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        brand: {
          50: "#f0f7ff",
          100: "#e0effe",
          200: "#bae0fd",
          300: "#7cc8fc",
          400: "#38aef7",
          500: "#0e95e8",
          600: "#0277c7",
          700: "#035fa1",
          800: "#075185",
          900: "#0c436e",
          950: "#082b49",
        },
      },
    },
  },
  plugins: [],
};
export default config;
