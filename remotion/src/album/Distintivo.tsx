import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {BOLIVIA, CAPITULOS, CREMA, DORADO, GRUPO, VINO} from './datos';
import {POPPINS} from './fuentes';

// Distintivo fijo en la esquina inferior derecha: nombre del grupo y progreso por capítulos.
// Está colocado justo encima de la marca de agua del vídeo original.
export const Distintivo: React.FC<{fin: number}> = ({fin}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const opacidad = interpolate(frame, [0, 12, fin - 12, fin], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const actual = CAPITULOS.reduce((acc, c, i) => (t >= c.inicio ? i : acc), 0);

  return (
    <div
      style={{
        position: 'absolute',
        right: 50,
        bottom: 52,
        width: 440,
        height: 124,
        borderRadius: 20,
        background: `linear-gradient(135deg, ${VINO}, #3d0f1b)`,
        border: `3px solid ${DORADO}`,
        boxShadow: '0 12px 30px rgba(0,0,0,0.45)',
        opacity: opacidad,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        padding: '0 26px',
        fontFamily: POPPINS,
      }}
    >
      <div style={{display: 'flex', alignItems: 'center', gap: 14}}>
        <div style={{display: 'flex', flexDirection: 'column', width: 34, height: 24, borderRadius: 4, overflow: 'hidden'}}>
          {BOLIVIA.map((c) => (
            <div key={c} style={{flex: 1, background: c}} />
          ))}
        </div>
        <div style={{color: CREMA, fontWeight: 800, fontSize: 36, letterSpacing: 1}}>{GRUPO}</div>
      </div>
      <div style={{display: 'flex', gap: 8, marginTop: 12}}>
        {CAPITULOS.map((_, i) => (
          <div
            key={i}
            style={{
              flex: 1,
              height: 8,
              borderRadius: 4,
              background: i < actual ? DORADO : i === actual ? CREMA : 'rgba(255,246,224,0.25)',
            }}
          />
        ))}
      </div>
    </div>
  );
};
