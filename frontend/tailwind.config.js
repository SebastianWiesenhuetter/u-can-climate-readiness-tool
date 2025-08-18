/** @type {import('tailwindcss').Config} */
export default {
  prefix: 'tw-',              //  all tailwind utilities must start with tw-
  corePlugins: { preflight: false }, //  no reset; don’t touch defaults
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brandBlue: '#3679C3',
        brandGreen: 'rgb(72, 125, 69)',
        brandTertiary: '#003399',
        siteBg: 'rgb(248, 247, 243)',
      },
      fontFamily: { nunito: ['"Nunito Sans"', 'sans-serif'] },
    },
  },
  plugins: [],
}
