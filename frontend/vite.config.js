import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@fullcalendar/react': '/src/vendor/fullcalendar/react.jsx',
      '@fullcalendar/daygrid': '/src/vendor/fullcalendar/daygrid.js',
      '@fullcalendar/timegrid': '/src/vendor/fullcalendar/timegrid.js',
      '@fullcalendar/interaction': '/src/vendor/fullcalendar/interaction.js',
    },
  },
});
