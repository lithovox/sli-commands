// Messages between the page and the Python worker.

export type Request =
  | { id: number; type: "init"; indexURL: string }
  | { id: number; type: "call"; fn: string; args: unknown[]; files: Uint8Array[] };

export type Response =
  | { id: number; type: "result"; ok: true; result: unknown; data?: Uint8Array }
  | { id: number; type: "result"; ok: false; error: string; problems?: string[] | null };

export type InitStep = "download" | "start" | "package";

export type Status = { type: "status"; step: InitStep };

export interface InitResult {
  python: string;
  pyodide: string;
}
