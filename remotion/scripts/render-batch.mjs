// Renderiza un vídeo por cada entrada de videos.json (o del archivo pasado como argumento).
// Uso: npm run batch            -> usa videos.json
//      npm run batch -- otro.json
import {bundle} from '@remotion/bundler';
import {renderMedia, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';

// Opcional: REMOTION_BROWSER=/ruta/a/chrome para usar un navegador ya instalado.
const browserExecutable = process.env.REMOTION_BROWSER ?? null;
const root = path.resolve(import.meta.dirname, '..');
const lista = JSON.parse(
  fs.readFileSync(path.resolve(root, process.argv[2] ?? 'videos.json'), 'utf8'),
);

console.log('Empaquetando proyecto...');
const serveUrl = await bundle({entryPoint: path.join(root, 'src/index.ts')});

for (const {archivo, ...inputProps} of lista) {
  const composition = await selectComposition({serveUrl, id: 'MiVideo', inputProps, browserExecutable});
  const outputLocation = path.join(root, 'out', archivo);
  console.log(`Renderizando ${archivo}...`);
  await renderMedia({composition, serveUrl, codec: 'h264', outputLocation, inputProps, browserExecutable});
  console.log(`  -> ${outputLocation}`);
}
console.log('¡Listo!');
