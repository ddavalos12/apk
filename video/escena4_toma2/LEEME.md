# Escena 4, toma 2: "El secreto de Sansón"

Otra grabación de la Escena 4 (archivo `41.mp4`), más larga y completa: 81 s en vez de 64 s. Sansón visita a Dalila, conversan, ella le sirve de beber, él se queda dormido y Dalila toma las tijeras (Jueces 16:17-19). Solo la música del inicio coincide con la toma 1; el resto es otra actuación.

- Original: `original/escena4_toma2_original.mp4` (1280x720, 30 fps, 2.6 Mbps).
- Resultado: `escena4_el_secreto_de_sanson_toma2.mp4` (1920x1080, 30 fps, H.264 CRF 19 + AAC 256 kbps, 86 MB).

## Qué se hizo

**Banner:** el mismo de la toma 1, "ESCENA 4 · *El secreto de Sansón*", abajo a la derecha, del segundo 1 al 8.5.

**Audio:** la música del inicio y las partes fuertes (40.6–45.2 s y 60.6–66.4 s) se dejan como están.

| Tramo | Antes | Después | Ganancia |
|---|---|---|---|
| Sansón llega con Dalila (14.1–18.3 s) | -26.1 | -16.3 | +14 dB |
| Saludo (18.8–20.8 s) | -24.7 | -16.1 | +14 dB |
| Conversación (21.5–26.3 s) | -23.1 | -14.4 | +14 dB |
| Conversación 2 (26.5–34.3 s) | -16.9 | -15.5 | +6 dB |
| Diálogo en voz baja (34.5–39.1 s) | -31.1 | -15.9 | +22 dB |
| Dalila sirve la bebida (45.8–48.8 s) | -27.6 | -15.2 | +18 dB |
| Frase corta (51.7–52.5 s) | -24.7 | picos como el resto | +12 dB |
| Frase en voz baja (54.6–56.1 s) | -37.9 | -14.9 | +22 dB |
| Dalila y la música final (68.5–81 s) | -24.4 | -18.2 | +8 dB, sin filtro de voz para no quitarle graves a la música |
| Escena completa | -15.2 | -16.0 | |

- El rango de volumen bajó de 21.2 a 5.9 LU.

**Imagen:** igual que las otras escenas. Se codificó con CRF 19 en vez de 17 para que el archivo quede por debajo de los 100 MB que acepta GitHub.

## Volver a generarlo

```bash
python3 editar_escena4_toma2.py
```

Usa `../comun_escenas.py`.
