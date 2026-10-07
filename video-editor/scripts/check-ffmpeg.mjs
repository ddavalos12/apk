// Comprueba que FFmpeg está disponible en el sistema.
import { execSync } from "node:child_process";
try {
  console.log(execSync("ffmpeg -version").toString().split("\n")[0]);
} catch {
  console.error("FFmpeg no está instalado o no está en el PATH (ver README.md).");
  process.exit(1);
}
