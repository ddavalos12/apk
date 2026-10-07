import React from 'react';
import {AbsoluteFill, random, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORES} from './datos';

// Explosión de confeti que cae desde arriba. Determinista: misma semilla = mismo confeti.
export const Confeti: React.FC<{semilla: string; piezas?: number}> = ({semilla, piezas = 90}) => {
  const frame = useCurrentFrame();
  const {width, height, fps} = useVideoConfig();
  const t = frame / fps;

  return (
    <AbsoluteFill style={{pointerEvents: 'none', overflow: 'hidden'}}>
      {new Array(piezas).fill(0).map((_, i) => {
        const r = (k: string) => random(`${semilla}-${i}-${k}`);
        const x0 = r('x') * width;
        const vx = (r('vx') - 0.5) * 500;
        const vy = -300 - r('vy') * 900;
        const g = 1400;
        const x = x0 + vx * t + Math.sin(t * 6 + i) * 30;
        const y = -40 + (r('y') * 200 - 100) + vy * t * 0.15 + 0.5 * g * t * t * (0.35 + r('g') * 0.3);
        if (y > height + 50) return null;
        const w = 14 + r('w') * 16;
        const forma = r('forma');
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x,
              top: y,
              width: w,
              height: forma < 0.3 ? w : w * 0.45,
              borderRadius: forma < 0.3 ? '50%' : 3,
              background: COLORES[Math.floor(r('c') * COLORES.length)],
              transform: `rotate(${t * 360 * (r('rot') - 0.5) * 3}deg) rotateX(${t * 540 * r('rx')}deg)`,
              opacity: Math.min(1, 3 - t),
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
