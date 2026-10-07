import {AbsoluteFill, random, useCurrentFrame, useVideoConfig} from 'remotion';
import {colors} from '../theme';

const COUNT = 22;

// Partículas doradas flotando, en sintonía con los destellos del fondo original.
export const Particles: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;

  return (
    <AbsoluteFill style={{pointerEvents: 'none', mixBlendMode: 'screen'}}>
      {new Array(COUNT).fill(0).map((_, i) => {
        const x0 = random(`x${i}`) * 1920;
        const speed = 12 + random(`s${i}`) * 30;
        const size = 3 + random(`r${i}`) * 7;
        const phase = random(`p${i}`) * 1080;
        const y = 1100 - ((phase + t * speed) % 1180);
        const x = x0 + Math.sin(t * 0.6 + i) * 25;
        const twinkle = 0.35 + 0.65 * Math.abs(Math.sin(t * (0.8 + random(`w${i}`)) + i));
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x,
              top: y,
              width: size,
              height: size,
              borderRadius: '50%',
              background: colors.gold,
              opacity: 0.4 * twinkle,
              boxShadow: `0 0 ${size * 3}px ${size}px rgba(242,193,78,0.45)`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
