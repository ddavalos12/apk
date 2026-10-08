import React from 'react';
import {Composition} from 'remotion';
import {MiVideo, miVideoSchema} from './MiVideo';
import {FPS} from './album/datos';
import {VideoAlbum, duracionTotal} from './album/VideoAlbum';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AlbumBumand"
        component={VideoAlbum}
        durationInFrames={duracionTotal(FPS)}
        fps={FPS}
        width={1920}
        height={1080}
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
