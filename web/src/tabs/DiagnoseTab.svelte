<script lang="ts">
  import { onMount } from "svelte";
  import { t, type Key } from "../lib/i18n.svelte";
  import { callPython, PythonError, resetPython, startPython } from "../lib/python";
  import { loadPython, python } from "../lib/state.svelte";
  // dummy test data from the repository, nothing real
  import exampleSoils from "../../../examples/soils.csv?raw";
  import koppejan from "../../../tests/fixtures/koppejan.sli?raw";
  import terzaghi from "../../../tests/fixtures/terzaghi.sld?raw";

  type State = "waiting" | "running" | "ok" | "failed";

  interface Step {
    key: Key;
    state: State;
    detail: string;
    ms?: number;
  }

  const KEYS: Key[] = [
    "diagnose.webassembly",
    "diagnose.worker",
    "diagnose.pyodide",
    "diagnose.package",
    "diagnose.convert",
    "diagnose.results",
  ];

  let steps = $state<Step[]>(KEYS.map((key) => ({ key, state: "waiting", detail: "" })));
  let running = $state(false);
  let copied = $state(false);

  const bytes = (text: string) => new TextEncoder().encode(text);

  function pingWorker(): Promise<string> {
    return new Promise((resolve, reject) => {
      const worker = new Worker(new URL("../lib/ping.worker.ts", import.meta.url), { type: "module" });
      const timer = setTimeout(() => reject(new Error("no answer within 5 s")), 5000);
      worker.onmessage = (e) => {
        clearTimeout(timer);
        worker.terminate();
        resolve(String(e.data));
      };
      worker.onerror = (e) => {
        clearTimeout(timer);
        worker.terminate();
        reject(new Error(e.message || "the worker could not be started"));
      };
      worker.postMessage("slicmd");
    });
  }

  // each check returns a short detail, or throws
  const CHECKS: Record<string, () => Promise<string>> = {
    "diagnose.webassembly": async () => {
      // the smallest valid module: magic number and version
      const valid = typeof WebAssembly === "object" && WebAssembly.validate(new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0]));
      if (!valid) throw new Error("WebAssembly is not available or disabled in this browser");
      return "OK";
    },
    "diagnose.worker": pingWorker,
    "diagnose.pyodide": async () => {
      resetPython();
      loadPython();
      const info = await startPython();
      return `Python ${info.python}, Pyodide ${info.pyodide}`;
    },
    "diagnose.package": async () => {
      const { result } = await callPython<{ model: string; soils: string[] }>("inspect_calculation", [], [bytes(koppejan)]);
      return `${result.model}, ${result.soils.length} soils`;
    },
    "diagnose.convert": async () => {
      const { result, data } = await callPython<{ name: string }>(
        "convert_calculation",
        ["koppejan.sli"],
        [bytes(koppejan), bytes(exampleSoils)],
      );
      if (!data?.length) throw new Error("no output");
      return `${result.name}, ${data.length} bytes`;
    },
    "diagnose.results": async () => {
      const { result } = await callPython<{ verticals: { series: unknown[] }[] }>("results", [], [bytes(terzaghi)]);
      return `${result.verticals.length} verticals, ${result.verticals[0].series.length} time steps`;
    },
  };

  async function run() {
    running = true;
    copied = false;
    for (const step of steps) Object.assign(step, { state: "waiting", detail: "", ms: undefined });
    let failed = false;
    for (const step of steps) {
      if (failed) break;
      step.state = "running";
      const start = performance.now();
      try {
        step.detail = await CHECKS[step.key]();
        step.state = "ok";
      } catch (e) {
        step.detail = e instanceof PythonError || e instanceof Error ? e.message : String(e);
        step.state = "failed";
        failed = true;
      }
      step.ms = Math.round(performance.now() - start);
    }
    running = false;
  }

  function report(): string {
    return [
      `slicmd ${__APP_VERSION__} diagnostics, ${new Date().toISOString()}`,
      `${t("diagnose.browser")}: ${navigator.userAgent}`,
      `URL: ${location.href}`,
      ...steps.map((s) => `[${s.state === "ok" ? "OK" : s.state.toUpperCase()}] ${t(s.key)}: ${s.detail}${s.ms !== undefined ? ` (${s.ms} ms)` : ""}`),
    ].join("\n");
  }

  async function copyReport() {
    await navigator.clipboard.writeText(report());
    copied = true;
  }

  onMount(run);
</script>

<section class="card stack">
  <p class="muted">{t("diagnose.intro")}</p>
  <ol class="steps">
    {#each steps as step (step.key)}
      <li class={step.state}>
        <span class="icon" aria-hidden="true">
          {step.state === "ok" ? "✓" : step.state === "failed" ? "✗" : step.state === "running" ? "…" : "·"}
        </span>
        <div>
          <div>{t(step.key)}</div>
          {#if step.detail}<div class="small mono detail">{step.detail}</div>{/if}
        </div>
        <span class="spacer"></span>
        {#if step.ms !== undefined}<span class="muted small">{step.ms} ms</span>{/if}
      </li>
    {/each}
  </ol>
  <div class="row">
    <button class="btn primary" disabled={running} onclick={run}>{t("diagnose.run")}</button>
    <button class="btn" disabled={running} onclick={copyReport}>{copied ? "✓" : t("diagnose.copy")}</button>
    <span class="spacer"></span>
    <span class="muted small mono">{python.info ? `Python ${python.info.python} · Pyodide ${python.info.pyodide}` : ""}</span>
  </div>
  <p class="muted small mono">{t("diagnose.browser")}: {navigator.userAgent}</p>
</section>

<style>
  .steps {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .steps li {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
    background: var(--bg-panel);
  }

  .icon {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    width: 1.6rem;
    height: 1.6rem;
    flex: none;
    border-radius: 50%;
    font-weight: 700;
    background: var(--border-color);
  }

  li.ok .icon {
    background: var(--ok-bg);
    color: var(--ok-color);
  }

  li.failed {
    background: var(--danger-bg);
  }

  li.failed .icon {
    background: var(--danger-color);
    color: #fff;
  }

  li.running .icon {
    background: var(--color-teal-soft);
    color: var(--color-teal);
  }

  .detail {
    color: var(--text-secondary);
    word-break: break-word;
  }

  li.failed .detail {
    color: var(--danger-color);
  }
</style>
