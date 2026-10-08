import {AbsoluteFill, Easing, interpolate, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {SOURCE_DURATION, VERTICAL_START} from '../timeline';

const src = staticFile('video_fondo_nuevo.mp4');

// Corrección de color suave: el fondo ya viene reemplazado (ver scripts/cambiar_fondo.py).
const GRADE = 'brightness(1.02) contrast(1.06) saturate(1.08)';

// Ancho del contenido vertical (9:16) dentro del cuadro 1920x1080.
const VERTICAL_WIDTH = 608;

export const GradedVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;

  // Baja la música suavemente en los últimos 2 segundos.
  const volume = (f: number) =>
    interpolate(f / fps, [SOURCE_DURATION - 2, SOURCE_DURATION], [1, 0], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    });

  const vertical = t >= VERTICAL_START;
  // Fundido de la versión con fondo desenfocado al entrar al tramo vertical.
  const verticalOpacity = interpolate(t, [VERTICAL_START, VERTICAL_START + 0.6], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      <OffthreadVideo src={src} volume={volume} style={{width: '100%', height: '100%', filter: GRADE}} />
      {vertical ? (
        <AbsoluteFill style={{opacity: verticalOpacity}}>
          {/* Relleno de las barras negras con una copia ampliada y desenfocada */}
          <AbsoluteFill style={{overflow: 'hidden'}}>
            <OffthreadVideo
              src={src}
              muted
              style={{
                position: 'absolute',
                width: 1920 * (1920 / VERTICAL_WIDTH),
                height: 1080 * (1920 / VERTICAL_WIDTH),
                left: -((1920 - VERTICAL_WIDTH) / 2) * (1920 / VERTICAL_WIDTH),
                top: -(1080 * (1920 / VERTICAL_WIDTH) - 1080) / 2,
                filter: `blur(40px) brightness(0.55) saturate(1.3)`,
              }}
            />
          </AbsoluteFill>
          <div
            style={{
              position: 'absolute',
              left: (1920 - VERTICAL_WIDTH) / 2,
              top: 0,
              width: VERTICAL_WIDTH,
              height: 1080,
              overflow: 'hidden',
              boxShadow: '0 0 80px rgba(0,0,0,0.6)',
            }}
          >
            <OffthreadVideo
              src={src}
              muted
              style={{
                position: 'absolute',
                width: 1920,
                height: 1080,
                left: -(1920 - VERTICAL_WIDTH) / 2,
                filter: GRADE,
              }}
            />
          </div>
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};
