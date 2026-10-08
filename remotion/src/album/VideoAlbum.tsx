import React from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, staticFile, useVideoConfig} from 'remotion';
import {Capitulo, DURACION_CAPITULO} from './Capitulo';
import {CAPITULOS, DURACION_VIDEO, FINAL, FIN_DISTINTIVO, INTRO, VIDEO} from './datos';
import {Distintivo} from './Distintivo';
import {Portada} from './Portada';

export const duracionTotal = (fps: number) => INTRO + Math.ceil(DURACION_VIDEO * fps) + FINAL;

export const VideoAlbum: React.FC = () => {
  const {fps} = useVideoConfig();
  const frames = Math.ceil(DURACION_VIDEO * fps);
  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      <Sequence durationInFrames={INTRO} name="Intro">
        <Portada tipo="intro" />
      </Sequence>

      <Sequence from={INTRO} durationInFrames={frames} name="Álbum">
        <OffthreadVideo src={staticFile(VIDEO)} />
        <Sequence durationInFrames={Math.round(FIN_DISTINTIVO * fps)} name="Distintivo">
          <Distintivo fin={Math.round(FIN_DISTINTIVO * fps)} />
        </Sequence>
        {CAPITULOS.map((c, i) => (
          <Sequence key={i} from={Math.round(c.inicio * fps)} durationInFrames={Math.round(DURACION_CAPITULO * fps)} name={c.titulo}>
            <Capitulo indice={i} />
          </Sequence>
        ))}
      </Sequence>

      <Sequence from={INTRO + frames} durationInFrames={FINAL} name="Final">
        <Portada tipo="final" />
      </Sequence>
    </AbsoluteFill>
  );
};
