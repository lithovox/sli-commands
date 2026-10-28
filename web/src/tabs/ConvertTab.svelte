<script lang="ts">
  import { untrack } from "svelte";
  import Dropzone from "../lib/Dropzone.svelte";
  import SoilsTable from "../lib/SoilsTable.svelte";
  import { download, type LoadedFile } from "../lib/files";
  import { t, type Key } from "../lib/i18n.svelte";
  import { callPython, PythonError } from "../lib/python";
  import { python, soils } from "../lib/state.svelte";
  import { createZip } from "../lib/zip";

  interface Inspection {
    model: string;
    action: "kj2bj" | "bj2kj" | null;
    calculation_type: string;
    strain_type: string;
    soils: string[];
  }

  interface Converted {
    action: string;
    name: string;
    notices: string[];
    data: Uint8Array;
  }

  interface Failure {
    message: string;
    problems: string[];
  }

  interface Table {
    header: string[];
    rows: string[][];
    problems: string[];
  }

  interface Calculation {
    id: number;
    file: LoadedFile;
    inspection?: Inspection;
    converted?: Converted;
    error?: Failure;
  }

  let nextId = 0;
  let calculations = $state<Calculation[]>([]);
  let table = $state<Table | undefined>();
  let soilsError = $state<Failure | undefined>();
  let busy = $state(false);

  function failure(e: unknown): Failure {
    if (e instanceof PythonError) return { message: e.message, problems: e.problems };
    return { message: e instanceof Error ? e.message : String(e), problems: [] };
  }

  // read the soils file whenever it changes, also when it comes from the Soil parameters tab
  $effect(() => {
    const file = soils.file;
    soilsError = undefined;
    // results made with another soils file are no longer valid, untracked so converting does not rerun this
    untrack(() => calculations.forEach((c) => (c.converted = undefined)));
    if (!file) {
      table = undefined;
      return;
    }
    callPython<Table>("soils_table", [], [file.data]).then(
      ({ result }) => (table = result),
      (e) => {
        table = undefined;
        soilsError = failure(e);
      },
    );
  });

  let codes = $derived(table?.rows.map((row) => row[0].trim()).filter((code) => code));

  function loadSoils(files: LoadedFile[]) {
    soils.file = files[0];
    soils.edited = false;
  }

  // an edit in the table becomes the soils file used for converting
  function editSoils(rows: string[][]) {
    const csv = [table!.header, ...rows].map((row) => row.join(";")).join("\n") + "\n";
    soils.file = { name: soils.file!.name, data: new TextEncoder().encode(csv) };
    soils.edited = true;
  }

  async function addCalculations(files: LoadedFile[]) {
    for (const file of files) {
      const calculation: Calculation = { id: nextId++, file };
      calculations.push(calculation);
      const item = calculations[calculations.length - 1];
      try {
        item.inspection = (await callPython<Inspection>("inspect_calculation", [], [file.data])).result;
      } catch (e) {
        item.error = failure(e);
      }
    }
  }

  function missing(calculation: Calculation): string[] {
    if (!codes || !calculation.inspection) return [];
    return calculation.inspection.soils.filter((s) => !codes!.includes(s));
  }

  function convertible(calculation: Calculation): boolean {
    return !!calculation.inspection?.action && !calculation.error && missing(calculation).length === 0;
  }

  let ready = $derived(!!table && table.problems.length === 0 && python.state === "ready");
  // soils used by the calculations that the soils file does not have, once each
  let allMissing = $derived([...new Set(calculations.flatMap((c) => missing(c)))]);
  let toConvert = $derived(calculations.filter((c) => convertible(c) && !c.converted));
  let converted = $derived(calculations.filter((c) => c.converted));

  async function convertAll() {
    busy = true;
    for (const calculation of toConvert) {
      try {
        const { result, data } = await callPython<Omit<Converted, "data">>(
          "convert_calculation",
          [calculation.file.name],
          [calculation.file.data, soils.file!.data],
        );
        calculation.converted = { ...result, data: data! };
      } catch (e) {
        calculation.error = failure(e);
      }
    }
    busy = false;
  }

  function downloadAll() {
    const zip = createZip(converted.map((c) => ({ name: c.converted!.name, data: c.converted!.data })));
    download("slicmd.zip", zip, "application/zip");
  }

  // the warnings of settlement.convert, other texts are shown as they are
  const NOTICES: Record<string, Key> = {
    "the calculation uses Terzaghi, Darcy is preferred": "notice.terzaghi",
    "strain type changed from Natural to Linear (required for NEN-Bjerrum)": "notice.strain",
  };

  const notice = (text: string) => (NOTICES[text] ? t(NOTICES[text]) : text);

  function modelName(model: string): string {
    return model === "NEN - Koppejan" ? t("model.koppejan") : model === "NEN - Bjerrum" ? t("model.bjerrum") : model;
  }
</script>

<div class="stack">
  <p class="muted">{t("convert.intro")}</p>
  <section class="card stack">
    <div class="row">
      <h2>1. {t("convert.soils")}</h2>
      {#if soils.file}
        <span class="badge accent mono">{soils.file.name}</span>
        {#if codes}<span class="badge ok">{t("convert.soils.count", { n: codes.length })}</span>{/if}
        {#if soils.edited}<span class="badge warn">{t("soils.edited")}</span>{/if}
        <span class="spacer"></span>
        <button class="btn" onclick={() => download(soils.file!.name, soils.file!.data, "text/csv")}>
          {t("soils.download")}
        </button>
      {/if}
    </div>
    <Dropzone
      label={t("drop.csv")}
      accept=".csv"
      compact={!!soils.file}
      onfiles={loadSoils}
    />
    {#if soilsError}
      <div class="message error">
        {soilsError.problems.length ? soilsError.message.split("\n")[0] : soilsError.message}
        {#if soilsError.problems.length}
          <ul>
            {#each soilsError.problems as problem, i (i)}<li>{problem}</li>{/each}
          </ul>
        {/if}
      </div>
    {:else if !soils.file}
      <p class="muted small">{t("convert.soils.hint")}</p>
    {/if}
    {#if table}
      <p class="muted small">{t("soils.intro")}</p>
      <SoilsTable header={table.header} rows={table.rows} missing={allMissing} onchange={editSoils} />
      {#if table.problems.length}
        <div class="message error">
          {t("soils.problems")}
          <ul>
            {#each table.problems as problem, i (i)}<li>{problem}</li>{/each}
          </ul>
        </div>
      {/if}
    {/if}
  </section>

  <section class="card stack">
    <div class="row">
      <h2>2. {t("convert.calculations")}</h2>
      <span class="spacer"></span>
      {#if calculations.length}
        <button class="link-btn" onclick={() => (calculations = [])}>{t("convert.clear")}</button>
      {/if}
    </div>
    <Dropzone
      label={t("drop.sli")}
      accept=".sli"
      multiple
      compact={calculations.length > 0}
      onfiles={addCalculations}
    />

    {#each calculations as calculation (calculation.id)}
      {@const lacking = missing(calculation)}
      <article class="calculation">
        <div class="row">
          <strong class="mono">{calculation.file.name}</strong>
          {#if calculation.inspection}
            {#if calculation.inspection.action}
              <span class="badge accent">
                {calculation.inspection.action === "kj2bj"
                  ? `${t("model.koppejan")} → ${t("model.bjerrum")}`
                  : `${t("model.bjerrum")} → ${t("model.koppejan")}`}
              </span>
            {:else}
              <span class="badge error">{modelName(calculation.inspection.model)}</span>
            {/if}
            <span class="badge">{calculation.inspection.calculation_type}</span>
            <span class="badge">{calculation.inspection.strain_type}</span>
          {/if}
          <span class="spacer"></span>
          {#if calculation.converted}
            <button class="btn" onclick={() => download(calculation.converted!.name, calculation.converted!.data)}>
              {t("convert.download")}
            </button>
          {/if}
          <button
            class="link-btn"
            aria-label={t("remove")}
            onclick={() => (calculations = calculations.filter((c) => c.id !== calculation.id))}>✕</button
          >
        </div>

        {#if calculation.inspection && !calculation.inspection.action}
          <div class="message error">{t("convert.no.model")}</div>
        {/if}

        {#if calculation.inspection}
          <div class="soils">
            {#each calculation.inspection.soils as soil (soil)}
              <span class="badge" class:error={lacking.includes(soil)} class:ok={codes && !lacking.includes(soil)}>
                {soil}
              </span>
            {/each}
          </div>
          {#if lacking.length}
            <div class="message error">{t("convert.missing")}: {lacking.join(", ")}</div>
          {/if}
        {/if}

        {#if calculation.error}
          <div class="message error">
            {calculation.error.problems.length ? calculation.error.problems[0] : calculation.error.message}
            {#if calculation.error.problems.length > 1}
              <ul>
                {#each calculation.error.problems.slice(1) as problem, i (i)}<li>{problem.trim()}</li>{/each}
              </ul>
            {/if}
          </div>
        {/if}

        {#if calculation.converted}
          <div class="message ok">{t("convert.done", { name: calculation.converted.name })}</div>
          {#each calculation.converted.notices as text, i (i)}
            <div class="message warn">{notice(text)}</div>
          {/each}
        {/if}
      </article>
    {/each}

    {#if calculations.length}
      <div class="row">
        <button class="btn primary" disabled={!ready || busy || toConvert.length === 0} onclick={convertAll}>
          {toConvert.length > 1 ? t("convert.run.all", { n: toConvert.length }) : t("convert.run")}
        </button>
        {#if converted.length > 1}
          <button class="btn" onclick={downloadAll}>{t("convert.download.all")}</button>
        {/if}
        {#if !codes}
          <span class="muted small">{t("convert.waiting")}</span>
        {/if}
      </div>
    {/if}
  </section>
</div>

<style>
  .calculation {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    padding: 0.9rem 1rem;
    border: 1px solid var(--border-color);
    border-radius: 10px;
  }

  .soils {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
  }

  .soils .badge {
    font-weight: 500;
  }
</style>
