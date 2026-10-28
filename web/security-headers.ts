// The security headers of the site. deploy/sli.caddy sends the same
// headers (a unit test checks this), vite preview uses them so the browser
// tests run under the same rules as the published site.

export const CONTENT_SECURITY_POLICY = [
  "default-src 'self'",
  // WebAssembly needs 'wasm-unsafe-eval', no other script source is allowed
  "script-src 'self' 'wasm-unsafe-eval'",
  "style-src 'self'",
  "img-src 'self' data:",
  "connect-src 'self'",
  "worker-src 'self'",
  "object-src 'none'",
  "base-uri 'none'",
  "form-action 'none'",
  "frame-ancestors 'none'",
].join("; ");

export const SECURITY_HEADERS: Record<string, string> = {
  "Content-Security-Policy": CONTENT_SECURITY_POLICY,
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "no-referrer",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
  "Cross-Origin-Opener-Policy": "same-origin",
};
