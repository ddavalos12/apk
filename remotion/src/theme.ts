import {continueRender, delayRender} from 'remotion';
import greatVibes from './fonts/GreatVibes.woff2';
import montserrat500 from './fonts/Montserrat-500.woff2';
import montserrat700 from './fonts/Montserrat-700.woff2';
import montserrat900 from './fonts/Montserrat-900.woff2';

// Fuentes incluidas en el proyecto para que el render no dependa de internet.
export const sans = 'Montserrat';
export const script = 'Great Vibes';

const faces = [
  new FontFace(sans, `url(${montserrat500}) format('woff2')`, {weight: '500'}),
  new FontFace(sans, `url(${montserrat700}) format('woff2')`, {weight: '700'}),
  new FontFace(sans, `url(${montserrat900}) format('woff2')`, {weight: '900'}),
  new FontFace(script, `url(${greatVibes}) format('woff2')`),
];
const handle = delayRender('Cargando fuentes');
Promise.all(faces.map((f) => f.load()))
  .then((loaded) => {
    loaded.forEach((f) => document.fonts.add(f));
    continueRender(handle);
  })
  .catch((err) => {
    console.error(err);
    continueRender(handle);
  });

// Colores tomados de las tarjetas finales del video (AMOR / LEALTAD) y de la bandera.
export const colors = {
  orange: '#E4621B',
  blue: '#1E3FBF',
  navy: '#0B1640',
  gold: '#F2C14E',
  cream: '#FFF6E5',
  boliviaRed: '#D52B1E',
  boliviaYellow: '#F9E300',
  boliviaGreen: '#007934',
};
