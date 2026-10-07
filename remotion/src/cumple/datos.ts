// Datos de la edición del vídeo de cumpleaños.
// Los tiempos (en segundos) marcan dónde empieza y acaba cada mensaje en public/video-subir.mp4.
// Para mostrar quién habla en cada mensaje, rellena "nombre".

export const FPS = 30;
export const VIDEO = 'video-subir.mp4';
export const DURACION_VIDEO = 506.5; // segundos
export const CUMPLEANERO = 'Oscar';

export const INTRO = 4 * FPS; // frames
export const FINAL = 6 * FPS; // frames

export type Mensaje = {inicio: number; fin: number; nombre: string};

export const MENSAJES: Mensaje[] = [
  {inicio: 37.2, fin: 64.5, nombre: ''},
  {inicio: 64.5, fin: 116.8, nombre: ''},
  {inicio: 116.8, fin: 137.7, nombre: ''},
  {inicio: 137.7, fin: 184.5, nombre: ''},
  {inicio: 184.5, fin: 204.9, nombre: ''},
  {inicio: 204.9, fin: 235.0, nombre: ''},
  {inicio: 235.0, fin: 266.8, nombre: ''},
  {inicio: 266.8, fin: 308.3, nombre: ''},
  {inicio: 308.3, fin: 320.8, nombre: ''},
  {inicio: 320.8, fin: 358.3, nombre: ''},
  {inicio: 358.3, fin: 394.5, nombre: ''},
  {inicio: 394.5, fin: 415.4, nombre: ''},
  {inicio: 415.4, fin: 463.8, nombre: ''},
];

// Frases que acompañan a cada mensaje cuando no hay nombre.
export const FRASES = [
  '¡Feliz cumpleaños!',
  'Con mucho cariño',
  '¡Que cumplas muchos más!',
  'Un abrazo enorme',
  '¡A celebrar!',
  'Te queremos mucho',
  '¡Que se cumplan tus deseos!',
];

export const COLORES = ['#ff4d6d', '#ffd23f', '#3ec1d3', '#8e7dff', '#06d6a0', '#ff8c42'];
