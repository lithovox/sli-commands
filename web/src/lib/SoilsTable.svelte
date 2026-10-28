<script lang="ts">
  import { t } from "./i18n.svelte";

  interface Props {
    header: string[];
    rows: string[][];
    /** soil codes the loaded calculations use but the table does not have */
    missing?: string[];
    onchange: (rows: string[][]) => void;
  }

  let { header, rows, missing = [], onchange }: Props = $props();

  // a number as the soils file accepts it, with a decimal point or comma
  const NUMBER = /^[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?$/;

  const valid = (column: number, value: string) => (column === 0 ? value.trim() !== "" : NUMBER.test(value.trim()));

  // ';' is the separator of the soils file
  const clean = (value: string) => value.replaceAll(";", "");

  function edit(row: number, column: number, value: string) {
    onchange(rows.map((r, i) => (i === row ? r.map((v, j) => (j === column ? clean(value) : v)) : r)));
  }

  function add(code = "") {
    onchange([...rows, [code, ...header.slice(1).map(() => "")]]);
  }
</script>

<div class="table-wrap soils-table">
  <table>
    <thead>
      <tr>
        {#each header as column (column)}<th>{column}</th>{/each}
        <th aria-label={t("remove")}></th>
      </tr>
    </thead>
    <tbody>
      {#each rows as row, r (r)}
        <tr>
          {#each row as value, c (c)}
            <td>
              <input
                class:code={c === 0}
                class:invalid={!valid(c, value)}
                {value}
                aria-label={`${row[0] || "?"} ${header[c]}`}
                spellcheck="false"
                onchange={(e) => edit(r, c, e.currentTarget.value)}
              />
            </td>
          {/each}
          <td>
            <button
              type="button"
              class="icon-btn btn-danger"
              title={t("remove")}
              aria-label={`${t("remove")} ${row[0]}`}
              onclick={() => onchange(rows.filter((_, i) => i !== r))}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
<div class="row">
  <button type="button" class="btn" onclick={() => add()}>+ {t("soils.add")}</button>
  {#if missing.length}
    <button type="button" class="btn" onclick={() => onchange([...rows, ...missing.map((code) => [code, ...header.slice(1).map(() => "")])])}>
      + {t("soils.add.missing", { n: missing.length })}
    </button>
  {/if}
</div>

<style>
  .soils-table {
    max-height: 420px;
  }

  td {
    padding: 3px 4px;
  }

  input {
    width: 6.5em;
    padding: 5px 7px;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    background: var(--bg-panel);
    color: var(--text-primary);
    font-family: var(--mono);
    font-size: 0.8rem;
    text-align: right;
    outline: none;
  }

  input.code {
    width: 12em;
    font-family: var(--font-family);
    text-align: left;
  }

  input:focus {
    border-color: var(--color-teal);
    box-shadow: 0 0 0 3px var(--color-teal-soft);
  }

  input.invalid {
    border-color: var(--danger-color);
    background: var(--danger-bg);
  }
</style>
