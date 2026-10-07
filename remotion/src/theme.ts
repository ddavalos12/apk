import {loadFont} from '@remotion/fonts';
import {greatVibes, montserrat500, montserrat700, montserrat900} from './fontData';

// Fuentes incluidas en el proyecto para que el render no dependa de internet.
export const sans = 'Montserrat';
export const script = 'Great Vibes';

loadFont({family: sans, url: montserrat500, weight: '500', format: 'woff2'});
loadFont({family: sans, url: montserrat700, weight: '700', format: 'woff2'});
loadFont({family: sans, url: montserrat900, weight: '900', format: 'woff2'});
loadFont({family: script, url: greatVibes, format: 'woff2'});

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
