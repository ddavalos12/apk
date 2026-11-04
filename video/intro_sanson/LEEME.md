# Intro "Sansón y Dalila"

Intro horizontal de 60 s para la Escuela Dominical de la Iglesia Evangélica Metodista "Monte de Horeb".

- Resultado: `../intro_sanson_dalila.mp4` (1920x1080, 30 fps, H.264 + AAC 44.1 kHz, igual que `video_comprimido.mp4`, así se pueden unir sin volver a codificar).
- Audio: canción "Con Fuerza de Dios - Alabanza de Sansón" (`assets/audio/`), editada a 60 s y normalizada a -16 LUFS.
- Fuentes: Cinzel y Cormorant Garamond (licencia SIL Open Font License).

## Guion

| Tiempo | Escena | Texto | Música |
|---|---|---|---|
| 0–7 s | Fachada de la iglesia | Iglesia Evangélica Metodista · *Monte de Horeb* | intro con golpes |
| 7–12 s | Letrero de la Escuela Dominical | Escuela Dominical presenta… | golpe de la intro en el cambio |
| 12–17 s | Letras SANSON | La historia de SANSÓN *y Dalila* (Jueces 13–16) | "y Dalila" sale con la subida (13.6 s) |
| 17–22 s | Escenario | Apartado como nazareo de Dios (Jue 13:5) | |
| 22–27 s | Puerta con las letras | Pero Sansón amó a Dalila… (Jue 16:4-5) | |
| 27–32 s | Escenario | Tanto le insistió… (Jue 16:16-17) | entra toda la banda |
| 32–44 s | Versículo | Jueces 16:17 (Reina-Valera 1960) | |
| 44–49 s | Letras SANSON (pierden el color) | Le raparon… su fuerza se apartó de él (Jue 16:19) | se va el bajo (45.9 s) |
| 49–56 s | Escenario con rayos + **póster** | «Acuérdate ahora de mí, y fortaléceme…» (Jue 16:28) | entra el coro final (48.8 s) |
| 56–60 s | Fachada de la iglesia | *Nuestra fuerza viene de Dios* | golpe final (57.2 s) |

## Cómo se editó la canción

La canción va a 143 BPM. Se usan tres tramos y cada salto es un número entero de compases, así el ritmo no se interrumpe. Los cortes están en pausas de la voz:

1. 0:00–0:44 de la canción (intro y primera estrofa)
2. 2:33–2:44 (pausa sin bajo y coro final)
3. 3:24–3:29 (nota larga y golpe final)

Los tramos y los tiempos de las escenas están en `generar_intro.py` (`AUDIO_EDITS` y `SCENES`).

## Volver a generarlo

```bash
python3 generar_intro.py
```

Requiere Python 3 con `numpy` y `Pillow`, y `ffmpeg`. Tarda unos 3–4 minutos.
