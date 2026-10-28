<script lang="ts">
  import { readFiles, type LoadedFile } from "./files";
  import { t } from "./i18n.svelte";

  interface Props {
    label: string;
    accept: string;
    multiple?: boolean;
    compact?: boolean;
    onfiles: (files: LoadedFile[]) => void;
  }

  let { label, accept, multiple = false, compact = false, onfiles }: Props = $props();

  let input: HTMLInputElement;
  let active = $state(false);

  async function handle(list: FileList | null | undefined) {
    if (!list?.length) return;
    const extensions = accept.split(",").map((e) => e.trim().toLowerCase());
    const accepted = Array.from(list).filter((f) => extensions.some((e) => f.name.toLowerCase().endsWith(e)));
    const files = await readFiles(multiple ? accepted : accepted.slice(0, 1));
    if (files.length) onfiles(files);
  }
</script>

<button
  type="button"
  class="dropzone"
  class:active
  class:compact
  onclick={() => input.click()}
  ondragover={(e) => {
    e.preventDefault();
    active = true;
  }}
  ondragleave={() => (active = false)}
  ondrop={(e) => {
    e.preventDefault();
    active = false;
    handle(e.dataTransfer?.files);
  }}
>
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M12 16V4m0 0-4.5 4.5M12 4l4.5 4.5M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" />
  </svg>
  <span class="label">{label}</span>
  <span class="muted small">{t("drop.browse")} · {accept}</span>
</button>
<input
  bind:this={input}
  type="file"
  {accept}
  {multiple}
  hidden
  onchange={(e) => {
    handle(e.currentTarget.files);
    e.currentTarget.value = "";
  }}
/>

<style>
  .dropzone {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.3rem;
    padding: 1.6rem 1rem;
    border: 2px dashed var(--border-color);
    border-radius: 12px;
    background: var(--bg-panel);
    transition:
      border-color 0.15s,
      background 0.15s;
  }

  .dropzone.compact {
    flex-direction: row;
    justify-content: center;
    padding: 0.8rem 1rem;
    gap: 0.6rem;
  }

  .dropzone:hover,
  .dropzone.active {
    border-color: var(--color-teal);
    background: var(--color-teal-soft);
  }

  svg {
    width: 28px;
    height: 28px;
    fill: none;
    stroke: var(--color-teal);
    stroke-width: 1.8;
    stroke-linecap: round;
    stroke-linejoin: round;
  }

  .compact svg {
    width: 20px;
    height: 20px;
  }

  .label {
    font-weight: 600;
  }
</style>
