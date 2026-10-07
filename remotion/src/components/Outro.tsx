import {AbsoluteFill, interpolate, random, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {colors, sans, script} from '../theme';

const VALUES = [
  {label: 'AMOR', color: colors.orange},
  {label: 'LEALTAD', color: colors.blue},
  {label: 'SACRIFICIO', color: colors.cream},
];

// Tarjeta final con el nombre del grupo y sus valores.
export const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const t = frame / fps;

  const fadeIn = interpolate(frame, [0, 12], [0, 1], {extrapolateRight: 'clamp'});
  const fadeOut = interpolate(frame, [durationInFrames - 18, durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const logo = spring({frame: frame - 6, fps, config: {damping: 12}});
  const thanks = spring({frame: frame - 26, fps, config: {damping: 16}});

  return (
    <AbsoluteFill
      style={{
        opacity: fadeIn * fadeOut,
        background: `radial-gradient(ellipse at 50% 40%, ${colors.blue} 0%, ${colors.navy} 75%)`,
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
      }}
    >
      {/* Anillos de luz que se expanden desde el centro */}
      {[0, 1, 2].map((i) => {
        const p = ((t + i * 0.9) % 2.7) / 2.7;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              width: 300 + p * 1500,
              height: 300 + p * 1500,
              borderRadius: '50%',
              border: `3px solid rgba(242,193,78,${0.5 * (1 - p)})`,
            }}
          />
        );
      })}
      {new Array(30).fill(0).map((_, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: random(`ox${i}`) * 1920,
            top: (random(`oy${i}`) * 1080 - t * (20 + random(`os${i}`) * 40) + 1080) % 1080,
            width: 6,
            height: 6,
            borderRadius: '50%',
            background: colors.gold,
            opacity: 0.6,
            boxShadow: `0 0 14px 4px rgba(242,193,78,0.5)`,
          }}
        />
      ))}
      <div
        style={{
          fontFamily: sans,
          fontWeight: 900,
          fontSize: 200,
          color: colors.cream,
          letterSpacing: 4,
          transform: `scale(${0.7 + 0.3 * logo})`,
          opacity: logo,
          textShadow: '0 14px 50px rgba(0,0,0,0.5)',
        }}
      >
        Buman<span style={{color: colors.orange}}>D</span>
      </div>
      <div
        style={{
          fontFamily: script,
          fontSize: 86,
          color: colors.gold,
          opacity: thanks,
          transform: `translateY(${(1 - thanks) * 30}px)`,
          marginTop: -10,
        }}
      >
        Gracias por cada momento
      </div>
      <div style={{display: 'flex', gap: 26, marginTop: 50}}>
        {VALUES.map((v, i) => {
          const s = spring({frame: frame - 44 - i * 8, fps, config: {damping: 14}});
          return (
            <div
              key={v.label}
              style={{
                fontFamily: sans,
                fontWeight: 900,
                fontSize: 34,
                letterSpacing: 3,
                padding: '14px 34px',
                borderRadius: 12,
                background: v.color,
                color: v.color === colors.cream ? colors.navy : 'white',
                opacity: s,
                transform: `translateY(${(1 - s) * 40}px)`,
                boxShadow: '0 10px 30px rgba(0,0,0,0.35)',
              }}
            >
              {v.label}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
