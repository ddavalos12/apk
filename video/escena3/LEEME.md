# Escena 3: "La oferta de los filisteos"

Los príncipes de los filisteos visitan a Dalila y le ofrecen plata para que descubra el secreto de la fuerza de Sansón (Jueces 16:5).

- Original: `original/escena3_original.mp4` (1280x720, 25 fps, 0.9 Mbps).
- Resultado: `escena3_la_oferta_de_los_filisteos.mp4` (1920x1080, 25 fps, H.264 alta calidad + AAC 256 kbps).

## Qué se hizo

**Banner:** "ESCENA 3 · *La oferta de los filisteos*", abajo a la **derecha** (Dalila está sentada a la izquierda). Entra en el segundo 1 y sale en el 8.5.

**Audio:** la música (13–19 s y 60–65 s) y la parte fuerte (43.5–56 s) se dejan como están. Se subieron los diálogos en vivo (sin micrófono):

| Tramo | Antes | Después | Ganancia |
|---|---|---|---|
| Filisteos hablan con Dalila (20.8–26.6 s) | -21.3 | -16.8 | +14 dB |
| Diálogo en voz baja (27.5–33.6 s) | -26.6 | -15.1 | +22 dB |
| Diálogo (35.1–38.0 s) | -21.6 | -17.1 | +14 dB |
| Frase débil antes del final (38.0–43.3 s) | -33.1 | -19.3 | +20 dB |
| Escena completa | -11.7 | -16.0 | |

- El rango de volumen bajó de 16.2 a 5.1 LU.
- La línea de tono que se ve en el espectrograma (≈386/784 Hz) es música de fondo, no un zumbido, así que no se quitó.

**Imagen:** igual que las Escenas 1 y 2 (limpieza de compresión, 1080p, enfoque, más contraste y color).

Los tramos, sus ganancias máximas y el título están al inicio de `editar_escena3.py` (`KIDS`, `LINE2`).

## Volver a generarlo

```bash
python3 editar_escena3.py
```

Usa `../comun_escenas.py` (banner, subida por tramos, nivelación final y codificación).
