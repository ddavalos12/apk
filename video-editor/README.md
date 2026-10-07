# Editor de vídeo automático (Remotion + FFmpeg)

Proyecto Remotion listo para generar vídeos MP4 desde código y datos (JSON).

## 1. Instalar en tu ordenador (una sola vez)

### Node.js (obligatorio, versión 18 o superior; recomendado 22 LTS)
- **Windows / macOS:** descarga el instalador LTS de https://nodejs.org
- **Linux (Ubuntu/Debian):** `sudo apt install nodejs npm` (o usa https://github.com/nvm-sh/nvm)

### FFmpeg
Remotion 4 ya incluye su propio FFmpeg para renderizar, así que no es imprescindible,
pero es útil tenerlo para cortar, convertir o unir vídeos fuera de Remotion:
- **Windows:** `winget install Gyan.FFmpeg` (cierra y vuelve a abrir la terminal)
- **macOS:** `brew install ffmpeg` (requiere https://brew.sh)
- **Linux:** `sudo apt install ffmpeg`

Comprueba: `ffmpeg -version`

### Dependencias del proyecto
```bash
git clone https://github.com/ddavalos12/apk.git
cd apk/video-editor
npm install
```
La primera vez que renderices, Remotion descargará automáticamente un Chrome headless (~100 MB).

En Linux puede que necesites además librerías del sistema para Chrome:
```bash
sudo apt install -y libnss3 libdbus-1-3 libatk1.0-0 libgbm-dev libasound2t64 libxrandr2 libxkbcommon-dev libxfixes3 libxcomposite1 libxdamage1 libatk-bridge2.0-0 libpango-1.0-0 libcairo2 libcups2
```

## 2. Uso

| Comando | Qué hace |
|---|---|
| `npm run studio` | Abre el editor visual en el navegador (vista previa en vivo) |
| `npm run render` | Genera `out/video.mp4` con los valores por defecto |
| `npm run render:datos` | Genera `out/video.mp4` usando los textos/colores de `datos.json` |
| `npm run lote` | Genera un vídeo por cada entrada de `lote.json` en `out/` |
| `npm run ffmpeg:check` | Comprueba que FFmpeg está instalado |

### Usar tus propios vídeos
Copia el clip a `public/` (p. ej. `public/clip.mp4`) y pon `"video": "clip.mp4"` en `datos.json`
o en `lote.json`. El título y subtítulo se superponen sobre el vídeo.

## 3. Estructura
- `src/Root.tsx` – registra la composición (duración, fps, resolución).
- `src/Principal.tsx` – el diseño y las animaciones del vídeo; edítalo para cambiar el estilo.
- `scripts/render-lote.mjs` – renderizado automático por lotes con la API de Node.
- `remotion.config.ts` – opciones de renderizado (códec, formato).

## Licencia de Remotion
Remotion es gratuito para particulares y empresas de hasta 3 personas; empresas más grandes
necesitan licencia: https://remotion.dev/license
