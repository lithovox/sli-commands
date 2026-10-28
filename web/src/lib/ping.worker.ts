/// <reference lib="webworker" />
// Only answers, used by the diagnostics to check that Web Workers may run.
onmessage = (event: MessageEvent<string>) => postMessage(`pong:${event.data}`);
