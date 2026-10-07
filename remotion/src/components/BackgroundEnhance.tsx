import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {VERTICAL_START} from '../timeline';

// Realza el fondo de pergamino: aclara el centro, oscurece los bordes y da un tono cálido.
export const BackgroundEnhance: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const strength = interpolate(t, [VERTICAL_START - 0.5, VERTICAL_START + 0.5], [1, 0.4], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  // Respiración muy lenta de la luz para que el fondo no se vea plano.
  const breathe = 0.9 + 0.1 * Math.sin(t * 0.8);

  return (
    <AbsoluteFill style={{pointerEvents: 'none', opacity: strength}}>
      <AbsoluteFill
        style={{
          mixBlendMode: 'soft-light',
          background: `radial-gradient(ellipse 60% 55% at 50% 48%, rgba(255,240,210,${0.55 * breathe}) 0%, rgba(255,220,170,0.15) 55%, rgba(0,0,0,0) 75%)`,
        }}
      />
      <AbsoluteFill
        style={{
          mixBlendMode: 'multiply',
          background:
            'radial-gradient(ellipse 85% 80% at 50% 50%, rgba(0,0,0,0) 55%, rgba(20,10,40,0.45) 100%)',
        }}
      />
      <AbsoluteFill
        style={{
          mixBlendMode: 'overlay',
          background: 'linear-gradient(180deg, rgba(30,63,191,0.10) 0%, rgba(0,0,0,0) 40%, rgba(228,98,27,0.10) 100%)',
        }}
      />
    </AbsoluteFill>
  );
};
