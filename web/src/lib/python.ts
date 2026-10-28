// The page side of the Python worker.
import type { InitResult, InitStep, Request, Response, Status } from "./protocol";

export class PythonError extends Error {
  constructor(
    message: string,
    readonly problems: string[] = [],
  ) {
    super(message);
  }
}

export interface CallResult<T> {
  result: T;
  data?: Uint8Array;
}

// Omit for each member of the Request union
type Outgoing = Request extends infer R ? (R extends Request ? Omit<R, "id"> : never) : never;

let worker: Worker | undefined;
let nextId = 1;
const pending = new Map<number, (response: Response) => void>();
let statusListener: ((step: InitStep) => void) | undefined;
let started: Promise<InitResult> | undefined;

function getWorker(): Worker {
  if (!worker) {
    worker = new Worker(new URL("./python.worker.ts", import.meta.url), { type: "module" });
    worker.onmessage = (event: MessageEvent<Response | Status>) => {
      const message = event.data;
      if (message.type === "status") {
        statusListener?.(message.step);
      } else {
        pending.get(message.id)?.(message);
        pending.delete(message.id);
      }
    };
  }
  return worker;
}

function send(request: Outgoing, transfer: Transferable[] = []): Promise<Response> {
  const id = nextId++;
  return new Promise((resolve) => {
    pending.set(id, resolve);
    getWorker().postMessage({ ...request, id }, transfer);
  });
}

/** Starts Python once, later calls return the same promise. */
export function startPython(onStatus?: (step: InitStep) => void): Promise<InitResult> {
  statusListener = onStatus;
  started ??= (async () => {
    const indexURL = new URL("pyodide/", document.baseURI).href;
    const response = await send({ type: "init", indexURL });
    if (!response.ok) throw new PythonError(response.error);
    return response.result as InitResult;
  })();
  return started;
}

/** Stops the worker, the next call starts Python again (used by the diagnostics). */
export function resetPython() {
  worker?.terminate();
  worker = undefined;
  started = undefined;
  for (const [id, resolve] of pending) {
    resolve({ id, type: "result", ok: false, error: "Python was restarted" });
  }
  pending.clear();
}

/** Calls a function of settlement.web, files are passed as bytes after args. */
export async function callPython<T>(fn: string, args: unknown[] = [], files: Uint8Array[] = []): Promise<CallResult<T>> {
  await startPython();
  // copies, so the caller keeps its own buffers
  const copies = files.map((f) => f.slice());
  const response = await send(
    { type: "call", fn, args, files: copies },
    copies.map((f) => f.buffer),
  );
  if (!response.ok) throw new PythonError(response.error, response.problems ?? []);
  return { result: response.result as T, data: response.data };
}
