// Reading dropped files and offering results for download.

export interface LoadedFile {
  name: string;
  data: Uint8Array;
}

export async function readFiles(files: FileList | File[]): Promise<LoadedFile[]> {
  return Promise.all(
    Array.from(files).map(async (file) => ({ name: file.name, data: new Uint8Array(await file.arrayBuffer()) })),
  );
}

export function hasExtension(name: string, extension: string): boolean {
  return name.toLowerCase().endsWith(extension);
}

export function download(name: string, data: Uint8Array | string, type = "application/octet-stream") {
  const blob = new Blob([typeof data === "string" ? data : (data as Uint8Array<ArrayBuffer>)], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
