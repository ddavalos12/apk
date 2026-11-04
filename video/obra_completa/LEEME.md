# Obra completa "Sansón y Dalila" con overlays animados

Intro + escenas 1 a 5 en un solo video, en Full HD (1920x1080, 30 fps), con overlays animados según lo que pasa en cada escena.

- Video completo: `sanson_y_dalila_obra_completa.mp4` (≈7 min 33 s). Pesa más de 100 MB, que es el límite de GitHub, así que **no está en el repositorio**: se entregó directamente en el chat.
- En el repositorio están las **partes por escena** (`partes/`), cortadas del video completo sin volver a codificar, así que tienen la misma calidad.

## De dónde sale cada parte

El video que armaste (`original/escuela_dominical_compilado.mp4`, 720p a 270 kbps) se reconstruyó con los masters en 1080p y **los mismos cortes**. Coincidencia del sonido de cada parte con tu video: 0.97–0.99.

| Tramo | Fuente | Desde – hasta (s de la fuente) |
|---|---|---|
| Intro | `../intro_sanson_dalila.mp4` | 0 – 60 |
| Escena 1 | `../escena1/escena1_la_revelacion.mp4` | 0 – 76.12 |
| Escena 2 | `../escena2/escena2_la_quijada_de_asno.mp4` | 0.75 – 56.70 |
| Clip extra de Sansón | tu video compilado (no hay otra copia) | 192.07 – 195.97 |
| Escena 3 | `../escena3/escena3_la_oferta_de_los_filisteos.mp4` | 0 – 64.83 |
| Escena 4 (toma 2) | `../escena4_toma2/escena4_el_secreto_de_sanson_toma2.mp4` | 0 – 80.96 |
| Escena 5 | `../escena5/escena5_el_templo_de_dagon.mp4` | 0 – 103.78 |
| Cierre "Fin" | último cuadro + final de la canción de la intro | 7 s |

El clip extra de 3.9 s solo existe en tu video compilado, así que se limpió y se pasó a 1080p, pero se ve algo más suave que el resto.

## Overlays

Estilo igual al de la intro y los banners (azul marino, dorado, Cinzel y Cormorant). Versículos de la Reina-Valera 1960.

| Escena | Overlays |
|---|---|
| 1. La revelación | lugar **Zora, tribu de Dan** (13:2) · versículo 13:1 · etiqueta **La esposa de Manoa** · **luz divina** cuando entra el ángel · etiqueta **El ángel de Jehová** · versículo 13:5 · título **"Nace Sansón"** con 13:24 sobre el escenario vacío |
| 2. La quijada de asno | etiqueta **Sansón** · lugar **Lehi** · etiqueta **Los filisteos** · **5 golpes** (onda dorada y chispas) en la pelea · versículo 15:15 · versículo 16:4 (paso a Dalila) |
| 3. La oferta de los filisteos | etiqueta **Dalila** · lugar **Valle de Sorec** · etiqueta **Los filisteos** · versículo 16:5 · **brillo de plata** en la caja · etiqueta **Mil cien siclos** |
| 4. El secreto de Sansón | etiquetas **Dalila** y **Sansón** · versículo 16:17 · **tono de noche y "Z z z"** cuando se duerme · **destello en las tijeras** y viñeta que late · versículo 16:19 |
| 5. El templo de Dagón | lugar **Gaza, templo de Dagón** · versículo 16:23 · etiqueta **Sansón, ciego y encadenado** · versículo 16:26 · versículo 16:28 con **rayos de luz** sobre Sansón · **temblor de cámara, destello y polvo** en el derrumbe |
| Cierre | Jueces 16:30 y **"Fin"**, que aparece con el golpe final de la canción de la intro |

Entre escenas hay un fundido corto a negro. Los tiempos y posiciones de cada overlay están en `build_overlays()` de `armar_obra.py`; los diseños están en `overlays.py`.

## Volver a generarlo

```bash
python3 armar_obra.py
```

Tarda unos 15–20 minutos. Genera el video completo y luego las partes. Para ver cuadros de prueba en ciertos segundos:

```bash
python3 armar_obra.py --preview /ruta/carpeta 105.5 155.5
```

Requiere Python 3 con `numpy` y `Pillow`, y `ffmpeg`.
