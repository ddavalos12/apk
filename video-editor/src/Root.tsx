import { Composition } from "remotion";
import { Principal, principalSchema } from "./Principal";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Principal"
      component={Principal}
      durationInFrames={150}
      fps={30}
      width={1920}
      height={1080}
      schema={principalSchema}
      defaultProps={{
        titulo: "¡Hola desde Remotion!",
        subtitulo: "Vídeo generado automáticamente",
        colorFondo: "#0b1d3a",
        colorTexto: "#ffffff",
        video: "",
      }}
    />
  );
};
