import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, staticFile, useVideoConfig} from 'remotion';
import {Confeti} from './Confeti';
import {DURACION_VIDEO, FINAL, INTRO, MENSAJES, VIDEO} from './datos';
import {Portada} from './Portada';
import {DURACION_ROTULO, Rotulo} from './Rotulo';

export const duracionTotal = (fps: number) => INTRO + Math.ceil(DURACION_VIDEO * fps) + FINAL;

export const VideoCumple: React.FC = () => {
  const {fps} = useVideoConfig();
  const frames = Math.ceil(DURACION_VIDEO * fps);
  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      <Sequence durationInFrames={INTRO} name="Intro">
        <Portada tipo="intro" />
      </Sequence>

      <Sequence from={INTRO} durationInFrames={frames} name="Vídeo">
        <OffthreadVideo src={staticFile(VIDEO)} />
        {MENSAJES.map((m, i) => (
          <Sequence key={i} from={Math.round(m.inicio * fps)} durationInFrames={Math.round(DURACION_ROTULO * fps)} name={`Mensaje ${i + 1}`}>
            <Confeti semilla={`m${i}`} />
            <Rotulo indice={i} />
          </Sequence>
        ))}
      </Sequence>

      <Sequence from={INTRO + frames} durationInFrames={FINAL} name="Final">
        <Portada tipo="final" />
      </Sequence>
    </AbsoluteFill>
  );
};
