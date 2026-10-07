import {AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {colors, sans, script} from '../theme';

const LETTERS = 'BUMAND'.split('');

// Título de apertura sobre el destello blanco inicial del video.
export const IntroTitle: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();

  const fadeOut = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const veil = interpolate(frame, [0, 10], [0, 0.82], {extrapolateRight: 'clamp'});
  const lineWidth = interpolate(frame, [18, 45], [0, 520], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const scriptIn = spring({frame: frame - 28, fps, config: {damping: 14}});

  return (
    <AbsoluteFill style={{opacity: fadeOut, alignItems: 'center', justifyContent: 'center'}}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at center, rgba(30,63,191,${veil}) 0%, rgba(11,22,64,${veil}) 70%)`,
        }}
      />
      <div style={{display: 'flex', gap: 10, position: 'relative'}}>
        {LETTERS.map((l, i) => {
          const s = spring({frame: frame - 4 - i * 3, fps, config: {damping: 12, mass: 0.6}});
          return (
            <span
              key={i}
              style={{
                fontFamily: sans,
                fontWeight: 900,
                fontSize: 190,
                letterSpacing: 6,
                color: i === LETTERS.length - 1 ? colors.orange : colors.cream,
                transform: `translateY(${(1 - s) * 80}px) scale(${0.6 + 0.4 * s})`,
                opacity: s,
                textShadow: '0 10px 40px rgba(0,0,0,0.45)',
              }}
            >
              {l}
            </span>
          );
        })}
      </div>
      <div style={{height: 6, width: lineWidth, background: colors.orange, borderRadius: 3, marginTop: 6}} />
      <div
        style={{
          fontFamily: script,
          fontSize: 92,
          color: colors.gold,
          marginTop: 10,
          opacity: scriptIn,
          transform: `translateY(${(1 - scriptIn) * 30}px)`,
          textShadow: '0 6px 24px rgba(0,0,0,0.5)',
        }}
      >
        Álbum de fotos
      </div>
    </AbsoluteFill>
  );
};
