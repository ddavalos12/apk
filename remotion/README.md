# BumanD – Álbum de fotos (edición con Remotion)

Edición del video `../video/video_comprimido.mp4` con:

- **Corrección de color**: más brillo, contraste y saturación en todas las fotos.
- **Fondo realzado**: luz cálida en el centro del pergamino, bordes más profundos y tono azul/naranja de la marca.
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

## Cambiar textos y tiempos

Todos los textos y los segundos donde aparecen están en `src/timeline.ts`.
