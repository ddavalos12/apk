import React from 'react';
import {AbsoluteFill, random, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORES} from './datos';

const Globo: React.FC<{color: string; tam: number}> = ({color, tam}) => (
  <svg width={tam} height={tam * 1.9} viewBox="0 0 100 190">
    <path d="M50 120 Q45 150 55 165 Q62 178 50 190" stroke="rgba(255,255,255,0.8)" strokeWidth="2" fill="none" />
    <ellipse cx="50" cy="58" rx="44" ry="56" fill={color} />
    <ellipse cx="34" cy="36" rx="9" ry="16" fill="rgba(255,255,255,0.45)" transform="rotate(-25 34 36)" />
    <path d="M44 112 L56 112 L50 122 Z" fill={color} />
  </svg>
);

// Globos que suben desde abajo, balanceándose.
export const Globos: React.FC<{cantidad?: number; semilla?: string}> = ({cantidad = 9, semilla = 'g'}) => {
  const frame = useCurrentFrame();
  const {width, height, fps} = useVideoConfig();
  const t = frame / fps;
  return (
    <AbsoluteFill style={{pointerEvents: 'none', overflow: 'hidden'}}>
      {new Array(cantidad).fill(0).map((_, i) => {
        const r = (k: string) => random(`${semilla}-${i}-${k}`);
        const tam = 110 + r('t') * 90;
        const vel = 260 + r('v') * 220;
        const x = r('x') * (width - tam) + Math.sin(t * 1.5 + i) * 25;
        const y = height + r('d') * 500 - vel * t;
        return (
          <div key={i} style={{position: 'absolute', left: x, top: y, transform: `rotate(${Math.sin(t * 2 + i) * 6}deg)`}}>
            <Globo color={COLORES[i % COLORES.length]} tam={tam} />
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
