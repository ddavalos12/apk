import React from 'react';
import {interpolate, random, useCurrentFrame} from 'remotion';
import {COLORES, MENSAJES} from './datos';

// Una vela por mensaje: se van encendiendo a medida que avanzan los mensajes.
export const Velas: React.FC<{actual: number}> = ({actual}) => {
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        display: 'flex',
        gap: 22,
        alignItems: 'flex-end',
        padding: '18px 34px 16px',
        background: 'rgba(20, 10, 40, 0.55)',
        borderRadius: 40,
        backdropFilter: 'blur(6px)',
      }}
    >
      {MENSAJES.map((_, i) => {
        const encendida = i <= actual;
        const esActual = i === actual;
        const parpadeo = 1 + Math.sin(frame / 3 + i) * 0.08 + random(`p${i}-${Math.floor(frame / 4)}`) * 0.06;
        const aparicion = esActual ? interpolate(frame, [8, 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 1;
        return (
          <svg key={i} width={40} height={esActual ? 96 : 80} viewBox="0 0 40 96">
            {encendida && (
              <g transform={`translate(20 26) scale(${parpadeo * aparicion * (esActual ? 1.25 : 1)}) translate(-20 -26)`}>
                <ellipse cx="20" cy="22" rx="10" ry="18" fill="#ffb703" opacity={0.35} />
                <path d="M20 4 C28 16 28 30 20 34 C12 30 12 16 20 4 Z" fill="#ffd166" />
                <path d="M20 16 C24 22 24 30 20 32 C16 30 16 22 20 16 Z" fill="#fff3c4" />
              </g>
            )}
            <line x1="20" y1="34" x2="20" y2="42" stroke="#333" strokeWidth="2" />
            <rect x="8" y="42" width="24" height="54" rx="5" fill={encendida ? COLORES[i % COLORES.length] : 'rgba(255,255,255,0.35)'} />
            <path d="M8 56 L32 50 M8 72 L32 66 M8 88 L32 82" stroke="rgba(255,255,255,0.55)" strokeWidth="4" />
          </svg>
        );
      })}
    </div>
  );
};
