// Datos de la edición del álbum de fotos de la Familia Bumand.
// Los tiempos están en segundos dentro de public/album-bumand.mp4.

export const FPS = 30;
export const VIDEO = 'album-bumand.mp4';
export const DURACION_VIDEO = 172.2; // segundos
export const GRUPO = 'Familia Bumand';

export const INTRO = Math.round(3.5 * FPS); // frames
export const FINAL = 5 * FPS; // frames

// El distintivo de la esquina (que tapa la marca de agua) se muestra hasta que aparece el logo.
export const FIN_DISTINTIVO = 159.7;

export type Capitulo = {inicio: number; titulo: string; subtitulo: string};

// Cada capítulo muestra un rótulo al empezar. Cambia los textos libremente.
export const CAPITULOS: Capitulo[] = [
  {inicio: 0.6, titulo: '¡Bienvenidos!', subtitulo: 'Así empezó todo'},
  {inicio: 12.5, titulo: 'Nuestras reuniones', subtitulo: 'Aprendiendo juntos'},
  {inicio: 37.7, titulo: 'Un gran equipo', subtitulo: 'Cada rostro cuenta'},
  {inicio: 60, titulo: 'Salidas y aventuras', subtitulo: 'Recuerdos al aire libre'},
  {inicio: 90.5, titulo: 'Días de fiesta', subtitulo: 'Celebrar también es servir'},
  {inicio: 110, titulo: 'Compartiendo', subtitulo: 'Testimonios y enseñanzas'},
  {inicio: 139.5, titulo: 'Unidos como familia', subtitulo: 'Con orgullo boliviano'},
];

export const DORADO = '#f2c14e';
export const VINO = '#6b1d2f';
export const CREMA = '#fff6e0';
export const BOLIVIA = ['#d52b1e', '#f9e300', '#007934'];
