# Escena 5: "El templo de Dagón"

Los filisteos celebran en el templo y traen a Sansón encadenado para burlarse de él. Sansón ora, se apoya en las columnas y derriba el templo (Jueces 16:23-30).

- Original: `original/escena5_original.mp4` (1280x720, 30 fps, 1.4 Mbps, 104 s).
- Resultado: `escena5_el_templo_de_dagon.mp4` (1920x1080, 30 fps, H.264 CRF 20 + AAC 256 kbps, 92 MB).

## Qué se hizo

**Banner:** "ESCENA 5 · *El templo de Dagón*", abajo a la derecha y un poco más bajo que en las otras escenas, para tapar solo pies y piso. Del segundo 1 al 8.5.

**Audio:**

| Tramo | Antes | Después |
|---|---|---|
| Traen a Sansón (34–36.7 s) | -27.6 | -17.8 (+18 dB) |
| Segunda cámara (43.3–56.1 s), venía más fuerte | -7.4 | -16.3 (se emparejó con el resto) |
| Se burlan de Sansón (61–69.4 s) | -14.8 | -16.5 (+8 dB) |
| Escena completa | -10.1 | -16.0 |

**Efectos de sonido del derrumbe** (sintetizados por el programa, sin derechos de autor), alineados cuadro por cuadro:

| Momento | Efecto |
|---|---|
| 95.8 s, Sansón se apoya en las columnas | empieza un retumbe de terremoto que crece hasta la caída |
| 96.6 → 98.55 s, mientras empuja | seis crujidos de piedra, cada vez más seguidos y fuertes |
| 98.6 s, la primera columna se inclina | silbido de los bloques cayendo |
| 99.1 s, los bloques golpean el piso | estruendo (golpe grave y ruido de impacto), con golpes secundarios en 99.3, 99.6, 100.0 y 100.45 s |
| 99.15 → 102.6 s | escombros que siguen cayendo y polvo, cada vez menos |

- El audio original de ese momento (gritos de los niños) ya era muy fuerte, así que se baja 3 dB mientras Sansón empuja y 7 dB durante la caída: el derrumbe se oye encima sin tapar a los niños. El golpe principal queda unos 6 dB por encima de lo que lo rodea.
- Todo: compresión suave, limitador y -16 LUFS (rango de 8.9 a 3.1 LU).

**Imagen:** igual que las otras escenas, con CRF 20 para que el archivo quede debajo de los 100 MB de GitHub.

Los tiempos de los efectos y sus niveles están al inicio de `editar_escena5.py` (`T_GRIP`, `CRACKS`, `T_FALL`, `IMPACTS`, `DUCK`).

## Volver a generarlo

```bash
python3 editar_escena5.py
```

Usa `../comun_escenas.py`.
