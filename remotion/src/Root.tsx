import {Composition} from 'remotion';
import {BumandAlbum} from './BumandAlbum';
import {FPS, TOTAL_DURATION} from './timeline';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="BumandAlbum"
      component={BumandAlbum}
      durationInFrames={Math.round(TOTAL_DURATION * FPS)}
      fps={FPS}
      width={1920}
      height={1080}
    />
  );
};
