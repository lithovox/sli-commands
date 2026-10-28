<script lang="ts">
  import Dropzone from "../lib/Dropzone.svelte";
  import { download, type LoadedFile } from "../lib/files";
  import { t } from "../lib/i18n.svelte";
  import { callPython, PythonError } from "../lib/python";
  import { soils } from "../lib/state.svelte";

  interface Parameters {
    header: string[];
    rows: string[][];
    placeholders: [number, number][];
    csv: string;
  }

  interface Props {
    onuse: () => void;
  }

  let { onuse }: Props = $props();

  let file = $state<LoadedFile | undefined>();
  let parameters = $state<Parameters | undefined>();
  let error = $state<string | undefined>();

  async function load(files: LoadedFile[]) {
    file = files[0];
    parameters = undefined;
    error = undefined;
    try {
      parameters = (await callPython<Parameters>("parameters", [], [file.data])).result;
    } catch (e) {
      error = e instanceof PythonError || e instanceof Error ? e.message : String(e);
    }
  }

  function isPlaceholder(row: number, column: number): boolean {
    return !!parameters?.placeholders.some(([r, c]) => r === row && c === column);
  }

  function useForConversion() {
    soils.file = { name: "soils.csv", data: new TextEncoder().encode(parameters!.csv) };
    soils.edited = false;
    onuse();
  }
</script>

<div class="stack">
  <section class="card stack">
    <p class="muted">{t("parameters.intro")}</p>
    <Dropzone label={t("drop.sli.one")} accept=".sli" compact={!!file} onfiles={load} />
    {#if error}
      <div class="message error">{error}</div>
    {/if}
  </section>

  {#if parameters && file}
    <section class="card stack">
      <div class="row">
        <h2 class="mono">{file.name}</h2>
        {#if parameters.placeholders.length}
          <span class="badge warn">{parameters.placeholders.length} × {t("parameters.placeholder")}</span>
        {/if}
        <span class="spacer"></span>
        <button class="btn" onclick={() => download("soils.csv", parameters!.csv, "text/csv")}>{t("parameters.download")}</button>
        <button class="btn primary" onclick={useForConversion}>{t("tab.convert")} →</button>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              {#each parameters.header as column (column)}<th>{column}</th>{/each}
            </tr>
          </thead>
          <tbody>
            {#each parameters.rows as row, r (r)}
              <tr>
                {#each row as value, c (c)}
                  <td class:mono={c > 0} class:placeholder={isPlaceholder(r, c)}>{value}</td>
                {/each}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </section>
  {/if}
</div>

<style>
  td.placeholder {
    background: var(--warn-bg);
    color: var(--warn-color);
    font-weight: 600;
  }
</style>
