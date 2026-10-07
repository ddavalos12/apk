import {AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';

// Destello de luz que cruza la pantalla al empezar cada sección.
export const LightSweep: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const x = interpolate(frame, [0, durationInFrames], [-60, 160], {
    easing: Easing.inOut(Easing.cubic),
  });
  const opacity = interpolate(frame, [0, 6, durationInFrames - 6, durationInFrames], [0, 1, 1, 0]);

  return (
    <AbsoluteFill
      style={{
        pointerEvents: 'none',
        mixBlendMode: 'screen',
        opacity,
        background: `linear-gradient(105deg, transparent ${x - 25}%, rgba(255,214,140,0.35) ${x - 8}%, rgba(255,255,255,0.45) ${x}%, rgba(255,214,140,0.35) ${x + 8}%, transparent ${x + 25}%)`,
      }}
    />
  );
};
