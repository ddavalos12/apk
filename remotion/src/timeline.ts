export const FPS = 30;

// Duración del video original (video_comprimido.mp4).
export const SOURCE_DURATION = 172.27;
// Tarjeta final añadida después del video.
export const OUTRO_DURATION = 5;
export const TOTAL_DURATION = SOURCE_DURATION + OUTRO_DURATION;

// A partir de aquí el video original pasa a formato vertical con barras negras.
export const VERTICAL_START = 158.4;
// Marca de agua "descript" (esquina inferior derecha) visible hasta este segundo.
export const WATERMARK_END = 158.6;

export type Chapter = {
  start: number;
  end: number;
  title: string;
  subtitle: string;
};

// Secciones del álbum, identificadas revisando el video cuadro a cuadro.
export const chapters: Chapter[] = [
  {start: 4.2, end: 13.5, title: '¡Bienvenidos!', subtitle: 'El inicio de una gran familia'},
  {start: 15.5, end: 46.5, title: 'Nuestras reuniones', subtitle: 'Aprendiendo y creciendo juntos'},
  {start: 48, end: 63, title: 'Familia BumanD', subtitle: 'Cada rostro, una historia'},
  {start: 64, end: 87.5, title: 'Momentos que unen', subtitle: 'Actividades, juegos y amistad'},
  {start: 93.5, end: 111, title: 'Rescatados', subtitle: 'Un evento para recordar'},
  {start: 112, end: 136.5, title: 'Compartiendo el mensaje', subtitle: 'Voces que inspiran'},
  {start: 137.5, end: 150.5, title: 'Juntos en el camino', subtitle: 'Unidos por un mismo propósito'},
];

// Momentos donde aparece la bandera de Bolivia en las fotos.
export const flagMoments = [
  {start: 88, end: 91.6},
  {start: 150.8, end: 154.6},
];
