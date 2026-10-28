import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { SECURITY_HEADERS } from "./security-headers";

// the headers set in the "header { ... }" block of the Caddy config
function caddyHeaders(config: string): Record<string, string> {
  const block = /^\s*header\s*\{\n([\s\S]*?)^\s*\}/m.exec(config);
  if (!block) throw new Error("no header block in the Caddy config");
  const headers: Record<string, string> = {};
  for (const line of block[1].split("\n")) {
    const match = /^\s*([A-Za-z-]+)\s+"(.*)"\s*$/.exec(line);
    if (match) headers[match[1]] = match[2];
  }
  return headers;
}

describe("deploy/sli.caddy", () => {
  const config = readFileSync(new URL("../deploy/sli.caddy", import.meta.url), "utf-8");

  it("sends the same security headers as vite preview", () => {
    const headers = caddyHeaders(config);
    for (const [name, value] of Object.entries(SECURITY_HEADERS)) {
      expect(headers[name], name).toBe(value);
    }
  });
});
