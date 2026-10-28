import { execFileSync } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { crc32, createZip } from "./zip";

const encode = (text: string) => new TextEncoder().encode(text);

describe("crc32", () => {
  it("matches the standard check value", () => {
    expect(crc32(encode("123456789"))).toBe(0xcbf43926);
  });

  it("is 0 for no data", () => {
    expect(crc32(new Uint8Array())).toBe(0);
  });
});

describe("createZip", () => {
  it("is read back by Python's zipfile", () => {
    const entries = [
      { name: "a.bj.sli", data: encode("first\r\nfile\r\n") },
      { name: "calc [1] é.kj.sli", data: new Uint8Array([0, 1, 2, 255]) },
    ];
    const path = join(mkdtempSync(join(tmpdir(), "zip-")), "test.zip");
    writeFileSync(path, createZip(entries));

    const script = `
import json, sys, zipfile
with zipfile.ZipFile(sys.argv[1]) as z:
    assert z.testzip() is None
    print(json.dumps({i.filename: list(z.read(i)) for i in z.infolist()}))`;
    const read = JSON.parse(execFileSync("python3", ["-c", script, path], { encoding: "utf-8" }));
    expect(read).toEqual(Object.fromEntries(entries.map((e) => [e.name, Array.from(e.data)])));
  });

  it("writes an empty archive", () => {
    expect(createZip([]).length).toBe(22);
  });
});
