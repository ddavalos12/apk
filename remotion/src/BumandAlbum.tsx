import {AbsoluteFill, Sequence, useVideoConfig} from 'remotion';
import {BrandBadge} from './components/BrandBadge';
import {ChapterProgress} from './components/ChapterProgress';
import {FlagBadge} from './components/FlagBadge';
import {GradedVideo} from './components/GradedVideo';
import {IntroTitle} from './components/IntroTitle';
import {LightSweep} from './components/LightSweep';
import {LowerThird} from './components/LowerThird';
import {Outro} from './components/Outro';
import {chapters, flagMoments, OUTRO_DURATION, SOURCE_DURATION} from './timeline';

export const BumandAlbum: React.FC = () => {
  const {fps} = useVideoConfig();
  const f = (s: number) => Math.round(s * fps);

  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      <Sequence durationInFrames={f(SOURCE_DURATION)} name="Video con corrección de color">
        <GradedVideo />
        <BrandBadge />
        <ChapterProgress />
      </Sequence>

      <Sequence durationInFrames={f(4)} name="Título de apertura">
        <IntroTitle />
      </Sequence>

      {chapters.map((c, i) => (
        <Sequence key={c.start} from={f(c.start)} durationInFrames={f(c.end - c.start)} name={`Sección: ${c.title}`}>
          <LowerThird index={i} title={c.title} subtitle={c.subtitle} />
          <Sequence durationInFrames={f(1.2)} name="Destello">
            <LightSweep />
          </Sequence>
        </Sequence>
      ))}

      {flagMoments.map((m) => (
        <Sequence key={m.start} from={f(m.start)} durationInFrames={f(m.end - m.start)} name="Bandera de Bolivia">
          <FlagBadge />
        </Sequence>
      ))}

      <Sequence from={f(SOURCE_DURATION)} durationInFrames={f(OUTRO_DURATION)} name="Cierre">
        <Outro />
      </Sequence>
    </AbsoluteFill>
  );
};
