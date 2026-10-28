// State shared between the tabs.
import type { LoadedFile } from "./files";
import type { InitResult, InitStep } from "./protocol";
import { PythonError, startPython } from "./python";

export const python = $state<{
  state: "loading" | "ready" | "failed";
  step: InitStep;
  error: string;
  info?: InitResult;
}>({ state: "loading", step: "download", error: "" });

export function loadPython() {
  startPython((step) => (python.step = step)).then(
    (info) => {
      python.info = info;
      python.state = "ready";
    },
    (e: unknown) => {
      python.error = e instanceof PythonError || e instanceof Error ? e.message : String(e);
      python.state = "failed";
    },
  );
}

/** The soils file of the Convert tab, the Soil parameters tab can fill it. */
export const soils = $state<{ file?: LoadedFile; edited?: boolean }>({});

export type Theme = "light" | "dark";

function storedTheme(): Theme {
  try {
    const theme = localStorage.getItem("theme");
    if (theme === "light" || theme === "dark") return theme;
  } catch {
    // storage can be blocked
  }
  return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export const theme = $state<{ value: Theme }>({ value: storedTheme() });

export function setTheme(value: Theme) {
  theme.value = value;
  document.documentElement.dataset.theme = value;
  try {
    localStorage.setItem("theme", value);
  } catch {
    // not remembered, still works for this visit
  }
}
