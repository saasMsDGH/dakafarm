import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  define: {
    global: 'window',
  },
  server: {
    port: 3000,
  },
  css: {
    preprocessorOptions: {
      scss: {
        quietDeps: true,
        silenceDeprecations: [
          'legacy-js-api', 
          'import', 
          'global-builtin', 
          'color-functions', 
          'slash-div', 
          'if-function', 
          'abs-percent',
          'function-units'
        ]
      }
    }
  }
});
