<script lang="ts">
  import Chart, { type Series } from "../lib/Chart.svelte";
  import Dropzone from "../lib/Dropzone.svelte";
  import { download, type LoadedFile } from "../lib/files";
  import { t } from "../lib/i18n.svelte";
  import { callPython, PythonError } from "../lib/python";
  import { compareVerticals, formatPosition, type Mismatch } from "../lib/verticals";

  interface Vertical {
    number: number;
    x: number;
    z: number;
    series: [number, number][];
  }

  interface ResultFile {
    id: number;
    name: string;
    color: string;
    verticals: Vertical[];
  }

  // distinguishable in the light and the dark theme
  const COLORS = ["#1f77b4", "#d95f02", "#2ca02c", "#9467bd", "#d62728", "#17becf", "#8c564b", "#e377c2"];

  let nextId = 0;
  let files = $state<ResultFile[]>([]);
  // files that could not be read or compared, with the reason
  let rejected = $state<{ name: string; message: string }[]>([]);
  let vertical = $state(1);
  let showTable = $state(false);

  function describe(mismatch: Mismatch, reference: ResultFile): string {
    if (mismatch.kind === "count") {
      return t("results.mismatch.count", { found: mismatch.found, expected: mismatch.expected, reference: reference.name });
    }
    return t("results.mismatch.position", {
      n: mismatch.number,
      found: formatPosition(mismatch.found),
      expected: formatPosition(mismatch.expected),
      reference: reference.name,
    });
  }

  async function add(loaded: LoadedFile[]) {
    rejected = [];
    for (const file of loaded) {
      try {
        const { result } = await callPython<{ verticals: Vertical[] }>("results", [], [file.data]);
        // every file is compared with the first one
        const reference = files[0];
        const mismatch = reference && compareVerticals(reference.verticals, result.verticals);
        if (mismatch) {
          rejected.push({ name: file.name, message: describe(mismatch, reference) });
          continue;
        }
        const used = new Set(files.map((f) => f.color));
        const color = COLORS.find((c) => !used.has(c)) ?? COLORS[files.length % COLORS.length];
        files.push({ id: nextId++, name: file.name, color, verticals: result.verticals });
      } catch (e) {
        rejected.push({ name: file.name, message: e instanceof PythonError || e instanceof Error ? e.message : String(e) });
      }
    }
    if (!verticals.some((v) => v.number === vertical)) vertical = verticals[0]?.number ?? 1;
  }

  function remove(file: ResultFile) {
    files = files.filter((f) => f.id !== file.id);
  }

  // all files have the same verticals, the first file names them
  let verticals = $derived(files[0]?.verticals ?? []);
  let current = $derived(verticals.find((v) => v.number === vertical));

  let shown = $derived(
    files.flatMap((file) => {
      const v = file.verticals.find((v) => v.number === vertical);
      return v ? [{ file, points: v.series }] : [];
    }),
  );
  let series = $derived<Series[]>(
    shown.map(({ file, points }) => ({ key: String(file.id), label: file.name, color: file.color, points })),
  );

  const verticalLabel = (v: Vertical) => t("results.vertical", { n: v.number, x: Number(v.x.toFixed(3)) });

  function downloadCsv() {
    const lines = ["file;vertical;time;settlement"];
    for (const { file, points } of shown) {
      for (const [time, settlement] of points) {
        lines.push(`${file.name};${vertical};${time.toFixed(7)};${settlement.toFixed(7)}`);
      }
    }
    download(`time-settlement-vertical-${vertical}.csv`, lines.join("\n") + "\n", "text/csv");
  }
</script>

<div class="stack">
  <p class="muted">{t("results.intro")}</p>

  <section class="card stack">
    <div class="row">
      <h2>{t("results.files")}</h2>
      {#if files.length}<span class="badge accent">{t("results.verticals.count", { n: verticals.length })}</span>{/if}
    </div>
    <Dropzone label={t("drop.sld")} accept=".sld" multiple compact={files.length > 0} onfiles={add} />

    {#each rejected as item (item.name)}
      <div class="message error"><strong class="mono">{item.name}</strong>: {item.message}</div>
    {/each}

    {#if files.length}
      <ul class="files">
        {#each files as file (file.id)}
          <li>
            <svg width="22" height="10" aria-hidden="true"><line x1="0" y1="5" x2="22" y2="5" stroke={file.color} stroke-width="3" /></svg>
            <span class="mono">{file.name}</span>
            <span class="spacer"></span>
            <button
              type="button"
              class="icon-btn btn-danger"
              title={t("results.remove")}
              aria-label={`${t("results.remove")} ${file.name}`}
              onclick={() => remove(file)}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </li>
        {/each}
      </ul>
    {/if}
  </section>

  {#if files.length}
    <section class="card stack">
      <div class="row">
        <label class="field" for="vertical-select">{t("results.vertical.select")}</label>
        <select id="vertical-select" bind:value={vertical}>
          {#each verticals as v (v.number)}
            <option value={v.number}>{verticalLabel(v)}</option>
          {/each}
        </select>
        {#if current}<span class="muted small">{formatPosition(current)}</span>{/if}
        <span class="spacer"></span>
        <button class="btn" onclick={() => (showTable = !showTable)}>{showTable ? t("results.chart") : t("results.table")}</button>
        <button class="btn" onclick={downloadCsv}>{t("results.download")}</button>
      </div>

      {#if showTable}
        <div class="tables">
          {#each shown as { file, points } (file.id)}
            <div class="table-wrap">
              <table>
                <thead>
                  <tr><th colspan="2">{file.name}</th></tr>
                  <tr><th>{t("results.time")}</th><th>{t("results.settlement")}</th></tr>
                </thead>
                <tbody>
                  {#each points as [time, settlement], i (i)}
                    <tr><td class="mono">{time.toFixed(7)}</td><td class="mono">{settlement.toFixed(7)}</td></tr>
                  {/each}
                </tbody>
              </table>
            </div>
          {/each}
        </div>
      {:else}
        <Chart {series} xLabel={t("results.time")} yLabel={t("results.settlement")} />
      {/if}
    </section>
  {/if}
</div>

<style>
  .files {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .files li {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 4px 4px 10px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    font-size: 0.88rem;
  }

  .field {
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 500;
  }

  select {
    padding: 7px 10px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background: var(--bg-panel);
    color: var(--text-primary);
    font-size: 0.88rem;
    outline: none;
  }

  select:focus {
    border-color: var(--color-teal);
    box-shadow: 0 0 0 3px var(--color-teal-soft);
  }

  .tables {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 1rem;
    max-height: 520px;
    overflow-y: auto;
  }
</style>
