<script lang="ts">
  import { interpolateLog, linearTicks, logPosition, logTicks } from "./scale";

  export interface Series {
    key: string;
    label: string;
    color: string;
    points: [number, number][];
  }

  interface Props {
    series: Series[];
    xLabel: string;
    yLabel: string;
  }

  let { series, xLabel, yLabel }: Props = $props();

  const HEIGHT = 380;
  const MARGIN = { top: 16, right: 36, bottom: 48, left: 68 };
  const LABEL_LENGTH = 48;

  let width = $state(800);
  let hoverX = $state<number | undefined>();

  // time 0 cannot be shown on a log axis
  let visible = $derived(series.map((s) => ({ ...s, points: s.points.filter(([time]) => time > 0) })));
  let allPoints = $derived(visible.flatMap((s) => s.points));
  let xTicks = $derived(
    allPoints.length ? logTicks(Math.min(...allPoints.map((p) => p[0])), Math.max(...allPoints.map((p) => p[0]))) : [],
  );
  let xMin = $derived(xTicks[0]?.value ?? 0.1);
  let xMax = $derived(xTicks.at(-1)?.value ?? 1);
  let yTicks = $derived(linearTicks(Math.max(0, ...allPoints.map((p) => p[1]))));
  let yMax = $derived(yTicks.at(-1)!.value);

  let plotWidth = $derived(Math.max(100, width - MARGIN.left - MARGIN.right));
  let plotHeight = HEIGHT - MARGIN.top - MARGIN.bottom;

  const x = (time: number) => MARGIN.left + logPosition(time, xMin, xMax, plotWidth);
  // settlement points downwards, 0 at the top
  const y = (settlement: number) => MARGIN.top + (settlement / yMax) * plotHeight;

  function path(points: [number, number][]): string {
    return points.map(([t, s], i) => `${i ? "L" : "M"}${x(t).toFixed(1)},${y(s).toFixed(1)}`).join("");
  }

  // the value of each series at the time under the mouse
  let hovered = $derived.by(() => {
    if (hoverX === undefined || !allPoints.length) return undefined;
    const time = 10 ** (Math.log10(xMin) + ((hoverX - MARGIN.left) / plotWidth) * Math.log10(xMax / xMin));
    const rows = visible.flatMap((s) => {
      const value = interpolateLog(s.points, time);
      return value === undefined ? [] : [{ label: s.label, color: s.color, value }];
    });
    return rows.length ? { time, rows, x: x(time) } : undefined;
  });

  const format = (value: number, decimals: number) => value.toFixed(decimals);
  // long file names would make the tooltip wider than the chart, it is placed next to the guide line but inside the plot
  const short = (label: string) => (label.length > LABEL_LENGTH ? `…${label.slice(-(LABEL_LENGTH - 1))}` : label);
</script>

<div class="chart" bind:clientWidth={width}>
  <svg {width} height={HEIGHT} role="img" aria-label={`${yLabel} / ${xLabel}`}>
    <g class="grid">
      {#each xTicks as tick (tick.value)}
        <line x1={x(tick.value)} x2={x(tick.value)} y1={MARGIN.top} y2={MARGIN.top + plotHeight} />
      {/each}
      {#each yTicks as tick (tick.value)}
        <line x1={MARGIN.left} x2={MARGIN.left + plotWidth} y1={y(tick.value)} y2={y(tick.value)} />
      {/each}
    </g>
    <g class="axis">
      {#each xTicks as tick (tick.value)}
        <text x={x(tick.value)} y={MARGIN.top + plotHeight + 18} text-anchor="middle">{tick.label}</text>
      {/each}
      {#each yTicks as tick (tick.value)}
        <text x={MARGIN.left - 8} y={y(tick.value) + 4} text-anchor="end">{tick.label}</text>
      {/each}
      <text class="title" x={MARGIN.left + plotWidth / 2} y={HEIGHT - 6} text-anchor="middle">{xLabel}</text>
      <text class="title" transform={`translate(16 ${MARGIN.top + plotHeight / 2}) rotate(-90)`} text-anchor="middle">
        {yLabel}
      </text>
    </g>

    {#each visible as s (s.key)}
      <path class="line" d={path(s.points)} stroke={s.color} />
    {/each}

    {#if hovered}
      <line class="guide" x1={hovered.x} x2={hovered.x} y1={MARGIN.top} y2={MARGIN.top + plotHeight} />
      {#each hovered.rows as row (row.label)}
        <circle cx={hovered.x} cy={y(row.value)} r="4" fill={row.color} />
      {/each}
      {@const boxWidth = 40 + 6.6 * Math.max(...hovered.rows.map((r) => short(r.label).length + 11))}
      {@const right = hovered.x + boxWidth + 12 <= MARGIN.left + plotWidth}
      {@const left = Math.max(MARGIN.left + 4, right ? hovered.x + 12 : hovered.x - boxWidth - 12)}
      <g class="tooltip" transform={`translate(${left} ${MARGIN.top + 8})`}>
        <rect width={boxWidth} height={26 + hovered.rows.length * 18} rx="6" />
        <text x="10" y="18" class="time">t = {format(hovered.time, hovered.time < 10 ? 3 : 1)}</text>
        {#each hovered.rows as row, i (row.label)}
          <circle cx="14" cy={33 + i * 18} r="4" fill={row.color} />
          <text x="24" y={37 + i * 18}>{format(row.value, 4)} m · {short(row.label)}</text>
        {/each}
      </g>
    {/if}

    <rect
      class="overlay"
      x={MARGIN.left}
      y={MARGIN.top}
      width={plotWidth}
      height={plotHeight}
      role="presentation"
      onpointermove={(e) => (hoverX = e.offsetX)}
      onpointerleave={() => (hoverX = undefined)}
    />
  </svg>
</div>

<style>
  .chart {
    width: 100%;
    overflow: hidden;
  }

  svg {
    display: block;
    font-size: 12px;
  }

  .grid line {
    stroke: var(--border-color);
    stroke-width: 1;
  }

  .axis text {
    fill: var(--text-secondary);
  }

  .axis .title {
    fill: var(--text-primary);
    font-weight: 600;
  }

  .line {
    fill: none;
    stroke-width: 2.2;
    stroke-linejoin: round;
  }

  .guide {
    stroke: var(--text-secondary);
    stroke-dasharray: 3 3;
  }

  .tooltip rect {
    fill: var(--bg-card);
    stroke: var(--border-color);
  }

  .tooltip text {
    fill: var(--text-primary);
  }

  .tooltip .time {
    font-weight: 600;
  }

  .overlay {
    fill: transparent;
    cursor: crosshair;
  }
</style>
