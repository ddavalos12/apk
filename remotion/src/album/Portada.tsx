import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {BOLIVIA, CREMA, DORADO, GRUPO, VINO} from './datos';
import {Destellos} from './Destellos';
import {PACIFICO, POPPINS} from './fuentes';

const Polaroid: React.FC<{rot: number; x: number; y: number; s: number; color: string}> = ({rot, x, y, s, color}) => (
  <div
    style={{
      position: 'absolute',
      left: x,
      top: y,
      width: 210,
      height: 250,
      transformOrigin: 'center',
      background: CREMA,
      padding: '16px 16px 54px',
      boxShadow: '0 20px 40px rgba(0,0,0,0.45)',
      transform: `rotate(${rot}deg) scale(${s})`,
    }}
  >
    <div style={{width: '100%', height: '100%', background: `linear-gradient(160deg, ${color}, #2a0a13)`}} />
  </div>
);

// Tarjeta de inicio o de cierre del álbum.
export const Portada: React.FC<{tipo: 'intro' | 'final'}> = ({tipo}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const s = (d: number) => spring({frame: frame - d, fps, config: {damping: 13}});
  const fundido = interpolate(frame, [0, 10, durationInFrames - 12, durationInFrames], [0, 1, 1, tipo === 'intro' ? 0 : 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at 50% 45%, #8a2b40 0%, ${VINO} 45%, #240711 100%)`,
        justifyContent: 'center',
        alignItems: 'center',
        textAlign: 'center',
        opacity: fundido,
      }}
    >
      <Polaroid rot={-12} x={70} y={50} s={s(0)} color="#c98b3a" />
      <Polaroid rot={8} x={90} y={740} s={s(4)} color="#7a5bd1" />
      <Polaroid rot={11} x={1610} y={50} s={s(2)} color="#2f8f6b" />
      <Polaroid rot={-9} x={1600} y={740} s={s(6)} color="#c0392b" />
      <div style={{position: 'relative'}}>
        <div style={{fontFamily: PACIFICO, fontSize: 110, color: DORADO, transform: `scale(${s(6)})`, textShadow: '0 8px 24px rgba(0,0,0,0.5)'}}>
          {tipo === 'intro' ? 'Álbum de fotos' : 'Gracias por cada momento'}
        </div>
        <div
          style={{
            fontFamily: POPPINS,
            fontWeight: 800,
            fontSize: 120,
            color: CREMA,
            letterSpacing: 8,
            lineHeight: 1.1,
            opacity: s(14),
            transform: `translateY(${(1 - s(14)) * 120}px)`,
          }}
        >
          {GRUPO.toUpperCase()}
        </div>
        <div style={{display: 'flex', justifyContent: 'center', marginTop: 26, transform: `scaleX(${s(22)})`}}>
          {BOLIVIA.map((c) => (
            <div key={c} style={{width: 120, height: 12, background: c}} />
          ))}
        </div>
        {tipo === 'final' && (
          <div style={{fontFamily: POPPINS, fontWeight: 600, fontSize: 40, color: CREMA, marginTop: 30, opacity: s(30)}}>
            Lo mejor está por venir
          </div>
        )}
      </div>
      <Destellos semilla={`portada-${tipo}`} x={960} y={470} cantidad={90} />
    </AbsoluteFill>
  );
};
