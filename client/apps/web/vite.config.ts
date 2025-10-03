import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  return {
    plugins: [react()],
    define: {
      'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
      'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY),
      'process.env.VITE_API_URL': JSON.stringify(env.VITE_API_URL || ''),
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@components': path.resolve(__dirname, './src/components'),
        '@screens': path.resolve(__dirname, './src/screens'),
        '@services': path.resolve(__dirname, './src/services'),
        '@store': path.resolve(__dirname, './src/store'),
        '@theme': path.resolve(__dirname, './src/theme'),
        '@assets': path.resolve(__dirname, './src/assets'),
        '@mock-data': path.resolve(__dirname, './src/mock-data'),
        'react-native': path.resolve(__dirname, './src/compat/react-native.ts'),
        'react-native-web$': path.resolve(__dirname, './src/compat/react-native-web.ts'),
      },
      extensions: ['.web.tsx', '.web.ts', '.mobile.tsx', '.mobile.ts', '.tsx', '.ts', '.jsx', '.js'],
    },
    optimizeDeps: {
      include: ['react-native-web'],
    },
    server: {
      host: '0.0.0.0',
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://api:8000',
          changeOrigin: true,
        },
      },
    },
  };
});