import { readFileSync } from "node:fs";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import { defineConfig } from "vitest/config";
import { SECURITY_HEADERS } from "./security-headers.ts";

// the version is set in pyproject.toml only
const pyproject = readFileSync(new URL("../pyproject.toml", import.meta.url), "utf-8");
const version = /^version\s*=\s*"([^"]+)"/m.exec(pyproject)?.[1] ?? "unknown";

export default defineConfig({
  plugins: [svelte()],
  // relative paths, so the site also works from a sub folder of the server
  base: "./",
  define: {
    __APP_VERSION__: JSON.stringify(version),
  },
  server: {
    // the worker imports the Python package from ../src/settlement
    fs: { allow: [".."] },
  },
  build: {
    target: "es2022",
    // no inline polyfill script, the Content Security Policy only allows scripts from the site itself
    modulePreload: { polyfill: false },
  },
  // the same headers as the published site, see deploy/sli.caddy
  preview: {
    headers: SECURITY_HEADERS,
  },
  worker: {
    format: "es",
  },
  test: {
    include: ["src/**/*.test.ts", "*.test.ts"],
  },
});
