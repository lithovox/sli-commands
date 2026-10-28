/// <reference lib="webworker" />
// Runs the settlement Python package with Pyodide, off the main thread.
import type { PyodideAPI } from "pyodide";
import type { PyProxy } from "pyodide/ffi";
import type { InitResult, Request, Response, Status } from "./protocol";

// the Python package as text, the same files slicmd uses
const sources = import.meta.glob("../../../src/settlement/*.py", {
  query: "?raw",
  import: "default",
  eager: true,
}) as Record<string, string>;

const BOOTSTRAP = `
import json, sys
sys.path.insert(0, "/app")
from settlement.web import dispatch

def _call(function, args, files):
    return dispatch(function, json.loads(args), [f.to_bytes() for f in files])
`;

type Call = (fn: string, args: string, files: Uint8Array[]) => PyProxy;

let pyodide: PyodideAPI | undefined;
let call: Call | undefined;

function status(step: Status["step"]) {
  postMessage({ type: "status", step } satisfies Status);
}

async function init(indexURL: string): Promise<InitResult> {
  status("download");
  // served by the site itself from public/pyodide, never from a CDN
  const { loadPyodide } = (await import(/* @vite-ignore */ `${indexURL}pyodide.mjs`)) as typeof import("pyodide");
  status("start");
  pyodide = await loadPyodide({ indexURL });

  status("package");
  pyodide.FS.mkdirTree("/app/settlement");
  for (const [path, source] of Object.entries(sources)) {
    pyodide.FS.writeFile(`/app/settlement/${path.split("/").pop()}`, source);
  }
  pyodide.runPython(BOOTSTRAP);
  call = pyodide.globals.get("_call") as Call;
  return { python: pyodide.runPython("sys.version.split()[0]") as string, pyodide: pyodide.version };
}

function run(fn: string, args: unknown[], files: Uint8Array[]): Omit<Response, "id" | "type"> {
  if (!call) throw new Error("Python is not started");
  const proxy = call(fn, JSON.stringify(args), files);
  try {
    const [json, data] = proxy.toJs() as [string, Uint8Array | undefined];
    const response = JSON.parse(json);
    return data ? { ...response, data } : response;
  } finally {
    proxy.destroy();
  }
}

onmessage = async (event: MessageEvent<Request>) => {
  const request = event.data;
  let response: Response;
  try {
    if (request.type === "init") {
      response = { id: request.id, type: "result", ok: true, result: await init(request.indexURL) };
    } else {
      response = { id: request.id, type: "result", ...run(request.fn, request.args, request.files) } as Response;
    }
  } catch (e) {
    response = { id: request.id, type: "result", ok: false, error: e instanceof Error ? e.message : String(e) };
  }
  const transfer = response.ok && response.data ? [response.data.buffer as ArrayBuffer] : [];
  postMessage(response, transfer);
};
