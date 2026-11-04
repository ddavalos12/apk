# Escena 2: "La quijada de asno"

Sansón vence a los filisteos con una quijada de asno (Jueces 15:15).

- Original: `original/escena2_original.mp4` (1280x720, 25 fps, 1 Mbps).
- Resultado: `escena2_la_quijada_de_asno.mp4` (1920x1080, 25 fps, H.264 alta calidad + AAC 256 kbps).

## Qué se hizo

**Banner:** "ESCENA 2 · *La quijada de asno*", abajo a la **derecha** (Sansón está a la izquierda del escenario). Entra en el segundo 1 y sale en el 8.5.

**Audio:** la mayor parte de la escena ya tenía buen volumen. Se subieron los tramos donde los niños hablan sin micrófono:

| Tramo | Antes | Después | Ganancia |
|---|---|---|---|
| Pelea con los filisteos (19–22 s) | -36.6 | -23.2 | +16 dB (casi todo forcejeo y ruido de sala; más subida solo sube el ruido) |
| Sansón habla solo (34.3–35.5 s) | -39.4 | -19.9 | +28 dB |
| Sansón y la mujer (44.3–45.8 s) | -22.6 | -16.6 | +18 dB |
| Escena completa | -10.0 | -16.0 | |

- Cada tramo lleva limpieza de ruido, corte de graves, ecualización para la voz, puerta de ruido suave y compresión, con fundidos de 60 ms al entrar y salir.
- Se igualaron los canales izquierdo y derecho (el derecho venía 0.8 dB más bajo).
- Todo: compresión suave, limitador y -16 LUFS. El rango de volumen bajó de 9.1 a 6.4 LU.

**Imagen:** igual que la Escena 1 (limpieza de compresión, 1080p, enfoque, más contraste y color).

Los tramos, sus ganancias máximas y el título están al inicio de `editar_escena2.py` (`KIDS`, `LINE2`).

## Volver a generarlo

```bash
python3 editar_escena2.py
```

Usa `../comun_escenas.py` (banner, nivelación final y codificación, compartidos con la Escena 1).
