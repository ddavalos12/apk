# Remotion: edición de vídeo automática

Proyecto listo para crear vídeos con código (React) usando [Remotion](https://www.remotion.dev) 4 y FFmpeg.

## Instalación en tu ordenador

1. Descarga o clona este repositorio y entra en la carpeta `remotion/`.
2. Ejecuta el instalador de tu sistema (instala Node.js, FFmpeg, las dependencias y el navegador de renderizado):
   - **Windows** (PowerShell):
     ```powershell
     powershell -ExecutionPolicy Bypass -File .\instalar-windows.ps1
     ```
   - **macOS / Linux**:
     ```bash
     bash instalar-mac-linux.sh
     ```

> Remotion 4 ya incluye su propio FFmpeg para renderizar; el FFmpeg del sistema es para que puedas
> recortar, convertir o unir vídeos desde la terminal o desde tus propios scripts.

## Uso

| Comando | Qué hace |
|---|---|
| `npm run studio` | Abre el editor visual en el navegador (vista previa en vivo) |
| `npm run render` | Renderiza `out/video.mp4` con los valores por defecto |
| `npm run render:props` | Renderiza usando los textos/colores de `props.json` |
| `npm run batch` | Genera un vídeo por cada entrada de `videos.json` |
| `npm run upgrade` | Actualiza Remotion a la última versión |

## Dónde editar

- `src/MiVideo.tsx` – el diseño y las animaciones del vídeo.
- `src/Root.tsx` – duración, fps, resolución y valores por defecto.
- `props.json` / `videos.json` – datos para generar vídeos sin tocar código.
- `public/` – pon aquí imágenes, música o clips y úsalos con `staticFile('archivo.mp4')`.

## Álbum de fotos de la Familia Bumand

Edición del vídeo `public/album-bumand.mp4` (composición `AlbumBumand`, 1920×1080):

- Portada animada al principio ("Álbum de fotos – Familia Bumand") y cierre ("Gracias por cada momento").
- 7 rótulos de capítulo con número, título y subtítulo, acompañados de destellos dorados.
- Distintivo "Familia Bumand" con la bandera de Bolivia y una barra de progreso por capítulos
  en la esquina inferior derecha (tapa también la marca de agua del vídeo original).
- Textos, tiempos y colores se cambian en `src/album/datos.ts`.

```bash
npm run studio         # previsualizar y elegir "AlbumBumand"
npm run render:album   # genera out/album-bumand.mp4
```

## Ejemplos útiles de FFmpeg

```bash
ffmpeg -i out/video.mp4 -ss 00:00:01 -t 3 -c copy recorte.mp4      # recortar
ffmpeg -i out/video.mp4 -i musica.mp3 -c:v copy -shortest final.mp4 # añadir audio
ffmpeg -i out/video.mp4 -vf scale=1280:-2 video-720p.mp4           # reducir resolución
```

Nota sobre la licencia: Remotion es gratis para particulares y empresas de hasta 3 personas;
empresas más grandes necesitan una licencia de empresa (ver remotion.dev/license).
