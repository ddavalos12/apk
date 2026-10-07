// Renderiza un vídeo por cada entrada de lote.json (o del archivo pasado como argumento).
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import { readFileSync, mkdirSync } from "node:fs";
import path from "node:path";

const archivo = process.argv[2] ?? "lote.json";
const trabajos = JSON.parse(readFileSync(archivo, "utf8"));
mkdirSync("out", { recursive: true });

const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });

for (const { salida, ...inputProps } of trabajos) {
  const composition = await selectComposition({
    serveUrl,
    id: "Principal",
    inputProps,
    browserExecutable: process.env.REMOTION_BROWSER ?? null,
  });
  const outputLocation = path.join("out", salida);
  await renderMedia({
    composition,
    serveUrl,
    codec: "h264",
    outputLocation,
    inputProps,
    browserExecutable: process.env.REMOTION_BROWSER ?? null,
  });
  console.log(`✔ ${outputLocation}`);
}
