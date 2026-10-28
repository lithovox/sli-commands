import { describe, expect, it } from "vitest";
import { compareVerticals, formatPosition } from "./verticals";

const two = [
  { number: 1, x: 10, z: 0 },
  { number: 2, x: 11, z: 0 },
];

describe("compareVerticals", () => {
  it("accepts the same verticals", () => {
    expect(compareVerticals(two, two.map((v) => ({ ...v })))).toBeUndefined();
  });

  it("ignores rounding in the last decimals", () => {
    expect(compareVerticals(two, [two[0], { number: 2, x: 11.00001, z: 0 }])).toBeUndefined();
  });

  it("reports another number of verticals", () => {
    expect(compareVerticals(two, [two[0]])).toEqual({ kind: "count", expected: 2, found: 1 });
  });

  it("reports the first vertical at another position", () => {
    const moved = { number: 2, x: 12, z: 0 };
    expect(compareVerticals(two, [two[0], moved])).toEqual({ kind: "position", number: 2, expected: two[1], found: moved });
  });

  it("compares z as well", () => {
    expect(compareVerticals(two, [two[0], { number: 2, x: 11, z: -1 }])?.kind).toBe("position");
  });
});

describe("formatPosition", () => {
  it("rounds to millimetres", () => {
    expect(formatPosition({ number: 1, x: 10.00049, z: -0.5 })).toBe("x = 10 m, z = -0.5 m");
  });
});
