import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {colors} from '../theme';
import {chapters, SOURCE_DURATION} from '../timeline';

const WIDTH = 1920 - 140;

// Línea de tiempo animada con un punto por cada sección del álbum.
export const ChapterProgress: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const progress = Math.min(t / SOURCE_DURATION, 1);
  const opacity = interpolate(t, [1, 2, SOURCE_DURATION - 1, SOURCE_DURATION], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{pointerEvents: 'none', opacity}}>
      <div style={{position: 'absolute', left: 70, bottom: 30, width: WIDTH, height: 6}}>
        <div style={{position: 'absolute', inset: 0, borderRadius: 3, background: 'rgba(11,22,64,0.18)'}} />
        <div
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            bottom: 0,
            width: WIDTH * progress,
            borderRadius: 3,
            background: `linear-gradient(90deg, ${colors.orange}, ${colors.gold})`,
            boxShadow: `0 0 12px ${colors.gold}`,
          }}
        />
        {chapters.map((c) => {
          const reached = t >= c.start;
          const pop = interpolate(t, [c.start, c.start + 0.3, c.start + 0.6], [1, 1.8, 1.25], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          return (
            <div
              key={c.start}
              style={{
                position: 'absolute',
                left: WIDTH * (c.start / SOURCE_DURATION) - 8,
                top: -5,
                width: 16,
                height: 16,
                borderRadius: '50%',
                background: reached ? colors.gold : 'rgba(255,255,255,0.6)',
                border: `2px solid ${colors.navy}`,
                transform: `scale(${reached ? pop : 1})`,
              }}
            />
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
