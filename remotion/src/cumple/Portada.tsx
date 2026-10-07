import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {CUMPLEANERO, MENSAJES} from './datos';
import {PACIFICO, POPPINS} from './fuentes';
import {Confeti} from './Confeti';
import {Globos} from './Globos';

const Tarta: React.FC = () => (
  <svg width={300} height={260} viewBox="0 0 300 260">
    <rect x="40" y="130" width="220" height="110" rx="18" fill="#ff8fab" />
    <path d="M40 150 Q67 180 95 150 Q122 180 150 150 Q177 180 205 150 Q232 180 260 150 L260 140 L40 140 Z" fill="#fff" />
    <rect x="20" y="232" width="260" height="18" rx="9" fill="#ffd166" />
    {[90, 150, 210].map((x, i) => (
      <g key={i}>
        <rect x={x - 8} y="80" width="16" height="55" rx="4" fill={['#3ec1d3', '#8e7dff', '#06d6a0'][i]} />
        <path d={`M${x} 52 C${x + 9} 64 ${x + 9} 76 ${x} 79 C${x - 9} 76 ${x - 9} 64 ${x} 52 Z`} fill="#ffd166" />
      </g>
    ))}
  </svg>
);

// Tarjeta animada para el principio ("intro") o el final del vídeo.
export const Portada: React.FC<{tipo: 'intro' | 'final'}> = ({tipo}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const s = (delay: number) => spring({frame: frame - delay, fps, config: {damping: 12}});
  const fundido = interpolate(frame, [0, 10, durationInFrames - 12, durationInFrames], [0, 1, 1, tipo === 'intro' ? 0 : 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        background: 'radial-gradient(circle at 50% 35%, #6a3fd1 0%, #2b1055 60%, #12062b 100%)',
        justifyContent: 'center',
        alignItems: 'center',
        textAlign: 'center',
        color: 'white',
        opacity: fundido,
      }}
    >
      <Globos semilla={tipo} cantidad={10} />
      <div style={{position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      <div style={{transform: `scale(${s(0)})`}}>
        <Tarta />
      </div>
      <div style={{fontFamily: PACIFICO, fontSize: 120, color: '#ffd166', marginTop: 20, transform: `scale(${s(8)})`, textShadow: '0 8px 30px rgba(0,0,0,0.4)'}}>
        {tipo === 'intro' ? 'Feliz cumpleaños' : '¡Felicidades!'}
      </div>
      <div style={{fontFamily: POPPINS, fontWeight: 800, fontSize: 190, letterSpacing: 10, lineHeight: 1, transform: `translateY(${(1 - s(16)) * 300}px)`, opacity: s(16)}}>
        {CUMPLEANERO.toUpperCase()}
      </div>
      <div style={{fontFamily: POPPINS, fontWeight: 600, fontSize: 52, marginTop: 50, opacity: s(28), maxWidth: 900}}>
        {tipo === 'intro' ? `${MENSAJES.length} mensajes de quienes te quieren` : 'Con mucho cariño, de todos nosotros'}
      </div>
      </div>
      <Confeti semilla={`portada-${tipo}`} piezas={140} />
    </AbsoluteFill>
  );
};
