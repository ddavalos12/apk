import { z } from "zod";
import {
  AbsoluteFill,
  OffthreadVideo,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export const principalSchema = z.object({
  titulo: z.string(),
  subtitulo: z.string(),
  colorFondo: z.string(),
  colorTexto: z.string(),
  // Nombre de un vídeo dentro de /public (p. ej. "clip.mp4"). Vacío = sin vídeo de fondo.
  video: z.string(),
});

type Props = z.infer<typeof principalSchema>;

export const Principal: React.FC<Props> = ({
  titulo,
  subtitulo,
  colorFondo,
  colorTexto,
  video,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const entrada = spring({ frame, fps, config: { damping: 200 } });
  const subOpacidad = interpolate(frame, [20, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const salida = interpolate(
    frame,
    [durationInFrames - 15, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <AbsoluteFill style={{ backgroundColor: colorFondo, opacity: salida }}>
      {video ? (
        <OffthreadVideo
          src={staticFile(video)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      ) : null}
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          fontFamily: "Helvetica, Arial, sans-serif",
          color: colorTexto,
          textAlign: "center",
        }}
      >
        <h1
          style={{
            fontSize: 120,
            margin: 0,
            transform: `translateY(${(1 - entrada) * 80}px)`,
            opacity: entrada,
            textShadow: "0 4px 20px rgba(0,0,0,0.5)",
          }}
        >
          {titulo}
        </h1>
        <p style={{ fontSize: 56, opacity: subOpacidad, marginTop: 24 }}>
          {subtitulo}
        </p>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
