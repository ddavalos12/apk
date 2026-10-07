import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

// Fuentes guardadas en public/fuentes para que el render funcione sin conexión.
export const PACIFICO = 'Pacifico';
export const POPPINS = 'Poppins';

loadFont({family: PACIFICO, url: staticFile('fuentes/Pacifico-Regular.woff2'), weight: '400'});
loadFont({family: POPPINS, url: staticFile('fuentes/Poppins-SemiBold.woff2'), weight: '600'});
loadFont({family: POPPINS, url: staticFile('fuentes/Poppins-ExtraBold.woff2'), weight: '800'});
