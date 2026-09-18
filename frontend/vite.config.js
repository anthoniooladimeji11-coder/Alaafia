import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Standalone Àlááfìà marketing + admin site. The two page components
// (AlaafiaPage, AlaafiaAdminPage) were lifted verbatim from the Ìyàwó
// frontend; they carry their own <style> blocks and only import React.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:4000',
        changeOrigin: true,
      },
    },
  },
});
