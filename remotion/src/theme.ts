import {continueRender, delayRender} from 'remotion';
import {greatVibes, montserrat500, montserrat700, montserrat900} from './fontData';

// Fuentes embebidas en el proyecto para que el render no dependa de internet.
export const sans = 'Montserrat';
export const script = 'Great Vibes';

const css = [
  [sans, montserrat500, '500'],
  [sans, montserrat700, '700'],
  [sans, montserrat900, '900'],
  [script, greatVibes, '400'],
]
  .map(
    ([family, url, weight]) =>
      `@font-face{font-family:'${family}';src:url(${url}) format('woff2');font-weight:${weight};font-display:block;}`,
  )
  .join('\n');

if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  // Espera a que las fuentes estén listas, pero nunca más de 5 s para no bloquear el render.
  const handle = delayRender('Cargando fuentes');
  Promise.race([
    Promise.all([
      document.fonts.load(`500 20px '${sans}'`),
      document.fonts.load(`700 20px '${sans}'`),
      document.fonts.load(`900 20px '${sans}'`),
      document.fonts.load(`20px '${script}'`),
    ]),
    new Promise((resolve) => setTimeout(resolve, 5000)),
  ]).finally(() => continueRender(handle));
}

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
