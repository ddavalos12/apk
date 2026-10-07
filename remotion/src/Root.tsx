import React from 'react';
import {Composition} from 'remotion';
import {MiVideo, miVideoSchema} from './MiVideo';
import {FPS} from './cumple/datos';
import {VideoCumple, duracionTotal} from './cumple/VideoCumple';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="CumpleOscar"
        component={VideoCumple}
        durationInFrames={duracionTotal(FPS)}
        fps={FPS}
        width={1080}
        height={1920}
      />
      <Composition
        id="MiVideo"
        component={MiVideo}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        schema={miVideoSchema}
        defaultProps={{
          titulo: '¡Hola desde Remotion!',
          subtitulo: 'Vídeos generados con código',
          colorFondo: '#0b1020',
          colorTexto: '#ffffff',
        }}
      />
    </>
  );
};
