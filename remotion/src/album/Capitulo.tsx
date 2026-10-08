import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {CAPITULOS, CREMA, DORADO, VINO} from './datos';
import {Destellos} from './Destellos';
import {PACIFICO, POPPINS} from './fuentes';

export const DURACION_CAPITULO = 4.5; // segundos

// Rótulo de capítulo: cinta con número, título y subtítulo, que entra desde la izquierda.
export const Capitulo: React.FC<{indice: number}> = ({indice}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const total = DURACION_CAPITULO * fps;
  const entrada = spring({frame, fps, config: {damping: 15, stiffness: 110}});
  const sub = spring({frame: frame - 10, fps, config: {damping: 200}});
  const linea = interpolate(frame, [12, 34], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const salida = interpolate(frame, [total - 14, total], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const {titulo, subtitulo} = CAPITULOS[indice];

  return (
    <AbsoluteFill style={{opacity: salida}}>
      <div style={{position: 'absolute', left: 70, top: 64, transform: `translateX(${(1 - entrada) * -800}px)`}}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 26,
            background: `linear-gradient(90deg, ${VINO} 0%, rgba(107,29,47,0.92) 100%)`,
            padding: '20px 44px 22px 22px',
            borderRadius: 18,
            border: `3px solid ${DORADO}`,
            boxShadow: '0 18px 40px rgba(0,0,0,0.45)',
          }}
        >
          <div
            style={{
              width: 96,
              height: 96,
              borderRadius: '50%',
              background: DORADO,
              color: VINO,
              fontFamily: POPPINS,
              fontWeight: 800,
              fontSize: 50,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transform: `rotate(${(1 - entrada) * -180}deg)`,
            }}
          >
            {indice + 1}
          </div>
          <div>
            <div style={{fontFamily: PACIFICO, fontSize: 64, color: CREMA, lineHeight: 1.15}}>{titulo}</div>
            <div style={{height: 4, width: `${linea * 100}%`, background: DORADO, borderRadius: 2, margin: '6px 0 8px'}} />
            <div style={{fontFamily: POPPINS, fontWeight: 600, fontSize: 30, color: DORADO, letterSpacing: 1, opacity: sub}}>{subtitulo}</div>
          </div>
        </div>
      </div>
      <Destellos semilla={`cap${indice}`} x={130} y={150} />
    </AbsoluteFill>
  );
};
