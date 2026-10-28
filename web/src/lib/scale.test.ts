import { describe, expect, it } from "vitest";
import { interpolateLog, linearTicks, logPosition, logTicks, niceStep } from "./scale";

describe("logTicks", () => {
  it("covers the range with powers of ten", () => {
    expect(logTicks(0.1, 10000).map((t) => t.value)).toEqual([0.1, 1, 10, 100, 1000, 10000]);
  });

  it("labels small and large values readably", () => {
    expect(logTicks(0.01, 1000).map((t) => t.label)).toEqual(["0.01", "0.1", "1", "10", "100", "1 000"]);
  });

  it("rounds outwards", () => {
    expect(logTicks(0.2, 9000).map((t) => t.value)).toEqual([0.1, 1, 10, 100, 1000, 10000]);
  });
});

describe("niceStep", () => {
  it.each([
    [0.53, 0.2],
    [1, 0.2],
    [0.05, 0.01],
    [12, 5],
  ])("max %s gives step %s", (max, step) => {
    expect(niceStep(max)).toBeCloseTo(step);
  });
});

describe("linearTicks", () => {
  it("starts at 0 and passes the maximum", () => {
    const ticks = linearTicks(0.53);
    expect(ticks[0].value).toBe(0);
    expect(ticks.at(-1)!.value).toBeGreaterThanOrEqual(0.53);
    expect(ticks.map((t) => t.label)).toEqual(["0.0", "0.2", "0.4", "0.6"]);
  });

  it("has at least two ticks for a flat curve", () => {
    expect(linearTicks(0).length).toBe(2);
  });
});

describe("logPosition", () => {
  it("places values on a log scale", () => {
    expect(logPosition(1, 0.1, 10, 100)).toBeCloseTo(50);
    expect(logPosition(0.1, 0.1, 10, 100)).toBeCloseTo(0);
    expect(logPosition(10, 0.1, 10, 100)).toBeCloseTo(100);
  });
});

describe("interpolateLog", () => {
  const points: [number, number][] = [
    [0.1, 0],
    [10, 0.2],
    [1000, 0.4],
  ];

  it("returns the points themselves", () => {
    expect(interpolateLog(points, 10)).toBeCloseTo(0.2);
    expect(interpolateLog(points, 1000)).toBeCloseTo(0.4);
  });

  it("is linear in log time", () => {
    expect(interpolateLog(points, 1)).toBeCloseTo(0.1);
    expect(interpolateLog(points, 100)).toBeCloseTo(0.3);
  });

  it("is undefined outside the points", () => {
    expect(interpolateLog(points, 0.05)).toBeUndefined();
    expect(interpolateLog(points, 2000)).toBeUndefined();
  });
});
