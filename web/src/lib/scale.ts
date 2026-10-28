// Axis calculations for the time-settlement chart.

export interface Tick {
  value: number;
  label: string;
}

/** Powers of ten that cover [min, max], for a logarithmic axis. */
export function logTicks(min: number, max: number): Tick[] {
  const ticks: Tick[] = [];
  for (let e = Math.floor(Math.log10(min)); e <= Math.ceil(Math.log10(max)); e++) {
    const value = 10 ** e;
    ticks.push({ value, label: e < 0 ? value.toFixed(-e) : value.toLocaleString("en-US").replaceAll(",", " ") });
  }
  return ticks;
}

/** A "nice" step (1, 2 or 5 times a power of ten) for about count ticks over [0, max]. */
export function niceStep(max: number, count = 5): number {
  if (max <= 0) return 1;
  const rough = max / count;
  const power = 10 ** Math.floor(Math.log10(rough));
  const fraction = rough / power;
  return (fraction <= 1 ? 1 : fraction <= 2 ? 2 : fraction <= 5 ? 5 : 10) * power;
}

/** Ticks from 0 to just past max with a nice step. */
export function linearTicks(max: number, count = 5): Tick[] {
  const step = niceStep(max, count);
  const decimals = Math.max(0, -Math.floor(Math.log10(step)));
  const ticks: Tick[] = [];
  for (let i = 0; i * step < max + step / 2; i++) {
    ticks.push({ value: i * step, label: (i * step).toFixed(decimals) });
  }
  if (ticks.length < 2) ticks.push({ value: step, label: step.toFixed(decimals) });
  return ticks;
}

export function logPosition(value: number, min: number, max: number, length: number): number {
  return ((Math.log10(value) - Math.log10(min)) / (Math.log10(max) - Math.log10(min))) * length;
}

/** Value at time, linear between the points on a log time axis, undefined outside the points. */
export function interpolateLog(points: [number, number][], time: number): number | undefined {
  for (let i = 1; i < points.length; i++) {
    const [t0, v0] = points[i - 1];
    const [t1, v1] = points[i];
    if (t0 <= time && time <= t1) {
      if (t1 === t0) return v1;
      return v0 + ((v1 - v0) * Math.log10(time / t0)) / Math.log10(t1 / t0);
    }
  }
  return undefined;
}
