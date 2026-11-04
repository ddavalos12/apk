# Escena 4: "El secreto de Sansón"

Sansón visita a Dalila, conversan, ella le sirve de beber, él se queda dormido y Dalila se acerca con las tijeras (Jueces 16:17-19).

- Original: `original/escena4_original.mp4` (1280x720, **30 fps**, 2.6 Mbps).
- Resultado: `escena4_el_secreto_de_sanson.mp4` (1920x1080, 30 fps, H.264 alta calidad + AAC 256 kbps).

## Qué se hizo

**Banner:** "ESCENA 4 · *El secreto de Sansón*", abajo a la **derecha** (Dalila está a la izquierda). Entra en el segundo 1 y sale en el 8.5.

**Audio:** la música (1–12 s y 61.4–64.4 s) y la parte fuerte (47.6–55 s, cuando Sansón alza la copa) se dejan como están. Se subieron los diálogos en vivo:

| Tramo | Antes | Después | Ganancia |
|---|---|---|---|
| Sansón llega con Dalila (12.4–22.1 s) | -27.2 | -15.6 | +18.9 dB |
| Conversación (22.1–31.7 s) | -18.5 | -15.6 | +9.2 dB |
| Diálogo en voz baja (32.5–37.0 s) | -36.8 | -18.2 | +22 dB |
| Conversación 2 (37.4–41.9 s) | -19.8 | -14.9 | +10 dB |
| Dalila sirve la bebida (42.3–45.8 s) | -30.3 | -16.4 | +20 dB |
| Sansón se duerme (55.5–58.2 s) | -17.4 | -16.8 | +8 dB |
| Dalila con las tijeras (59.2–60.3 s) | -27.6 | -15.6 | +16 dB |
| Escena completa | -15.3 | -16.0 | |

- El rango de volumen bajó de 20.8 a 5.8 LU.

**Imagen:** igual que las otras escenas (limpieza de compresión, 1080p, enfoque, más contraste y color).

Los tramos, sus ganancias máximas y el título están al inicio de `editar_escena4.py` (`KIDS`, `LINE2`).

## Volver a generarlo

```bash
python3 editar_escena4.py
```

Usa `../comun_escenas.py` (banner, subida por tramos, nivelación final y codificación).
