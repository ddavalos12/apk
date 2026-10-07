import {loadFont} from '@remotion/fonts';
import greatVibes from './fonts/GreatVibes.woff2';
import montserrat500 from './fonts/Montserrat-500.woff2';
import montserrat700 from './fonts/Montserrat-700.woff2';
import montserrat900 from './fonts/Montserrat-900.woff2';

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
