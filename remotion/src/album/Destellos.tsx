import React from 'react';
import {AbsoluteFill, random, useCurrentFrame, useVideoConfig} from 'remotion';

// Destellos dorados que brotan desde un punto y se desvanecen.
export const Destellos: React.FC<{semilla: string; x: number; y: number; cantidad?: number}> = ({semilla, x, y, cantidad = 40}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {new Array(cantidad).fill(0).map((_, i) => {
        const r = (k: string) => random(`${semilla}-${i}-${k}`);
        const ang = r('a') * Math.PI * 2;
        const vel = 120 + r('v') * 380;
        const vida = 0.8 + r('l') * 1.2;
        const p = t / vida;
        if (p >= 1) return null;
        const tam = 6 + r('t') * 14;
        const dist = vel * t * (1 - p * 0.5);
        return (
          <svg
            key={i}
            width={tam * 2}
            height={tam * 2}
            viewBox="-10 -10 20 20"
            style={{
              position: 'absolute',
              left: x + Math.cos(ang) * dist - tam,
              top: y + Math.sin(ang) * dist - tam + 60 * t * t,
              opacity: 1 - p,
              transform: `rotate(${t * 180 * (r('r') - 0.5)}deg) scale(${1 - p * 0.4})`,
            }}
          >
            <path d="M0 -10 L2 -2 L10 0 L2 2 L0 10 L-2 2 L-10 0 L-2 -2 Z" fill={r('c') < 0.7 ? '#ffd76a' : '#fff6e0'} />
          </svg>
        );
      })}
    </AbsoluteFill>
  );
};
