import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";

const MOCK_SERVER = "http://127.0.0.1:8787";
const PREVIEW_PORT = 4173;
const API_PREFIX = "/api";

type Environment = Record<string, string | undefined>;

/**
 * Returns the value of an entry of the environment, or undefined when the entry is missing or empty,
 * so an entry left empty in a copy of .env.example counts as not set.
 */
function readEntry(env: Environment, name: string): string | undefined {
  const value = env[name]?.trim();
  return value === undefined || value === "" ? undefined : value;
}

/**
 * Builds the proxy of the programming interface. Every path under /api goes to the address of VITE_API_PROXY_TARGET,
 * the service, with the address of the person in X-Forwarded-For. The paths listed in VITE_API_MOCK_PATHS, separated
 * by commas, go to the mock server at VITE_API_MOCK_TARGET instead: the operations the service does not answer yet.
 * A listed path stands before /api, because the first entry that matches a request takes it.
 */
function buildApiProxy(env: Environment) {
  const service = { target: readEntry(env, "VITE_API_PROXY_TARGET") ?? MOCK_SERVER, changeOrigin: true, xfwd: true };
  const mock = { target: readEntry(env, "VITE_API_MOCK_TARGET") ?? MOCK_SERVER, changeOrigin: true };
  const mockPaths = (readEntry(env, "VITE_API_MOCK_PATHS") ?? "")
    .split(",")
    .map((path) => path.trim())
    .filter((path) => path.startsWith(`${API_PREFIX}/`));
  return { ...Object.fromEntries(mockPaths.map((path) => [path, mock])), [API_PREFIX]: service };
}

/**
 * The development server and the preview pass the programming interface on as buildApiProxy says, by default
 * all of it to the mock server of this project. The entries are read from the environment of the process,
 * and then from the file .env.local of this directory, which is never committed; .env.example lists them.
 * The build has no proxy: the application calls the host it was loaded from.
 *
 * The preview is also how a server of the team serves the built application: FRONTEND_HOST and FRONTEND_PORT
 * set the address it listens on, and it answers under any host name.
 */
export default defineConfig(({ mode }) => {
  const env: Environment = { ...loadEnv(mode, process.cwd(), ["VITE_", "FRONTEND_"]), ...process.env };
  const apiProxy = buildApiProxy(env);
  return {
    plugins: [react(), tailwindcss()],
    server: { proxy: apiProxy },
    preview: { proxy: apiProxy, host: readEntry(env, "FRONTEND_HOST"), port: Number(readEntry(env, "FRONTEND_PORT") ?? PREVIEW_PORT), allowedHosts: true as const },
    test: { environment: "node", include: ["src/**/*.test.ts", "scripts/**/*.test.ts"] },
  };
});
