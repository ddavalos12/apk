import {AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {colors, sans, script} from '../theme';

type Props = {
  index: number;
  title: string;
  subtitle: string;
};

// Rótulo animado de cada sección del álbum (abajo a la izquierda).
export const LowerThird: React.FC<Props> = ({index, title, subtitle}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();

  const enter = spring({frame, fps, config: {damping: 16, stiffness: 120}});
  const exit = interpolate(frame, [durationInFrames - 14, durationInFrames], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.in(Easing.cubic),
  });
  const reveal = interpolate(frame, [6, 26], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const subIn = spring({frame: frame - 14, fps, config: {damping: 18}});
  const accent = index % 2 === 0 ? colors.orange : colors.blue;

  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div
        style={{
          position: 'absolute',
          left: 70,
          bottom: 95,
          transform: `translateX(${(1 - enter) * -120 - exit * 160}px)`,
          opacity: enter * (1 - exit),
          display: 'flex',
          alignItems: 'stretch',
        }}
      >
        <div
          style={{
            width: 74,
            background: accent,
            borderRadius: '14px 0 0 14px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: sans,
            fontWeight: 900,
            fontSize: 34,
            color: 'white',
          }}
        >
          {String(index + 1).padStart(2, '0')}
        </div>
        <div
          style={{
            background: 'linear-gradient(90deg, rgba(11,22,64,0.92), rgba(11,22,64,0.78))',
            padding: '16px 34px 14px 26px',
            borderRadius: '0 14px 14px 0',
            border: '2px solid rgba(242,193,78,0.55)',
            borderLeft: 'none',
            backdropFilter: 'blur(6px)',
            boxShadow: '0 14px 40px rgba(0,0,0,0.35)',
            clipPath: `inset(0 ${100 - reveal}% 0 0)`,
          }}
        >
          <div
            style={{
              fontFamily: sans,
              fontWeight: 900,
              fontSize: 54,
              color: colors.cream,
              letterSpacing: 1,
              textTransform: 'uppercase',
              lineHeight: 1.05,
            }}
          >
            {title}
          </div>
          <div
            style={{
              fontFamily: script,
              fontSize: 44,
              color: colors.gold,
              marginTop: 2,
              opacity: subIn,
              transform: `translateY(${(1 - subIn) * 12}px)`,
            }}
          >
            {subtitle}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
