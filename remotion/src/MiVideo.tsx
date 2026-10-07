import React from 'react';
import {z} from 'zod';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

export const miVideoSchema = z.object({
  titulo: z.string(),
  subtitulo: z.string(),
  colorFondo: z.string(),
  colorTexto: z.string(),
});

export const MiVideo: React.FC<z.infer<typeof miVideoSchema>> = ({
  titulo,
  subtitulo,
  colorFondo,
  colorTexto,
}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();

  const entrada = spring({frame, fps, config: {damping: 200}});
  const opacidadSub = interpolate(frame, [20, 45], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const salida = interpolate(
    frame,
    [durationInFrames - 20, durationInFrames],
    [1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colorFondo,
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: 'sans-serif',
        color: colorTexto,
        opacity: salida,
      }}
    >
      <h1
        style={{
          fontSize: 110,
          margin: 0,
          transform: `scale(${entrada}) translateY(${(1 - entrada) * 80}px)`,
        }}
      >
        {titulo}
      </h1>
      <p style={{fontSize: 48, opacity: opacidadSub, marginTop: 24}}>
        {subtitulo}
      </p>
    </AbsoluteFill>
  );
};
