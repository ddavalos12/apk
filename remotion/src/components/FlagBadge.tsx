import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {colors, sans} from '../theme';

const STRIPES = [colors.boliviaRed, colors.boliviaYellow, colors.boliviaGreen];

// Bandera boliviana ondeando cuando aparece en las fotos.
export const FlagBadge: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 14}});
  const exit = interpolate(frame, [durationInFrames - 12, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const t = frame / fps;
  const COLS = 24;

  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div
        style={{
          position: 'absolute',
          top: 70,
          right: 80,
          display: 'flex',
          alignItems: 'center',
          gap: 22,
          padding: '16px 28px 16px 20px',
          background: 'rgba(11,22,64,0.85)',
          borderRadius: 18,
          boxShadow: '0 12px 36px rgba(0,0,0,0.35)',
          opacity: enter * exit,
          transform: `translateY(${(1 - enter) * -60}px)`,
        }}
      >
        <div style={{display: 'flex', width: 132, height: 88}}>
          {new Array(COLS).fill(0).map((_, c) => {
            const wave = Math.sin(t * 5 - c * 0.45) * 5 * (c / COLS);
            const shade = 0.88 + 0.12 * Math.cos(t * 5 - c * 0.45);
            return (
              <div
                key={c}
                style={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  transform: `translateY(${wave}px)`,
                  filter: `brightness(${shade})`,
                }}
              >
                {STRIPES.map((s) => (
                  <div key={s} style={{flex: 1, background: s}} />
                ))}
              </div>
            );
          })}
        </div>
        <div style={{fontFamily: sans, color: colors.cream}}>
          <div style={{fontWeight: 900, fontSize: 38, lineHeight: 1}}>BOLIVIA</div>
          <div style={{fontWeight: 500, fontSize: 24, color: colors.gold, marginTop: 6}}>Orgullo de nuestra tierra</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
