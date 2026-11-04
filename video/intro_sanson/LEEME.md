# Intro "Sansón y Dalila"

Intro horizontal de 59 s para la Escuela Dominical de la Iglesia Evangélica Metodista "Monte de Horeb".

- Resultado: `../intro_sanson_dalila.mp4` (1920x1080, 30 fps, H.264 + AAC 44.1 kHz, igual que `video_comprimido.mp4`, así se pueden unir sin volver a codificar).
- Música original generada por el script (sin derechos de autor), normalizada a -16 LUFS.
- Fuentes: Cinzel y Cormorant Garamond (licencia SIL Open Font License).

## Guion

| Tiempo | Escena | Texto |
|---|---|---|
| 0–6 s | Fachada de la iglesia | Iglesia Evangélica Metodista · *Monte de Horeb* |
| 6–11 s | Letrero de la Escuela Dominical | Escuela Dominical presenta… |
| 11–17 s | Letras SANSON | La historia de SANSÓN *y Dalila* (Jueces 13–16) |
| 17–22 s | Escenario | Apartado como nazareo de Dios (Jue 13:5) |
| 22–27 s | Puerta con las letras | Pero Sansón amó a Dalila… (Jue 16:4-5) |
| 27–32 s | Escenario | Tanto le insistió… (Jue 16:16-17) |
| 32–43 s | Versículo | Jueces 16:17 (Reina-Valera 1960) |
| 43–48 s | Letras SANSON (pierden el color) | Le raparon… su fuerza se apartó de él (Jue 16:19) |
| 48–54 s | Escenario con rayos de luz | «Acuérdate ahora de mí, y fortaléceme…» (Jue 16:28) |
| 54–59 s | Fachada de la iglesia | *Nuestra fuerza viene de Dios* |

## Volver a generarlo

Los textos y tiempos están en `generar_intro.py` (`SCENES` y `build_texts`).

```bash
python3 generar_intro.py
```

Requiere Python 3 con `numpy` y `Pillow`, y `ffmpeg`. Tarda unos 3–4 minutos.
