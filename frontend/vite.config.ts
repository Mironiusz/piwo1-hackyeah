import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

const apiProxy = { "/api": { target: process.env.VITE_API_PROXY_TARGET ?? "http://127.0.0.1:8787", changeOrigin: true } };

/**
 * The development server and the preview pass the programming interface to the address of
 * VITE_API_PROXY_TARGET, by default the mock server of this project. The build has no proxy:
 * the application calls the host it was loaded from.
 */
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { proxy: apiProxy },
  preview: { proxy: apiProxy },
  test: { environment: "node", include: ["src/**/*.test.ts", "scripts/**/*.test.ts"] },
});
