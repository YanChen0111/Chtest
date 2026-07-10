import vue from '@vitejs/plugin-vue';
import { defineConfig, loadEnv } from 'vite';

function normalizeApiProxyTarget(value: string | undefined): string | null {
  if (!value || value.startsWith('/')) {
    return null;
  }
  const url = new URL(value);
  if (url.pathname === '/api' || url.pathname === '/api/') {
    url.pathname = '/';
  }
  url.search = '';
  url.hash = '';
  return url.toString().replace(/\/$/, '');
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const apiProxyTarget =
    normalizeApiProxyTarget(env.VITE_API_PROXY_TARGET) ??
    normalizeApiProxyTarget(env.VITE_API_BASE_URL) ??
    'http://127.0.0.1:8000';

  return {
    plugins: [vue()],
    server: {
      proxy: {
        '/api': apiProxyTarget,
      },
    },
    test: {
      environment: 'jsdom',
      setupFiles: ['./src/test/setup.ts'],
    },
  };
});
