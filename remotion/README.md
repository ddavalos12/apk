# BumanD – Álbum de fotos (edición con Remotion)

Edición del video `../video/video_comprimido.mp4` con:

- **Corrección de color**: más brillo, contraste y saturación en todas las fotos.
- **Fondo nuevo**: el pergamino original se reemplaza por un fondo claro y neutro; cada foto lleva un marco blanco, sombra y un poco más de nitidez. También devuelve el verde a la bandera boliviana, que el filtro original había vuelto azul (`scripts/cambiar_fondo.py` genera `video/video_fondo_nuevo.mp4`).
- **Título de apertura** animado "BUMAND – Álbum de fotos".
- **Rótulos por sección** (¡Bienvenidos!, Nuestras reuniones, Familia BumanD, Momentos que unen, Rescatados, Compartiendo el mensaje, Juntos en el camino).
- **Bandera de Bolivia animada** cuando la bandera aparece en las fotos.
- **Partículas doradas**, destellos de luz entre secciones y **línea de tiempo** con un punto por sección.
- **Sello BumanD** en la esquina inferior derecha (tapa la marca de agua "descript").
- **Tramo vertical final** con fondo desenfocado en lugar de barras negras.
- **Cierre** de 5 s: "BumanD – Gracias por cada momento" con los valores Amor, Lealtad y Sacrificio.

## Previsualizar en tu PC (PowerShell)

Necesitas Node.js 18 o superior (`winget install OpenJS.NodeJS.LTS`).

```powershell
cd "C:\Users\Daniel\Documents\apk"
git pull
cd remotion
npm install
npm run studio
```

Se abre Remotion Studio en el navegador (http://localhost:3000). Ahí puedes reproducir el video y moverte por la línea de tiempo.

## Exportar el video final

```powershell
npm run render
```

El resultado queda en `remotion\out\bumand_editado.mp4`.

## Volver a generar el fondo

```powershell
pip install opencv-python-headless numpy
python scripts/cambiar_fondo.py ..\video\video_comprimido.mp4 ..\video\video_fondo_nuevo.mp4
```

Los colores del fondo están al inicio de `scripts/cambiar_fondo.py` (`center`, `edge`).

## Cambiar textos y tiempos

Todos los textos y los segundos donde aparecen están en `src/timeline.ts`.
