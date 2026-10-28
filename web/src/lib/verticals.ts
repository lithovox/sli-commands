// Results can only be compared when the calculations have the same verticals.

export interface Position {
  number: number;
  x: number;
  z: number;
}

export type Mismatch =
  | { kind: "count"; expected: number; found: number }
  | { kind: "position"; number: number; expected: Position; found: Position };

// co-ordinates in the .sld file have 7 decimals
const TOLERANCE = 1e-4;

/** Why candidate cannot be compared with reference, or undefined if it can. */
export function compareVerticals(reference: Position[], candidate: Position[]): Mismatch | undefined {
  if (reference.length !== candidate.length) {
    return { kind: "count", expected: reference.length, found: candidate.length };
  }
  for (let i = 0; i < reference.length; i++) {
    const expected = reference[i];
    const found = candidate[i];
    if (
      expected.number !== found.number ||
      Math.abs(expected.x - found.x) > TOLERANCE ||
      Math.abs(expected.z - found.z) > TOLERANCE
    ) {
      return { kind: "position", number: expected.number, expected, found };
    }
  }
  return undefined;
}

export function formatPosition(position: Position): string {
  const round = (value: number) => Number(value.toFixed(3));
  return `x = ${round(position.x)} m, z = ${round(position.z)} m`;
}
