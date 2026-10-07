import React from 'react';
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLORES, FRASES, MENSAJES} from './datos';
import {POPPINS} from './fuentes';
import {Velas} from './Velas';

export const DURACION_ROTULO = 5.5; // segundos

// Rótulo que aparece al inicio de cada mensaje: velas arriba y tarjeta abajo.
export const Rotulo: React.FC<{indice: number}> = ({indice}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const total = DURACION_ROTULO * fps;
  const entrada = spring({frame, fps, config: {damping: 14, stiffness: 120}});
  const salida = interpolate(frame, [total - 15, total], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const {nombre} = MENSAJES[indice];
  const color = COLORES[indice % COLORES.length];
  const texto = nombre ? `De: ${nombre}` : FRASES[indice % FRASES.length];

  return (
    <AbsoluteFill style={{fontFamily: POPPINS, opacity: salida}}>
      <div style={{position: 'absolute', top: 70, width: '100%', display: 'flex', justifyContent: 'center', transform: `translateY(${(1 - entrada) * -220}px)`}}>
        <Velas actual={indice} />
      </div>
      <div
        style={{
          position: 'absolute',
          bottom: 230,
          left: 70,
          transform: `translateX(${(1 - entrada) * -900}px) rotate(-2deg)`,
        }}
      >
        <div
          style={{
            display: 'inline-block',
            background: color,
            color: '#1b1033',
            fontWeight: 800,
            fontSize: 34,
            letterSpacing: 2,
            padding: '8px 22px',
            borderRadius: '14px 14px 0 0',
            textTransform: 'uppercase',
          }}
        >
          Mensaje {indice + 1} de {MENSAJES.length}
        </div>
        <div
          style={{
            background: 'rgba(255,255,255,0.95)',
            color: '#1b1033',
            fontWeight: 800,
            fontSize: 64,
            padding: '18px 36px',
            borderRadius: '0 22px 22px 22px',
            borderLeft: `14px solid ${color}`,
            boxShadow: '0 16px 40px rgba(0,0,0,0.35)',
            maxWidth: 860,
          }}
        >
          {texto}
        </div>
      </div>
    </AbsoluteFill>
  );
};
