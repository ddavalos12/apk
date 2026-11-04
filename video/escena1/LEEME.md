# Escena 1: "La revelación"

- Original: `original/escena1_original.mp4` (1280x720, 25 fps, 500 kbps).
- Resultado: `escena1_la_revelacion.mp4` (1920x1080, 25 fps, H.264 alta calidad + AAC 256 kbps).

## Qué se hizo

**Banner:** cinta azul con borde dorado, "ESCENA 1 · *La revelación*" abajo a la izquierda. Entra en el segundo 1 y sale en el 8.5, durante la música de entrada.

**Audio** (antes / después, en LUFS):

| Parte | Antes | Después |
|---|---|---|
| Música de entrada (0–13 s) | -10.2 | -16.0 |
| Narrador (14–42 s) | -10.5 | -16.3 |
| **Niños (44–60 s)** | **-30.4** | **-15.4** |
| Narrador (61–76 s) | -10.0 | -16.0 |

- Niños: limpieza de ruido, corte de graves (pasos y retumbe), ecualización para que se entiendan mejor las palabras, puerta de ruido suave, compresión y +30 dB de ganancia.
- Todo el video: compresión suave, limitador y normalización a -16 LUFS (pico máximo -1.5 dBTP). El rango de volumen bajó de 22.7 a 5.6 LU.

**Imagen:** reducción del ruido de compresión, escalado a 1080p (Lanczos), enfoque adaptativo y un poco más de contraste y color.

## Volver a generarlo

```bash
python3 editar_escena1.py
```

Usa las fuentes de `../intro_sanson/assets/fonts`. Requiere Python 3 con `numpy` y `Pillow`, y `ffmpeg`.
