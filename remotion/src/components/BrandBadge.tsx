import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {colors, sans, script} from '../theme';
import {WATERMARK_END} from '../timeline';

// Sello de BumanD en la esquina inferior derecha (tapa la marca de agua del editor original).
export const BrandBadge: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const opacity = interpolate(t, [0.6, 1.2, WATERMARK_END - 0.3, WATERMARK_END + 0.2], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const shine = ((t * 0.35) % 1) * 160 - 30;

  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div
        style={{
          position: 'absolute',
          right: 52,
          bottom: 44,
          width: 420,
          height: 108,
          borderRadius: 54,
          opacity,
          overflow: 'hidden',
          background: `linear-gradient(120deg, ${colors.navy} 0%, ${colors.blue} 100%)`,
          border: `3px solid ${colors.gold}`,
          boxShadow: '0 10px 30px rgba(0,0,0,0.4)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 16,
        }}
      >
        <div style={{fontFamily: sans, fontWeight: 900, fontSize: 44, color: colors.cream}}>
          Buman<span style={{color: colors.orange}}>D</span>
        </div>
        <div style={{fontFamily: script, fontSize: 40, color: colors.gold}}>álbum</div>
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: `linear-gradient(100deg, transparent ${shine}%, rgba(255,255,255,0.25) ${shine + 8}%, transparent ${shine + 16}%)`,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
