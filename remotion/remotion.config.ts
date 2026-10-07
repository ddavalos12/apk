import {Config} from '@remotion/cli/config';

// El video original vive en ../video, así no se duplica en el repositorio.
Config.setPublicDir('../video');
Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
