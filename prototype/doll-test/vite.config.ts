import { defineConfig } from 'vite'

function pagesBase(): string {
  const fromEnv = process.env.VITE_BASE
  if (typeof fromEnv === 'string' && fromEnv.trim().length > 0) return fromEnv.trim()
  return './'
}

export default defineConfig({
  base: pagesBase(),
  server: { host: '0.0.0.0', port: 5173 },
  build: { target: 'es2022', sourcemap: true },
})
